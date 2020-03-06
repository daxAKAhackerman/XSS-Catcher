FROM alpine:latest

RUN apk add --update npm apache2 libapache2-mod-wsgi-py3 python3 python3-mysqldb python3-pip

COPY ./server /var/www/html/server
RUN python3 -m pip install -r /var/www/html/server/requirements.txt

COPY ./client /var/www/html/client
WORKDIR /var/www/html/client
RUN npm install
RUN npm run build

COPY ./vhost.conf /etc/apache2/sites-available/000-default.conf

RUN echo 'Listen 8080' >> /etc/apache2/ports.conf
RUN echo 'Listen 8081' >> /etc/apache2/ports.conf

RUN a2enmod headers
RUN a2enmod proxy
RUN a2enmod proxy_http
RUN a2enmod proxy_http2

RUN sed -i 's/Indexes //g' /etc/apache2/apache2.conf
RUN sed -i 's/ServerTokens OS/ServerTokens Prod/g' /etc/apache2/conf-enabled/security.conf
RUN sed -i 's/ServerSignature On/ServerSignature Off/g' /etc/apache2/conf-enabled/security.conf

EXPOSE 80

CMD  /usr/sbin/apache2ctl -D FOREGROUND
