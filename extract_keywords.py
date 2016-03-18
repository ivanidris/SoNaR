import datetime
import dautil as dl
import pandas as pd
import numpy as np
import wikipedia
from joblib import Memory
import pickle


memory = Memory(cachedir='.')


@memory.cache
def search_wiki(phrase):
    return wikipedia.search(phrase)


def get_terms(alist, sw):
    df = dl.nlp.calc_tfidf(alist, sw)

    return dl.nlp.select_terms(df, method=None,
                               select_func=lambda x: np.percentile(x, 50))


corpus = dl.nlp.WebCorpus('sonar_corpus')
saved = dl.nlp.WebCorpus('sonar_bookmarks')
texts = corpus.get_texts()
texts.extend(saved.get_texts())

sw = dl.nlp.common_unigrams()
unigrams_tfidf = dl.nlp.calc_tfidf(texts, ngram_range=None)
all_unigrams = set(unigrams_tfidf['term'].values.tolist())
uncommon = dl.nlp.select_terms(unigrams_tfidf)
sw = sw.union(all_unigrams - uncommon)
sw = sw.union(set(['blog', 'podcast', 'webinar',
                   'tweets', 'nba', 'nfl', 'facebook', 'pinterest']))

text_terms = get_terms(texts, sw)
titles = corpus.get_titles()
titles = titles.union(saved.get_titles())
title_terms = get_terms(titles, sw)

terms = text_terms.intersection(title_terms) - corpus.get_authors()

with open('terms.pkl', 'wb') as f:
    pickle.dump(terms, f)

fname = 'keywords.csv'
old = set(pd.read_csv(fname)['Term'].values.tolist())
terms = terms - old
log = dl.log_api.conf_logger(__name__)
in_wiki = dict()

for t in terms:
    if not dl.nlp.has_digits(t) \
            and not dl.nlp.has_duplicates(t):
        pages = search_wiki('python ' + t)

        if len(pages) > 0:
            log.debug('Term={0}, Wiki pages={1}'.format(t, pages))
            in_wiki[t] = len(pages)
        else:
            log.debug('Term={0} Not found in Wiki'.format(t))

limit = np.percentile(list(in_wiki.values()), 50)
selected = set([term for term, count in in_wiki.items()
                if count < limit])

log.debug('Selected={0}'.format(len(selected)))

with open(fname, 'a') as csv_file:
    for s in selected:
        ts = datetime.datetime.now().isoformat()
        csv_file.write(ts + ',' + s + ',Use\n')
