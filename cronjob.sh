#!/bin/bash
cd /home/lukas/Documents/code_to_run/Google-Scholar

git fetch
git pull
uv sync
#uv run scrape.py
uv run plotting.py
git add .
git commit . -m 'Ran the code'
git push

