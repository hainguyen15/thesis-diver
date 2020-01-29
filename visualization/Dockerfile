FROM python:3.6

WORKDIR /usr/src/app
COPY . .

RUN apt-get update 
RUN apt-get install openslide-tools -y
RUN apt-get install python3-openslide -y

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /usr/diver/projects

ENV PROJECT_BASE_DIR /usr/diver/projects
ENV FLASK_ENV production

EXPOSE 5000

ENTRYPOINT [ "gunicorn", "-b 0.0.0.0:5000" , "wsgi:app" ]