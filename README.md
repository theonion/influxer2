# influxer2

A simple, fast uwsgi/gevent application to record pageview data to InfluxDB

## running the dev environment

__Requirements:__

1. the latest [ansible-roles](https://github.com/theonion/ansible-roles) along side this repo
2. vagrant and virtual box installed
3. `ansible` globally installed 

Assuming you have the reqs, all you need to do is `vagrant up` the repo. 

The provisioning will take a while, since Influx will only run on system start, so the provisioning process 
reboots the VM and waits (takes up to 5 minutes some times).
