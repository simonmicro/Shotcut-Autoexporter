#!/bin/bash

eval waitress-serve --max-request-body-size=8589934592 --port=8080 --call 'run:getApp'
