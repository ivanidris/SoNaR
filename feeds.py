import feedparser as fp
import newspaper
import pandas as pd
import dautil as dl
import datetime


urls = ['http://planet.scipy.org/rss20.xml',
        'http://dsguide.biz/reader/feeds/posts']
texts = []
titles = []
summaries = []
authors = set()


log = dl.log_api.conf_logger(__name__)

for url in urls:
    rss = fp.parse(url)

    for entry in rss.entries:
        titles.append(entry.title)
        summaries.append(entry.summary)

        try:
            a = newspaper.Article(entry.link, language='en')
            a.download()
            a.parse()
            texts.append(a.text)

            for author in a.authors:
                authors.add(author.lower())

            log.debug('Link={0} len(text)={1}'.format(
                entry.link, len(a.text)))
        except newspaper.article.ArticleException as e:
            log.warning('{0} {1}'.format(entry.link, e))

text_terms = dl.nlp.select_terms(dl.nlp.calc_tfidf(texts))
title_terms = dl.nlp.select_terms(dl.nlp.calc_tfidf(titles))
summary_terms = dl.nlp.select_terms(dl.nlp.calc_tfidf(summaries))

terms = summary_terms.intersection(
    text_terms.intersection(title_terms)) - authors

fname = 'keywords.csv'
old = set(pd.read_csv(fname)['Term'].values.tolist())

with open(fname, 'a') as csv_file:
    for t in terms:
        if t not in old:
            ts = datetime.datetime.now().isoformat()
            csv_file.write(ts + ',' + t + ',Use\n')
