from nltk.twitter import Query
from nltk.twitter import credsfromfile
import pandas as pd


def hrefs_from_text(str):
    res = str

    for s in str.split():
        if s.startswith('http'):
            res = str.replace(s, '<a href=\"{0}\">{0}</a>'.format(s))

    return res

oauth = credsfromfile()
client = Query(**oauth)

with open('twitter.html', 'w') as html:
    html.write('<html><body>')
    df = pd.read_csv('keywords.csv')
    df = df[df['Flag'] == 'Use']

    li_html = '<li>name={0} created={1} favorited={2} retweeted={3} {4}</li>'

    for term in df['Term']:
        query = 'python {}'.format(term)
        html.write('<h1>{}</h1>'.format(query))
        html.write('<ol>')
        tweets = client.search_tweets(keywords=query + ' http -RT',
                                      lang='en', limit=5)

        for t in tweets:
            text = t['text']
            uname = t['user']['name']

            html.write(li_html.format(uname, t['created_at'],
                                      t['favorite_count'],
                                      t['retweet_count'],
                                      hrefs_from_text(text)))

        html.write('</ol>')

    html.write('</body></html>')
