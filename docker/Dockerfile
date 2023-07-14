# Build a docker image for ISPMonitor

FROM python:3

#############################################
###   Install required networking tools   ###
#############################################

RUN apt-get update
RUN apt-get -y install traceroute iputils-ping net-tools nano curl
RUN curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash
RUN apt-get -y install speedtest
RUN speedtest --servers --accept-license

#############################################
###    Setup required python libraries    ###
#############################################
WORKDIR /usr/src/app

COPY ../python/requirements.txt .
RUN pip install -r requirements.txt

#############################################
###  Copy over python flask source files  ###
#############################################
COPY ../python/*.py .
COPY ../python/config.yaml ./config.yaml
COPY ../python/templates ./templates
COPY ../python/static ./static
COPY ../python/lib ./lib

RUN mkdir logs events graphdata

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=8000"]