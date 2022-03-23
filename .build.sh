#!/bin/bash

python3 -m pip install --user virtualenv
python3 -m venv .venv
source .venv/bin/activate
cd schools
pip install -r requirements.txt
pip install schools --no-index --find-links .

# Should not be necessary with travis, but nice to have as a guide
#wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
#echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
#apt update && apt install -y mongodb-org
#apt install apt-transport-https ca-certificates curl software-properties-common
#curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
#add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
#apt-cache policy docker-ce
#apt install docker-ce

apt install redis-server

docker pull mongo && docker run --name mongodb -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=mdipass -p 27017:27017 mongo &
python3 -m rq worker crawling-tasks --path . &
python3 schools/app.py &
