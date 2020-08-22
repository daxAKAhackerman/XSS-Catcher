# XSS Catcher
XSS Catcher is a simple application that facilitates blind Cross-Site Scripting attacks and attacks that aim to gather data (e.g. cookies, session/local storage, screenshots, etc.). 
## Features
* Generates simple customizable XSS payloads
* Sends email alerts when a new XSS is caught
* Separates the gathered data by clients
* Multi-user with administrative and low privilege users
* Stores information about the triggered XSS payloads like User-Agent, source IP address, timestamp, etc.
* Allows capture of cookies, local storage, session storage and any other specified parameters
* Payload can be customized by the users as he pleases. Simply pass your data in the query string or POST body and the application will catch it! 
* Leverages [html2canvas](https://github.com/niklasvh/html2canvas) and [fingerprintjs2](https://github.com/Valve/fingerprintjs2)
* Captures the full DOM so you can easily know where the payload triggered
* Granular deletion of captured data
* Uses db initialisation scripts with Flask-Migrate, so using an alternative database only requires minor modifications of the docker-compose.yml file
## Install
```bash
git clone https://github.com/daxAKAhackerman/XSS-Catcher.git
cd XSS-Catcher
docker-compose up -d
```
## First login
* Default credentials to connect to the Web interface are **admin:xss**
* Default Web port is **8888**
## *JavaScript mixed content error*
*In order to avoid JavaScript mixed content errors when the XSS payload is triggered, it is highly recommended to put XSS Catcher behind a reverse proxy providing valid TLS certificates.*
## Pictures
### Dashboard
![Alt text](/pictures/dashboard.png?raw=true "Dashboard")
### Payload generation
![Alt text](/pictures/payload.png?raw=true "Payload generation")
### Captured XSS
![Alt text](/pictures/xss.png?raw=true "Captured XSS")
### XSS details
![Alt text](/pictures/details.png?raw=true "XSS details")
### Captured data
![Alt text](/pictures/data.png?raw=true "Captured data")

> The bootstrap theme used can be found [here](https://bootswatch.com/slate/)
