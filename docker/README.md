# Notes on building and running the docker image for ISP Monitor

To build, run the following command from the PARENT folder. I.e. the one above this docker folder.

docker build -t ispmonitor -f docker/Dockerfile .

docker buildx build --platform linux/amd64,linux/arm64 --push -t simonsecuritypedant/ispmonitor:1.4 -f docker/Dockerfile .