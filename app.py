from __future__ import print_function
from pyquery import PyQuery as pq
import feedparser


def clean_ascii(str):
    return str.encode("ascii", errors="ignore").decode()


def fetch_news_body(srcs):
    """
    Srap News Body from srcs url
    @param srcs Array of url
    @return String Scrapped news content
    """

    LookupAttr = [
        '#article-entry',
        '.articlePage',
        '.page',
        '.page__body',
        '#body-text',
        '#storycontent',
        '.Article__body',
        '.wrap-content',
        '.MsoNormal']
    IgnoredAttr = [
        'script',
        'style',
        'svg',
        'button',
        'input',
        'text',
        'span',
        'a',
        'img']
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
        resp.append(fetch_news_body(cntxt['entries']))

    # Adding Steve Jobs' related news.
    url=[
        'http://edition.cnn.com/2011/10/05/us/obit-steve-jobs/index.html',
        'http://money.cnn.com/2017/09/12/technology/gadgets/apple-iphone-event/index.html',
        'http://money.cnn.com/2017/09/12/technology/future/inside-apple-park/index.html',
    ]
    srcs = map(lambda x: {'title': '', 'description': '', 'link': x}, url)
    resp.append(fetch_news_body(srcs))
    return resp

print(parse_news_src())
