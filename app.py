from __future__ import print_function
from pyquery import PyQuery as pq
import feedparser
from pyspark.sql import SparkSession
import nltk
from pyspark.sql import Row
from pyspark.ml import Pipeline
from pyspark.ml.feature import StopWordsRemover, CountVectorizer
from pyspark.mllib.clustering import KMeans
from pyspark.mllib.linalg import Vectors
from math import sqrt
import pickle

# TODO(Refactor): Move to src/main.py


def create_cluster(sp):
    # Stage 1: Pre-Processing and features extraction
    words_token = map(tokenize, parse_news_src())
    raw_df = sp.createDataFrame(words_token, ['words', 'url', 'summary'])

    # Stage 2: Train our model.
    model = feat_extraction_pipeline().fit(raw_df)
    df = model.transform(raw_df)
    sparse_rdd = df.rdd.map(ml_to_mllib_sparse).cache()

    # TODO: Train model on smaller set of big data. Right now i have ~100+ item
    #   So training data is same as actual predicted data.
    # train_rdd = spark.sparkContext.parallelize(sparse_rdd.take(100))
    K = 83
    model = KMeans.train(sparse_rdd, k=K, initializationMode="k-means||")

    # Stage 3: Predict data then map and save it's serialized version
    WSSSE = sparse_rdd.map(
        lambda p: calculate_wssse(
            model,
            p)).reduce(
        lambda x,
        y: x + y)
    output = {
        'algo_meta': {'wsss_error': str(WSSSE), 'k': K, 'iteration': 100},
        'clustere_news': df.rdd.map(lambda r: map_predict(r, model)).collect()
    }

    return pickle.dump(output, open("index.p", "wb"))

# TODO(Refactor): Move /src/utils.py


def feat_extraction_pipeline():
    """
    Pipeline builder for features extarction
    @return Pipeline
    """

    rm_stop_words = StopWordsRemover(inputCol="words", outputCol="filtered")
    count_freq = CountVectorizer(inputCol=rm_stop_words.getOutputCol(),
                                 outputCol="feat", minDF=2.0)
    return Pipeline(stages=[rm_stop_words, count_freq])


def tokenize(line):
    """
    Tokenize lines into words and clean all words.
    """

    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    return Row(
        [w.lower() for w in tokenizer.tokenize(line['text'])],
        line['url'],
        line['summary']
    )


def map_predict(r, model):
    return {
        'url': r.url,
        'cluster_id': model.predict(ml_to_mllib_sparse(r)),
        'summary': r.summary
    }


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
    # Adding Extra Steve Jobs' related news.
    url = [
        'http://edition.cnn.com/2011/10/05/us/obit-steve-jobs/index.html',
        'http://cnnmon.ie/2w3M6WA',
        'http://cnnmon.ie/2w4a3gB',
    ]
    srcs = map(lambda x: {'title': '', 'description': '', 'link': x}, url)
    resp += fetch_news_body(srcs)
    return resp


def calculate_wssse(model, point):
    """
    Evaluate clustering by computing Within Set Sum of Squared Errors
    """

    center = model.centers[model.predict(point)]
    return sqrt(sum([x**2 for x in (point - center)]))


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


def clean_ascii(str):
    """ Clean nonAscii characters from str """
    return str.encode("ascii", errors="ignore").decode()


def ml_to_mllib_sparse(v):
    """
    Converting ML => MLLib vector, As we are using mllib KMeans
    from spark while ML features for Pre-Processing stage
    """
    return Vectors.sparse(v.feat.size, v.feat.indices, v.feat.values)


if __name__ == "__main__":
    spark = SparkSession.builder.appName("NewsSimilarityApp")\
        .getOrCreate()
    create_cluster(spark)
