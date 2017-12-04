from __future__ import print_function
from pyquery import PyQuery as pq
import feedparser
import json
from pyspark.sql import SparkSession
import nltk
from pyspark.sql import Row
from pyspark.ml import Pipeline
from pyspark.ml.feature import StopWordsRemover, CountVectorizer, IDF, CountVectorizerModel
from pyspark.mllib.clustering import KMeans
from pyspark.mllib.linalg import Vectors
from math import sqrt

def clean_ascii(str):
    return str.encode("ascii", errors="ignore").decode()

def fetch_news_body(srcs):
    """
    Srap News Body from srcs url
    @param srcs Array of url
    @return String Scrapped news content
    """

    LookupAttr = [
        '#article-entry', '.articlePage', '.page',
        '.page__body', '#body-text', '#storycontent',
        '.Article__body', '.wrap-content', '.MsoNormal'
    ]
    IgnoredAttr = [
        'script', 'style', 'svg', 'button',
        'input', 'text', 'span', 'a', 'img'
    ]
    resp = []
    for i in srcs:
        html = pq(url=i['link'])
        query = html(','.join(LookupAttr)).remove(','.join(IgnoredAttr))
        txt = clean_ascii(i['title'] + i['description'] + query.text())
        resp.append({'text': txt, 'url': i['link'], 'summary': txt[:100]})
    return resp

def parse_news_src():
    """
    Responsible to fetch data from RSS sources
    """

    sources = [
        'https://www.cbsnews.com/latest/rss/main',
        'http://rss.cnn.com/rss/cnn_topstories.rss',
        'http://feeds.foxnews.com/foxnews/latest',
    ]

    resp = []
    for src_url in sources:
        cntxt = feedparser.parse(src_url)
        resp += fetch_news_body(cntxt['entries'])
    # Adding Steve Jobs' related news.
    url=[
        'http://edition.cnn.com/2011/10/05/us/obit-steve-jobs/index.html',
        'http://money.cnn.com/2017/09/12/technology/gadgets/apple-iphone-event/index.html',
        'http://money.cnn.com/2017/09/12/technology/future/inside-apple-park/index.html',
    ]
    srcs = map(lambda x: {'title': '', 'description': '', 'link': x}, url)
    resp += fetch_news_body(srcs)
    return resp

def tokenize(line):
    """
    Tokenize lines into words and clean all words that contains digits
    """

    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    return Row([w.lower() for w in tokenizer.tokenize(line['text'])], line['url'], line['summary'])

def feat_extraction_pipeline():
    """
    Pipeline builder for tf idf feature
    @return Pipeline
    """

    rm_stop_words = StopWordsRemover(inputCol="words", outputCol="filtered")
    count_freq = CountVectorizer(inputCol=rm_stop_words.getOutputCol(),
        outputCol="feat", minDF=2.0)
    return Pipeline(stages=[rm_stop_words, count_freq])

def ml_to_mllib_sparse(v):
    """
    Converting ML => MLLib vector, As we are using mllib KMeans
    from spark while ML features for Pre-Processing stage
    """
    return Vectors.sparse(v.feat.size, v.feat.indices, v.feat.values)

def map_output(r):
  return {'url': r.url, 'cluster_id': model.predict(ml_to_mllib_sparse(r)), 'summary': r.summary}

def calculate_wssse(model, point):
    """
    Evaluate clustering by computing Within Set Sum of Squared Errors
    """

    center = model.centers[model.predict(point)]
    return sqrt(sum([x**2 for x in (point - center)]))

if __name__ == "__main__":
  spark = SparkSession.builder.appName("NewsSimilarityApp")\
    .getOrCreate()

  #words_token = map(tokenize, parse_news_src())
  #raw_df = spark.createDataFrame(words_token, ['words', 'url', 'summary'])

  # TIPS: Use following to avoid HTTP calls to scrab the news data.
  #     Helpful when optimising K-Means parameters.
  #raw_df.write.parquet("/tmp/raw")
  raw_df = spark.read.parquet("/tmp/raw")
  model = feat_extraction_pipeline().fit(raw_df)
  df = model.transform(raw_df)
  sparse_rdd = df.rdd.map(ml_to_mllib_sparse).cache()
  # TODO: Train model on smaller set of data. Right now i have ~100+ items
  #   So training data is same as actual predicted data.
  #train_rdd = spark.sparkContext.parallelize(sparse_rdd.take(100))

  model = KMeans.train(sparse_rdd, k=83, initializationMode="k-means||")
  WSSSE = sparse_rdd.map(lambda p: calculate_wssse(model, p)).reduce(lambda x, y: x + y)
  #print(json.dumps(df.rdd.map(map_output).collect()))
  print("Within Set Sum of Squared Error = " + str(WSSSE))
