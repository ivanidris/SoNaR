import feedparser as fp
import newspaper
import pandas as pd
import dautil as dl
import datetime
from multiprocessing_on_dill import Pool
import listparser
import os
import numpy as np


def select(arr):
    return np.percentile(arr, 99.5)


def get_terms(alist):
    df = dl.nlp.calc_tfidf(alist)

    return dl.nlp.select_terms(df, method=None, select_func=select)


def init_config():
    config = newspaper.Config()
    config.fetch_images = False
    config.verbose = True

    return config


def process_url(entry):
    try:
        if entry.link in corpus.url_set:
            return

        a = newspaper.Article(entry.link, config)
        a.download()
        a.parse()

        corpus.store_text(entry.title.replace(' ', '_'),
                          a.text, entry.link, entry.title,
                          " ".join([author.lower()
                                    for author in a.authors]))

        log.debug('Link={0} len(text)={1}'.format(
            entry.link, len(a.text)))
    except newspaper.article.ArticleException as e:
        log.warning('{0} {1}'.format(entry.link, e))

if __name__ == "__main__":
    urls = ['http://planet.scipy.org/rss20.xml',
            'http://planetpython.org/rss20.xml',
            'http://dsguide.biz/reader/feeds/posts']

    for f in os.listdir('opml'):
        if f.endswith('opml'):
            fname = os.path.join('opml', f)
            parsed_opml = listparser.parse(fname)
            urls.extend([feed.url for feed in parsed_opml.feeds])

    log = dl.log_api.conf_logger(__name__)
    config = init_config()

    corpus = dl.nlp.WebCorpus('sonar_corpus')

    entries = []

    for url in set(urls):
        rss = fp.parse(url)

        for entry in set(rss.entries):
            entries.append(entry)

    with Pool(8) as p:
        p.map(process_url, entries)

    texts = corpus.get_texts()

    text_terms = get_terms(texts)
    title_terms = get_terms(corpus.get_titles())

    terms = text_terms.intersection(title_terms) - corpus.get_authors()

    fname = 'keywords.csv'
    old = set(pd.read_csv(fname)['Term'].values.tolist())

    with open(fname, 'a') as csv_file:
        for t in terms:
            if t not in old:
                ts = datetime.datetime.now().isoformat()
                csv_file.write(ts + ',' + t + ',Use\n')
