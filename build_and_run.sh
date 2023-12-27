# build the docker container and run the container
docker build -t pipeline-ecom-industry-descriptions .
docker run -e PLACEHOLDER='' pipeline-ecom-industry-descriptions