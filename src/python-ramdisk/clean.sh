#!/bin/bash

/usr/bin/find . -iname "*.pyc" -print -exec rm {} \;
/usr/bin/find . -iname "__pycache__" -print -exec rm -rf {} \;


