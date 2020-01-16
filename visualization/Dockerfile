FROM python:3.6

WORKDIR /usr/src/app
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT [ "gunicorn", "-b 0.0.0.0:5000", "wsgi:app" ]