#!/bin/bash
i=0;while [ $i -le $1 ]; do (( i++ )); python web.py & done