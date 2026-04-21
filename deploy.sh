#!/bin/bash
set -e

cd "$(dirname "$0")"

git pull

(
  cd src/site
  npm install
  npm run build
)

sudo docker compose up -d --build

sudo docker image prune -f
