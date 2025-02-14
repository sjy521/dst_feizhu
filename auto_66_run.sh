#!/bin/bash


nohup /root/bgProjects/fliggy-mobile-control/venv/bin/python3 /root/bgProjects/fliggy-mobile-control/auto_run/auto_66_run.py > /root/bgProjects/fliggy-mobile-control/logs/auto_66_run.log 2>&1 &
nohup /root/bgProjects/fliggy-mobile-control/venv/bin/python3 /root/bgProjects/fliggy-mobile-control/auto_run/auto_66_run_java.py > /root/bgProjects/fliggy-mobile-control/logs/auto_66_run_java.log 2>&1 &
