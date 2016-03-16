from googleapiclient.discovery import build
from urllib.parse import quote_plus
import datetime
import configparser
import pandas as pd
from langdetect import detect
import dautil as dl


def format_date(date):
    return datetime.datetime.strftime(date, '%Y%m%d')


def get_response(service, query, yest, today, cx):
    return service.cse().list(
        q=quote_plus(query, safe='"'),
        cx=cx,
        sort='date:r:{0}:{1}'.format(yest, format_date(today))).execute()


def main():
    log = dl.log_api.conf_logger(__name__)
    config = configparser.ConfigParser()
    config.read('config.ini')
    service = build("customsearch", "v1",
                    developerKey=config['Custom Search Engine']['key'])

    today = datetime.datetime.now()
    yesterday = format_date(today - datetime.timedelta(1))
    hates = set(pd.read_csv('exclude_urls.csv')['URL'].values)

    with open('result.html', 'w') as html:
        html.write('<html><body>')

        df = pd.read_csv('keywords.csv')
        df = df[df['Flag'] == 'Use']

        for term in df['Term']:
            query = 'python {}'.format(term)
            res = get_response(service, query, yesterday,
                               today, config['Custom Search Engine']['cx'])
            html.write('<h1>{}</h1>'.format(query))

            if res.get('items') is None:
                continue

            html.write('<ol>')

            for i in res['items']:
                if i['link'] in hates:
                    continue

                if detect(i['htmlSnippet']) != 'en':
                    log.debug('Not English: {0}'.format(i['htmlSnippet']))
                    continue

                html.write('<li>{0} <a href="{1}">link</a></li>'.format(
                    i['htmlSnippet'], i['link']))

            html.write('</ol>')

        html.write('</body></html>')

if __name__ == '__main__':
    main()
