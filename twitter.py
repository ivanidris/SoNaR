from nltk.twitter import Query
from nltk.twitter import credsfromfile
from datetime import datetime
import pickle
from datetime import timedelta
import dautil as dl
import pandas as pd
import core


def hrefs_from_text(str):
    res = str

    for s in str.split():
        if s.startswith('http'):
            res = str.replace(s, '<a href=\"{0}\">{0}</a>'.format(s))

    return res


def hours_from_now(dt):
    diff = int(datetime.strftime(datetime.now(), '%s')) - \
        int(datetime.strftime(dt, '%s'))

    return diff/3600


def write_file():
    with open('twitter.html', 'w') as html:
        html.write('<html><body><ol>\n')

        yesterday = datetime.now() - timedelta(1)
        res = db.query('SELECT html FROM twitter_searches \
                       WHERE search_date > \"{}\"'.
                       format(yesterday))

        for row in res:
            html.write('<li>{}</li>\n'.format(row['html']))

        html.write('</ol>\n')
        html.write('<p>Created {}</p>'.format(datetime.now()))
        html.write('</body></html>')


def search():
    oauth = credsfromfile()
    client = Query(**oauth)
    df = pd.read_sql('SELECT URL FROM twitter_users',
                     db.executable.raw_connection())

    users = set([u.replace('https://twitter.com/', '')
                 for u in df['URL'].values])
    terms = set(['@' + u for u in users])

    with open('terms.pkl', 'rb') as f:
        terms = terms.union(pickle.load(f))

    searches = 0

    li_html = 'name={0} created={1} favorited={2} retweeted={3} \
        {4} query={5}'

    for term in terms:
        searches += 1
        row = twitter_searches.find_one(query=term)

        if row is not None:
            if hours_from_now(row['search_date']) < 24:
                continue

        tweets = client.search_tweets(keywords=term + ' python http -RT',
                                      lang='en')

        for t in tweets:
            if int(t['favorite_count']) == 0:
                log.debug('No favorites')
                continue

            text = t['text']
            dt = datetime.strptime(t['created_at'],
                                   '%a %b %d %H:%M:%S %z %Y')

            if hours_from_now(dt) > 24:
                continue

            if core.not_english(text):
                log.debug('Not english: {}'.format(text))
                continue

            log.debug('Searching for {}'.format(term))
            uname = t['user']['screen_name']
            uname_html = '<a href="https://twitter.com/{0}">{0}</a>'

            if uname not in set(users):
                db['twitter_users'].insert(
                    dict(Flag='Recommended', Date=datetime.now(),
                         URL='https://twitter.com/' + uname))

            html = li_html.format(uname_html.format(uname), t['created_at'],
                                  t['favorite_count'], t['retweet_count'],
                                  hrefs_from_text(text), term)

            twitter_searches.upsert(dict(query=term,
                                         search_date=datetime.now(),
                                         html=html),
                                    ['query', 'html'])
        if searches == 150:
            break


if __name__ == "__main__":
    log = dl.log_api.conf_logger(__name__)
    db = core.connect()
    twitter_searches = db['twitter_searches']
    search()
    write_file()
