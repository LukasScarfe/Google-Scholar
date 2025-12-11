#!/bin/bash
uv sync
#uv run scrape.py
uv run plotting.py
git add .
git commit . -m 'Ran the code'
git push
git fetch
git pull
