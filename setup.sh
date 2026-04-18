#!/usr/bin/env bash

set -e

CONFIG=${1:-links.yaml}

parse_yaml() {
    python3 - <<EOF
import yaml, os
data = yaml.safe_load(open("$CONFIG"))
for x in data["links"]:
    print(x["target"], x["link"])
EOF
}

parse_yaml | while read target link; do
    link="${link/#\~/$HOME}"

    echo "Link: $link -> $target"

    if [ -e "$link" ]; then
        echo "  skip (exists)"
        continue
    fi

    ln -s "$(pwd)/$target" "$link"
done