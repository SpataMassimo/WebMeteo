FROM selenium/standalone-chrome:101.0
ENV PATH /usr/src/app/bin:$PATH
WORKDIR /usr/src/app

COPY requirements.txt ./
USER root
RUN apt-get update && apt-get install python3-pip -y &&\
    pip install --no-cache-dir -r requirements.txt
