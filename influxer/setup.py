from setuptools import setup

setup(
    name="influxer2",
    version="0.0.1",

    packages=["influxer2", ],
    install_requires=["gevent==1.0.2", "influxdb==2.8.0", ],

    author="Vince Forgione",
    author_email="vforgione@theonion.com",
    description="A simple, fast uwsgi/gevent application to record pageview data to InfluxDB",
    license="MIT",
    keywords=["uwsgi gevent influxdb pageview"],
    url="https://github.com/theonion/influxer2",
)
