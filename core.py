import newspaper
from langdetect import detect
import dataset
import numpy as np
from datetime import date
import dautil as dl


def get_excluded_domains(db):
    return set([row['url'] for row in db['exclude_domains'].all()])


def is_domain_excluded(url, domains):
    for d in domains:
        if d in url:
            return True

    return False


def get_terms(alist, sw, save=False, fname=None):
    df = dl.nlp.calc_tfidf(alist, sw)

    if save:
        df.to_pickle(fname)

    return dl.nlp.select_terms(df, method=None,
                               select_func=lambda x: np.percentile(x, 50))


def get_date_tuple():
    today = date.today()
    today.strftime('%Y %m %b')

    return today.strftime('%Y %m %b').lower().split()


def check_url_date(url):
    year, mm, mmm = get_date_tuple()

    return year in url and (mm in url or mmm in url)


class TfidfLottery():
    def __init__(self, df):
        self.df = df
        self.terms = df['term'].values
        self.prob = df['tfidf'].values
        self.prob = self.prob/self.prob.sum()

    def draw(self, size=3):
        return set(np.random.choice(self.terms, size=size, p=self.prob))


def connect():
    return dataset.connect('sqlite:///sonar.db')


def not_english(text):
    return detect(text) != 'en'


def init_config():
    config = newspaper.Config()
    config.fetch_images = False
    config.verbose = True

    return config


def parse_article(url):
    a = newspaper.Article(url, init_config())
    a.download()
    a.parse()

    return a
