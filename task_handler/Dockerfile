# FROM python:3.6
FROM pytorch/pytorch:1.3-cuda10.1-cudnn7-runtime
WORKDIR /usr/src/app

COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT [ "gunicorn", "-b 0.0.0.0:5001", "wsgi:app" ]
