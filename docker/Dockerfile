# Build the frontend
FROM node:16.18-alpine3.15 as build

COPY ./client /build
COPY ./collector_script /collector_script
WORKDIR /collector_script
RUN npm ci
RUN npx webpack -o /build/public/static
WORKDIR /build
RUN npm ci
RUN npm run build

# Switch to main image
FROM ubuntu:22.04

# Install dependencies
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y software-properties-common python3 python3-launchpadlib gnupg curl postgresql-client nginx supervisor postgresql
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.10
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.10
RUN apt-get clean && apt-get autoremove --purge && rm -rf /var/lib/apt/lists/*

# Setup supervisor
RUN mkdir -p /var/log/supervisor
COPY ./docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Setup nginx
COPY --from=build /build/dist /frontend
COPY ./docker/default /etc/nginx/sites-available/default

# Setup Flask
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /backend
COPY ./server /backend
RUN python3.10 -m pip install -r requirements.txt --ignore-installed --no-compile --no-cache-dir
RUN chmod +x *.sh

# Setup PostgreSQL
COPY ./docker/pg_ident.conf /etc/postgresql/14/main/pg_ident.conf
COPY ./docker/pg_hba.conf /etc/postgresql/14/main/pg_hba.conf

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
