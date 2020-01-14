#Readme Linux Server Configuration

The port on which you can access the server is: 80
SSH port is : 2200 
Put the servers Public IPv4 address and route: `3.20.105.201/catalog/` in your browser to access the application.

***Dependencies:***

-apache2
- postgresql
- python3.6
- pip
- uwsgi

***Python packages:***

- sqlalchemy
- flask
- packaging
- oauth2client
- redis
- passlib
- flask-httpauth
- bleach
- requests
- psycopg2-binary
- flask-sqlalchemy


ssh:
ssh -i .ssh/AWS.pem ubuntu@ec2-3-134-118-107.us-east-2.compute.amazonaws.com

**1. Dependencies**

```bash

# connect to instance 
ssh -i .ssh/AWS_fullstack.pem ubuntu@18.184.199.190

# update package system
sudo apt-get update
sudo apt-get upgrade

# change port 
sudo vim /etc/ssh/sshd_config # change port in this file 
sudo su - 
sudo systemctl restart sshd 

sudo timedatectl set-timezone Europe/Berlin 


# install postgresql system
sudo apt-get install postgresql postgresql-contrib
```

***2. Create user & initial setup***

To create a user, the `postgres` user has to be used:
```bash
# switch to postgres user
sudo -i -u postgres

# create your user: catalog
createuser --interactive

# can create Databases but not other users.
```

***3. Install Python packages***

Created a virtualenvironment with virtualenvwrapper and installed the following libraries and dependencies:

```bash

#pip 
sudo apt install python-pip3
# install apache dependencies , install seperately do not put into requirements.txt
pip3 install mod_wsgi-httpd
pip3 install mod_wsgi
#python packages via pip package manager
pip3 install flask packaging oauth2client redis passlib flask-httpauth
pip3 install sqlalchemy flask-sqlalchemy psycopg2-binary bleach requests
```

Third party sources used where:

[Port](https://stackoverflow.com/questions/13475303/running-ssh-on-amazon-ec2-instance-on-port-other-than-22)
[Postgres](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04)
[redis](https://www.digitalocean.com/community/tutorials/how-to-install-redis-from-source-on-ubuntu-18-04)
[Firewall](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-18-04)
[ssh keys for grader](https://www.digitalocean.com/community/questions/ubuntu-16-04-creating-new-user-and-adding-ssh-keys)
[timezone](https://linuxize.com/post/how-to-set-or-change-timezone-on-ubuntu-18-04/)
[deploy Flaskapp](https://towardsdatascience.com/deploying-a-python-web-app-on-aws-57ed772b2319)
