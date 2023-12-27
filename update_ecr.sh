#!/bin/bash

aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 329870157973.dkr.ecr.eu-central-1.amazonaws.com/pipeline-ecom-industry-descriptions

echo "Building docker image"
docker build -t "329870157973.dkr.ecr.eu-central-1.amazonaws.com/pipeline-ecom-industry-descriptions" .

echo "Pushing docker image"
docker push "329870157973.dkr.ecr.eu-central-1.amazonaws.com/pipeline-ecom-industry-descriptions"