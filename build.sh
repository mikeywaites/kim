#!/usr/bin/env
set -e


docker build -f ./Dockerfile.py2 --tag mikeywaites/kim:2 .
docker build -f ./Dockerfile.py3 --tag mikeywaites/kim:3 .

docker push mikeywaites/kim
