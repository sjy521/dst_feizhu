#!/bin/bash

nohup /root/bgProjects/fliggy-mobile-control/venv/bin/python3 /root/bgProjects/fliggy-mobile-control/orderstatic.py > /root/bgProjects/fliggy-mobile-control/logs/orderstatic.log 2>&1 &
nohup /root/bgProjects/fliggy-mobile-control/venv/bin/python3 /root/bgProjects/fliggy-mobile-control/proxy_monitor.py > /root/bgProjects/fliggy-mobile-control/logs/proxy_monitor.log 2>&1 &
