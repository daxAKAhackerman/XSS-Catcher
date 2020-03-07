FROM alpine:latest

RUN echo http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories  
RUN apk add --update npm apache2 python3 py3-pip py3-pymysql apache2-mod-wsgi apache2-proxy apache2-proxy-html libxml2-dev

COPY ./server /var/www/html/server
WORKDIR /var/www/html/server
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r /var/www/html/server/requirements.txt
RUN python3 -m flask db init
RUN python3 -m flask db migrate -m "Initial migration."
RUN python3 -m flask db upgrade
RUN chown -R apache:www-data /var/www/html/server

COPY ./client /var/www/html/client
WORKDIR /var/www/html/client
RUN npm install
RUN npm audit fix
RUN npm run build
RUN chown -R apache:www-data /var/www/html/client

COPY ./vhost.conf /etc/apache2/conf.d/vhost.conf

RUN sed -i 's/ServerTokens OS/ServerTokens Prod/g' /etc/apache2/httpd.conf
RUN sed -i 's/ServerSignature On/ServerSignature Off/g' /etc/apache2/httpd.conf

EXPOSE 80

CMD /usr/sbin/httpd -D FOREGROUND
