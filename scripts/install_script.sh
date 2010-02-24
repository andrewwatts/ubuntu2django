#!/usr/bin/env bash

mkdir /home/%(user)s/virtualenvs
virtualenv /home/%(user)s/virtualenvs/%(site)s
source /home/%(user)s/virtualenvs/%(site)s/bin/activate
easy_install pip
pip install flup
pip install django
django-admin.py startproject %(site)s
