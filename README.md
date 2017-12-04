# Usage Instructions
> Tested on Ubuntu 16 

## 1. Install Spark
```bash
# Update package.
sudo apt -qy update

# Install JRE and pip
sudo apt -qy install default-jre python-pip

# Download from spark.
wget https://d3kbcqa49mib13.cloudfront.net/spark-2.2.0-bin-hadoop2.7.tgz

# Extract it.
tar -xzf spark-2.2.0-bin-hadoop2.7.tgz

# Remove tar file
rm spark-2.2.0-bin-hadoop2.7.tgz

# Adjusting Environment variable PATH
echo 'export PATH=$PATH:~/spark-2.2.0-bin-hadoop2.7/sbin/' >> ~/.bash_aliases
echo 'export PATH=$PATH:~/spark-2.2.0-bin-hadoop2.7/bin/' >> ~/.bash_aliases
echo 'export SPARK_HOME=~/spark-2.2.0-bin-hadoop2.7/' >> ~/.bash_aliases

source ~/.bashrc
```

## 2. Install App and it's dependencies
```
git clone https://github.com/mabdullah353/cluster.git
cd cluster

# Install dependencies
sudo pip install -r requirements.txt
python -c 'import nltk
nltk.download("punkt")'
```

## 3. Run The App on spark
```
spark-submit app.py
```

This will generate `index.p` serialized python object which is going to be utillized by api endpoint in `api.py`

# Launch The API

api.py holds is responsible for expoing API endpoint to launch it use the following method

```bash
$ python api.py --port 8083
```

To list full usage of above command use the following help command.
```bash
$ python api.py --help
usage: api.py [-h] [--host HOST] [--port PORT] [--debug DEBUG]

Expose K-Mean cluster

optional arguments:
  -h, --help     show this help message and exit
  --host HOST    Adjust the host of the server.
  --port PORT    Adjust the port of the server.
  --debug DEBUG  Enable app debugging.
```


