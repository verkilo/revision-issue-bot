#!/bin/bash

cd revision-recorder
python3 setup.py bdist_wheel
pip3 install dist/*
cd ..