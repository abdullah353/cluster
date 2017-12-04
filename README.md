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

Visit [http://52.26.18.233:8083/cluster](http://52.26.18.233:8083/cluster) To see the response.

> Note: Use the IP Address accordingly, in above url.

## Understanding the Response:

```json
{
  "algo_meta": {
    "wsss_error": "476.100523092",
    "k": 83,
    "iteration": 100
  },
  "clustere_news": [
    {
      "url": "https://www.cbsnews.com/news/billy-bush-donald-trump-voice-access-hollywood-tape/",
      "cluster_id": 46,
      "summary": "Billy Bush confirms it was Trump on infamous tapeBush writes of the tape validity amid reports tha"
    },
    {
      "url": "https://www.cbsnews.com/news/commentary-the-anti-trump-coalition-isnt-happening/",
      "cluster_id": 13,
      "summary": "Commentary: The anti-Trump coalition isn't happeningWhy a bipartisan "
    },
   .....
}
```

| Key        | Purpose           |
| ------------- |:-------------:|
| algo_meta.wsss_error      | Within Set Sum of Squared Errors |
| algo_meta.k      | K used to generate the data      |
| algo_meta.iteration | Maximum Number of Iteration      |
| clustere_news.cluster_id | Cluster Id in which news categorized |
| clustere_news.url | URL Of the original News |
| clustere_news.summary | Summary of the original New |
