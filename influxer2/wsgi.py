#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
from collections import Counter
import logging
import os

import gevent
from gevent import queue
from influxdb.client import InfluxDBClient

try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs


# build the response gif
gif = base64.b64decode("R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==")

# init influxdb client
host = os.environ.get("INFLUXER_INFLUXDB_HOST_IP", "localhost")
port = os.environ.get("INFLUXER_INFLUXDB_PORT", 8086)
user = os.environ.get("INFLUXER_INFLUXDB_USERNAME", "root")
pwd = os.environ.get("INFLUXER_INFLUXDB_PASSWORD", "root")
db = os.environ.get("INFLUXER_INFLUXDB_DB", "influxdb")
influx_client = InfluxDBClient(host, port, user, pwd, db)

# init the gevent queue
events_queue = queue.Queue()
flush_interval = os.environ.get("INFLUXER_FLUSH_INTERVAL", 60)  # seconds

# acceptable site names
site_names = ("onion", "avclub", "clickhole", "onionstudios", "onionads", )

# init the logger
logger = logging.getLogger('influxer')
logger.setLevel(logging.INFO)


# main wait loop
def count_events():
    """pulls data from the queue, tabulates it and spawns a send event
    """
    # wait loop
    while 1:
        # sleep and let the queue build up
        gevent.sleep(flush_interval)

        # init the data points containers
        page_views = Counter()
        content_views = Counter()

        # flush the queue
        while 1:
            try:
                site, content_id, event, path = events_queue.get_nowait()
                if site not in site_names:
                    continue
                if site and content_id:
                    content_views[(site, content_id)] += 1
                    if event and path:
                        page_views[(site, content_id, event, path)] += 1
            except queue.Empty:
                break
            except Exception as e:
                logger.exception(e)
                break

        # after tabulating, spawn a new thread to send the data to influxdb
        if len(page_views):
            gevent.spawn(write_page_views, page_views)

        if len(content_views):
            gevent.spawn(write_content_views, content_views)


# create the wait loop
gevent.spawn(count_events)


# write operations
def write_page_views(page_views):
    payloads = {}
    for (site, content_id, event, path), count in page_views.items():
        payloads.setdefault(site, [])
        payloads[site].append([content_id, event, path, count])

    for site, points in payloads.items():
        body = []
        for (content_id, event, path, count) in points:
            body.append({
                "measurement": site,
                "tags": {
                    "content_id": content_id,
                    "event": event,
                    "path": path
                },
                "fields": {
                    "value": count,
                }
            })
        try:
            influx_client.write_points(body)
        except Exception as e:
            logger.exception(e)


def write_content_views(content_views):
    payloads = {}
    top = sorted(
        [(key, count) for key, count in content_views.items()],
        key=lambda x: x[1],
        reverse=True
    )

    for (site, content_id), count in top:
        try:
            int(content_id)
        except ValueError:
            continue

        payloads.setdefault(site, [])
        payloads[site].append((content_id, count))

    for site, points in payloads.items():
        name = "{}_trending".format(site)
        body = []
        for (content_id, count) in points:
            body.append({
                "measurement": name,
                "tags": {
                    "content_id": content_id,
                },
                "fields": {
                    "value": count,
                }
            })
        try:
            influx_client.write_points(body)
        except Exception as e:
            logger.exception(e)


# main applications
def application(env, start_response):
    """wsgi application
    """
    path = env["PATH_INFO"]

    if path == "/influx.gif":
        # send response
        start_response("200 OK", [("Content-Type", "image/gif")])
        yield gif
        # parse the query params and stick them in the queue
        params = parse_qs(env["QUERY_STRING"])
        try:
            site = params.get("site", [""])[0]
            content_id = params.get("content_id", [""])[0]
            event = params.get("event", [""])[0]
            path = params.get("path", [""])[0]
            events_queue.put((site, content_id, event, path))
        except Exception as e:
            logger.exception(e)

    else:
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        yield "Nothing Here"
