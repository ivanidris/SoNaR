import feedparser as fp
import newspaper
import dautil as dl
import listparser
import os
import core
import pandas as pd


def process_url(entry):
    try:
        if entry.link in corpus.url_set:
            return

        a = core.parse_article(entry.link)
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

    df = pd.read_csv('feeds.csv')
    df = df[df['Flag'] == 'Use']
    urls.extend(df['URL'].values)

    for f in os.listdir('opml'):
        if f.endswith('opml'):
            fname = os.path.join('opml', f)
            parsed_opml = listparser.parse(fname)
            urls.extend([feed.url for feed in parsed_opml.feeds])

    log = dl.log_api.conf_logger(__name__)
    config = core.init_config()

    corpus = dl.nlp.WebCorpus('sonar_corpus')

    for url in set(urls):
        rss = fp.parse(url)

        for entry in set(rss.entries):
            process_url(entry)
