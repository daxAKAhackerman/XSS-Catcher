<h1 align="center">
  <br>
  <img src="https://raw.githubusercontent.com/daxAKAhackerman/XSS-Catcher/master/resources/icon.png" alt="XSS Catcher" width="150">
  <br>
  XSS Catcher
  <br>
</h1>
<h4 align="center">A blind XSS detection and XSS data capture framework that runs on <a href="https://flask.palletsprojects.com/" target="_blank">Flask</a>, <a href="https://vuejs.org/" target="_blank">VueJS</a> and <a href="https://www.postgresql.org/" target="_blank">PostgreSQL</a>.</h4>
XSS Catcher is a simple application that facilitates blind Cross-Site Scripting attacks and attacks that aim to gather data (e.g. cookies, session/local storage, screenshots, etc.).
<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#updating">Updating</a> •
  <a href="#first-login">First login</a> •
  <a href="#api-documentation">API documentation</a> •
  <a href="#demo">Demo</a> •
  <a href="#troubleshooting">Troubleshooting</a> •
  <a href="#credits">Credits</a>
</p>

![screenshot](https://raw.githubusercontent.com/daxAKAhackerman/XSS-Catcher/master/resources/dashboard.png)

## Features

- Generate simple and customizable XSS payloads with an easy-to-use payload generator
- Send notifications when a new XSS is caught using webhooks (Slack, Discord or automation format) and email
- The destination email or webhook can be configured globally and per client
- Multi-user with admin and low privilege users
- Multi factor authentication with TOTP
- Allows capture of cookies, local storage, session storage, and more
- Stores additional information about the XSS such as like HTTP headers, source IP address, timestamp, etc.
- Acts as a "catch-all" endpoint. Just send your data in the querystring (GET) or body (POST) to your client's URL and XSS Catcher will catch it!
- Leverages [html2canvas](https://github.com/niklasvh/html2canvas) and [fingerprintjs](https://github.com/fingerprintjs/fingerprintjs)
- Captures the full DOM so you can easily know where the payload triggered
- Allows you to add custom tags to your XSS to better categorize and search them.
- Allows you to run custom JavaScript code and capture the output.
- Support up to 5 API keys per user to automate advanced attack scenarios when combined with webhooks

## Installation

To clone and run this application, you'll need [Git](https://git-scm.com), [Docker](https://docs.docker.com/engine/), [Docker Compose](https://docs.docker.com/compose/) and [make](https://www.gnu.org/software/make/). From your command line:

```bash
# Clone this repository
$ git clone https://github.com/daxAKAhackerman/XSS-Catcher.git

# Go into the repository
$ cd XSS-Catcher

# Start the application
$ make start
```

## Update

```bash
# Pull the repository
$ git pull

# Before running an update, it is recommended to make a copy of your database in case something unexpected happens
$ cp -r /var/lib/docker/volumes/xss-catcher_xss-db/ /var/lib/docker/volumes/xss-catcher_xss-db-bak/

# Update the application
$ make update
```

## Start/Stop containers

```bash
# Start the containers
$ make start

# Stop the containers
$ make stop
```

## First login

- Default credentials to connect to the Web interface are **admin:xss**
- Default Web port is **8888**

## Demo

![screenshot](https://raw.githubusercontent.com/daxAKAhackerman/XSS-Catcher/master/resources/animation.gif)

## API documentation

The Postman collections can be found here: https://www.postman.com/maintenance-architect-74448403/workspace/xss-catcher

## Troubleshooting

### JavaScript mixed content error

In order to avoid JavaScript mixed content errors when the XSS payload is triggered, it is highly recommended to put XSS Catcher behind a reverse proxy providing valid TLS certificates.

### I accidentally deleted the `.db_password` file that contained my database password

You can set a new database password by following these steps:

```bash
# While XSS Catcher is running, attach to the database container
$ docker exec -it xss-catcher_db_1 bash

# Log into the PostgreSQL database
$ psql -U user xss

# Set a new password for the user "user"
$ \password user

# Exit PostgreSQL and the container
$ exit
$ exit

# Create a new file in the XSS Catcher directory named ".db_password" with the following content
POSTGRES_PASSWORD=YOUR_NEW_PASSWORD

# Stop the application and start it again
$ make stop
$ make start
```

## Credits

- [Flask](https://flask.palletsprojects.com/)
- [VueJS](https://vuejs.org/)
- [BootstrapVue](https://bootstrap-vue.org/)
- [FingerprintJS](https://github.com/fingerprintjs/fingerprintjs)
- [html2canvas](https://github.com/niklasvh/html2canvas)
- [vue-code-highlight](https://github.com/elisiondesign/vue-code-highlight)
- [vue-json-pretty](https://github.com/leezng/vue-json-pretty)

## Disclaimer

Usage of this tool for attacking targets without prior mutual consent is illegal. It is the end user’s responsibility to obey all applicable local, state and federal laws. We assume no liability and are not responsible for any misuse or damage caused by this tool.

## You may also like...

- [Simple One Time Secret](https://github.com/daxAKAhackerman/simple-one-time-secret) - Generate single use, expiring links to share sensitive information
- [Source Map Decoder](https://github.com/daxAKAhackerman/source-map-decoder) - Quickly decode source maps

---

> GitHub [@daxAKAhackerman](https://github.com/daxAKAhackerman/)
