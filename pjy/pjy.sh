#!/bin/bash

nohup /root/bgProjects/fliggy-mobile-control/venv/bin/python3 /root/bgProjects/fliggy-mobile-control/pjy/pjy.py > /root/bgProjects/fliggy-mobile-control/pjy/pjy.log 2>&1 &
nohup /root/bgProjects/fliggy-mobile-control/venv/bin/python3 /root/bgProjects/fliggy-mobile-control/pjy/pjy_1.py > /root/bgProjects/fliggy-mobile-control/pjy/pjy_1.log 2>&1 &
