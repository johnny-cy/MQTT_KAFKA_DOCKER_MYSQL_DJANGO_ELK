# How to run Python3.6 on Ubuntu 16.04

## Install Python 3.6

```
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get update
sudo apt-get install python3.6
```

## Install virtualenv and build tools
```
sudo apt-get install virtualenv
sudo apt-get install libmysqlclient-dev
sudo apt-get install python3.6-dev
```

## Run example

```
cd <epa2018>/examples/read_database

virtualenv -p python3.6 venv3.6
source venv3.6/bin/activate

pip install -r requirements.txt

python read_lass.py
```
