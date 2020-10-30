#!/bin/bash

eval waitress-serve --port=8080 --call 'run:getApp'
