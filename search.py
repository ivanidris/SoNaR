from googleapiclient.discovery import build
from urllib.parse import quote_plus
import datetime
import configparser
import pandas as pd
import dautil as dl
import core


def process_query(html, query):
    html.write('</ol>')
    res = get_response(service, query, yesterday,
                       today, config['Custom Search Engine']['cx'])
    html.write('<h1>{}</h1>'.format(query))

    if res.get('items') is None:
        return

    html.write('<ol>')

    for i in res['items']:
        if i['link'] in hates:
            continue

        # Avoid CVs with buzzwords
        if 'resume' in i['link']:
            continue

        if cse_searches.find_one(link=i['link']):
            continue

        if core.not_english(i['htmlSnippet']):
            log.debug('Not English: {0}'.format(i['htmlSnippet']))
            continue

        html.write('<li>{0} <a href="{1}">{1}</a></li>'.format(
            i['htmlSnippet'], i['link']))
        cse_searches.insert(dict(search_date=datetime.datetime.now(),
                                 html_snippet=i['htmlSnippet'],
                                 link=i['link']))


def format_date(date):
    return datetime.datetime.strftime(date, '%Y%m%d')


def get_response(service, query, yest, today, cx):
    return service.cse().list(
        q=quote_plus(query, safe='"'),
        cx=cx,
        sort='date:r:{0}:{1}'.format(yest, format_date(today))).execute()


def main():

    with open('result.html', 'w') as html:
        html.write('<html><body>')

        df = pd.read_csv('keywords.csv')
        df = df[df['Flag'] == 'Use']

        for term in df['Term']:
            query = 'python {}'.format(term)
            process_query(html, query)

        df = pd.read_csv('code_keywords.csv')
        df = df[df['Flag'] == 'Use']

        # Some confusion around Term v term
        for term in df['term']:
            query = 'python {}'.format(term)
            process_query(html, query)

        html.write('</body></html>')

if __name__ == '__main__':
    log = dl.log_api.conf_logger(__name__)
    config = configparser.ConfigParser()
    config.read('config.ini')
    service = build("customsearch", "v1",
                    developerKey=config['Custom Search Engine']['key'])

    today = datetime.datetime.now()
    yesterday = format_date(today - datetime.timedelta(1))
    hates = set(pd.read_csv('exclude_urls.csv')['URL'].values)
    db = core.connect()
    cse_searches = db['cse_searches']
    main()
