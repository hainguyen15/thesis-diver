FROM node:10.15.3

ENV PATH=/usr/src/app/node_modules/.bin:$PATH

RUN apt-get install nginx
RUN rm /etc/nginx/conf.d/default.conf

COPY ./nginx/prod.conf /etc/nginx/conf.d
COPY . /usr/src/app

WORKDIR /usr/src/app/web

RUN npm install -g bower
RUN bower install

CMD [ "nginx", "-g", "daemon off;" ]
