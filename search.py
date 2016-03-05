from googleapiclient.discovery import build
from urllib.parse import quote_plus
import datetime
import configparser
import pandas as pd


def format_date(date):
    return datetime.datetime.strftime(date, '%Y%m%d')


def get_response(service, query, yest, today, cx):
    return service.cse().list(
        q=quote_plus(query, safe='"'),
        cx=cx,
        sort='date:r:{0}:{1}'.format(yest, format_date(today))).execute()


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    service = build("customsearch", "v1",
                    developerKey=config['Custom Search Engine']['key'])

    today = datetime.datetime.now()
    yesterday = format_date(today - datetime.timedelta(1))

    with open('result.html', 'w') as html:
        html.write('<html>')

        df = pd.read_csv('keywords.csv')
        df = df[df['Flag'] == 'Use']

        for term in df['Term']:
            query = 'python data analysis \"{}\"'.format(term)
            res = get_response(service, query, yesterday,
                               today, config['Custom Search Engine']['cx'])
            html.write('<h1>{}</h1>'.format(query))

            if res.get('items') is None:
                continue

            html.write('<ol>')

            for i in res['items']:
                html.write('<li><a href="{1}">{0}</a></li>'.format(
                    i['htmlSnippet'], i['link']))

            html.write('</ol>')

        html.write('</html>')

if __name__ == '__main__':
    main()
