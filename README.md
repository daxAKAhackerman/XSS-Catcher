# XSS Catcher
XSS Catcher is a simple application that facilitates blind Cross-Site Scripting attacks and attacks that aim to gather data (e.g. cookies). 
## Features
* Generates simple customizable XSS payloads. 
* Separates the gathered data by client. 
* Multi-user. 
* Stores informations about the triggered XSS payloads like User-Agent, source IP address, timestamp, etc.
* Allows capture of cookies, local storage, session storage and any other specified parameters
* Granular deletion of captured data
## Install
```bash
git clone https://github.com/daxAKAhackerman/XSS-Catcher.git
cd XSS-Catcher
docker-compose up -d
# Even if the containers are up, allow for a little bit of time before the first login. The MySQL container takes like 1 minute to be ready
```
## First login
* Default credentials to connect to the Web interface are **admin:xss**
* Default Web port is **8888**
## To Do
* [x] Create a README.md file
* [ ] Allow management of users
* [X] Add some CSS
* [ ] Add concept of admin users and client permission management
## Pictures
![Alt text](/pictures/dashboard.png?raw=true "Dashboard")
![Alt text](/pictures/payload.png?raw=true "Payload generation")
![Alt text](/pictures/xss.png?raw=true "Captured XSS")
![Alt text](/pictures/details.png?raw=true "XSS details")
![Alt text](/pictures/data.png?raw=true "Captured data")

> The bootstrap theme used can be found [here](https://bootswatch.com/slate/)