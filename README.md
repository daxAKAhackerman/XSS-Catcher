<h1 align="center">
  <br>
  <img src="https://raw.githubusercontent.com/daxAKAhackerman/XSS-Catcher/master/resources/icon.png" alt="XSS-Catcher" width="150">
  <br>
  XSS Catcher
  <br>
</h1>
<h4 align="center">A blind XSS detection framework that runs on <a href="https://flask.palletsprojects.com/" target="_blank">Flask</a> and <a href="https://vuejs.org/" target="_blank">VueJS</a>.</h4>
XSS Catcher is a simple application that facilitates blind Cross-Site Scripting attacks and attacks that aim to gather data (e.g. cookies, session/local storage, screenshots, etc.).
<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#updating">Updating</a> •
  <a href="#first-login">First login</a> •
  <a href="#demo">Demo</a> •
  <a href="#troubleshooting">Troubleshooting</a> •
  <a href="#credits">Credits</a>
</p>

![screenshot](https://raw.githubusercontent.com/daxAKAhackerman/XSS-Catcher/master/resources/dashboard.png)

## Features

-   Generates simple customizable XSS payloads
-   Sends email alerts or webhooks (in Slack format) when a new XSS is caught
-   The destination email or webhook can be configured globally and per client
-   Separates the gathered data by clients
-   Multi-user with administrative and low privilege users
-   Stores information about the triggered XSS payloads like User-Agent, source IP address, timestamp, etc.
-   Allows capture of cookies, local storage, session storage, and more.
-   Acts as a "catch-all" endpoint. Just send your data in the querystring (GET) or body (POST) to your client's URL and XSS Catcher will catch it!
-   Leverages [html2canvas](https://github.com/niklasvh/html2canvas) and [fingerprintjs](https://github.com/fingerprintjs/fingerprintjs)
-   Captures the full DOM so you can easily know where the payload triggered
-   Allows you to add custom tags to your XSS to better categorize them.

## Installation

To clone and run this application, you'll need [Git](https://git-scm.com), [Docker](https://docs.docker.com/engine/), [Docker Compose](https://docs.docker.com/compose/) and [make](https://www.gnu.org/software/make/). From your command line:

```bash
# Clone this repository
$ git clone https://github.com/daxAKAhackerman/XSS-Catcher.git

# Go into the repository
$ cd XSS-Catcher

# Deploy the application. Also, run this once if you are migrating from v1.0.0
$ make deploy
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

-   Default credentials to connect to the Web interface are **admin:xss**
-   Default Web port is **8888**

## Demo

![screenshot](https://raw.githubusercontent.com/daxAKAhackerman/XSS-Catcher/master/resources/animation.gif)

## Troubleshooting

### JavaScript mixed content error

In order to avoid JavaScript mixed content errors when the XSS payload is triggered, it is highly recommended to put XSS Catcher behind a reverse proxy providing valid TLS certificates.

### Database looks empty after migrating from v1.0.0 to v1.1.0 and up

Since v1.1.0 introduced the usage of randomized database passwords, be sure to run `make deploy` after pulling the new version. If you don't, your application will fallback to a local SQLite database, which is empty by default.

### I accidentally deleted the `.env` file that contained my database password

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

# Create a new file in the XSS Catcher directory named ".env" with the following content
POSTGRES_PASSWORD=YOUR_NEW_PASSWORD
POSTGRES_USER=user
POSTGRES_DB=xss

# Stop the application and start it again
$ make stop
$ make start
```

###

## Credits

-   [Flask](https://flask.palletsprojects.com/)
-   [VueJS](https://vuejs.org/)
-   [BootstrapVue](https://bootstrap-vue.org/)
-   [FingerprintJS](https://github.com/fingerprintjs/fingerprintjs)
-   [html2canvas](https://github.com/niklasvh/html2canvas)
-   [Bootswatch Slate theme](https://bootswatch.com/slate/)
-   [vue-code-highlight](https://github.com/elisiondesign/vue-code-highlight)
-   [vue-json-pretty](https://github.com/leezng/vue-json-pretty)

## Disclaimer

Usage of this tool for attacking targets without prior mutual consent is illegal. It is the end user’s responsibility to obey all applicable local, state and federal laws. We assume no liability and are not responsible for any misuse or damage caused by this tool.

## You may also like...

-   [Source Map Decoder](https://github.com/daxAKAhackerman/source-map-decoder) - Quickly decode source maps

---

> GitHub [@daxAKAhackerman](https://github.com/daxAKAhackerman/)
