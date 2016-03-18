import pandas as pd
import core
import dautil as dl
from datetime import datetime


def main():
    log = dl.log_api.conf_logger(__name__)
    df = pd.read_csv('bookmarks.csv', encoding='cp1252')
    corpus = dl.nlp.WebCorpus('sonar_bookmarks')
    found_feeds = set()

    for url in set(df['URL'].values):
        try:
            a = core.parse_article(url)
            corpus.store_text(a.title.replace(' ', '_'), a.text,
                              url, a.title,
                              " ".join([author.lower()
                                        for author in a.authors]))

            feeds = dl.web.find_feeds(url, a.html)

            if feeds is not None:
                for feed in feeds:
                    found_feeds.add(feed)

            log.debug('Link={0} len(text)={1}'.format(
                url, len(a.text)))
        except Exception as e:
            log.warning('{0} {1}'.format(url, e))

    with open('feeds.csv', 'a') as f:
        for feed in found_feeds:
            if 'comments' not in feed and 'commits' not in feed:
                f.write('{0},{1},Recommended\n'.format(
                    datetime.now(), feed))

if __name__ == "__main__":
    main()
