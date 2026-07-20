#!/bin/bash
# Daily: scrape Google Scholar citation counts, regenerate plots, publish both.
#
# Data (CSVs) is committed to master with normal history.
# Plots are NOT committed to master -- see .gitignore. Every plot changes every day
# because its date axis grows, so committing 56 PNGs daily grew .git to 2.8 GB in
# 7 months. Instead the plots directory is published to the orphan `plots` branch as a
# single *parentless* commit that is force-pushed, so plot history never accumulates.
#
# Runs from cron with no TTY; see /etc/cron.d/ScholarCitations (which sets PATH).
set -uo pipefail

cd /home/lukas/Documents/code_to_run/Google-Scholar || exit 1

git fetch origin
git checkout master
git pull --ff-only origin master || exit 1

uv sync
uv run scrape.py || exit 1
uv run plotting.py || exit 1

# --- data -> master (normal history) ---
git add citations_history.csv citations_wide_format.csv
if ! git diff --cached --quiet; then
    git commit -m "Citation data $(date -I)"
    git push origin master
else
    echo "INFO: no data change; nothing to commit to master"
fi

# --- plots -> orphan `plots-latest` branch (single parentless commit, force-pushed) ---
# plots/ is gitignored, so -f is required to stage it. Build a tree rooted at the
# plots directory, wrap it in a commit with no parent, then reset the index back.
# The branch is deliberately NOT called `plots`: that would collide with the plots/
# directory and make every `git log plots` style command ambiguous.
git add -f plots
TREE=$(git write-tree --prefix=plots)
COMMIT=$(git commit-tree "$TREE" -m "Plots $(date -I)")
git reset -q                      # unstage; leaves working tree untouched
git update-ref refs/heads/plots-latest "$COMMIT"
git push -f origin plots-latest

echo "INFO: done"
