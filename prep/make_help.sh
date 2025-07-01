#!/bin/bash
grep -E '^[a-zA-Z_-]+:.*?## .*$$' "$1" |
  sort |
  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $1, $2}'
