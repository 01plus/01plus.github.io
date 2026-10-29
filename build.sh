#!/bin/sh
# Builds every page served by GitHub Pages. See build.py.
cd "$(dirname "$0")" && python3 -I build.py
