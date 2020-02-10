FROM pytorch/pytorch:1.3-cuda10.1-cudnn7-runtime
WORKDIR /usr/src/app

COPY . .
RUN apt-get update && \ 
    apt-get install --no-install-recommends libsm6 libxext6 \
    libxrender-dev openslide-tools -y 

# RUN apt-get install python3-openslide -y
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN mkdir -p /usr/diver/projects
RUN mkdir /usr/diver/model/

ENV PROJECT_BASE_DIR=/usr/diver/projects
ENV FLASK_ENV=production
