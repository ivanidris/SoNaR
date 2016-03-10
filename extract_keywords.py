import datetime
import dautil as dl
import pandas as pd


def get_terms(alist, sw):
    df = dl.nlp.calc_tfidf(alist, sw)

    return dl.nlp.select_terms(df)


corpus = dl.nlp.WebCorpus('sonar_corpus')
texts = corpus.get_texts()

sw = dl.nlp.common_unigrams()
unigrams_tfidf = dl.nlp.calc_tfidf(texts, ngram_range=None)
all_unigrams = set(unigrams_tfidf['term'].values.tolist())
uncommon = dl.nlp.select_terms(unigrams_tfidf)
sw = sw.union(all_unigrams - uncommon)

text_terms = get_terms(texts, sw)
title_terms = get_terms(corpus.get_titles(), sw)

terms = text_terms.intersection(title_terms) - corpus.get_authors()

fname = 'keywords.csv'
old = set(pd.read_csv(fname)['Term'].values.tolist())

with open(fname, 'a') as csv_file:
    for t in terms:
        if t not in old and not dl.nlp.has_digits(t) \
                and not dl.nlp.has_duplicates(t):
            ts = datetime.datetime.now().isoformat()
            csv_file.write(ts + ',' + t + ',Use\n')
