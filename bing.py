import urllib
import requests
from requests.auth import HTTPBasicAuth
import configparser
import core
from datetime import datetime
import pandas as pd


def search_bing(query, top=50):
    query = '%27{0}%27'.format(urllib.parse.quote(query))
    base_url = 'https://api.datamarket.azure.com/Bing/Search/Web'
    url = '{0}?Query={1}&$top={2}&$format=json'.format(base_url, query, top)

    user_agent = "Bing Client"
    auth = HTTPBasicAuth(API_KEY, API_KEY)
    headers = {'User-Agent': user_agent}

    response_data = requests.get(url, headers=headers, auth=auth)
    json_result = response_data.json()

    return json_result


def parse_results(json, flag):
    for r in json['d']['results']:
        if core.not_english(r['Title']) or core.not_english(r['Description']):
            continue

        if bing_searches.find_one(url=r['Url']):
            continue

        html.write('<li><b>{0}</b><br/> {1} <a href="{2}">{2}</a></li>'.format(
            r['Title'], r['Description'], r['Url']))
        bing_searches.insert(dict(search_date=datetime.now(),
                                  title=r['Title'],
                                  description=r['Description'],
                                  url=r['Url'],
                                  flag=flag,
                                  res_id=r['ID']))


def handle_query(keyword, flag):
    json = search_bing('python ' + keyword)
    html.write('<h2>{0} Flag={1}</h2>'.format(keyword, flag))
    html.write('<ol>')
    parse_results(json, flag)
    html.write('</ol>')


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config['Bing']['key']
    db = core.connect()
    bing_searches = db['bing_searches']

    with open('bing.html', 'w') as html:
        df = None
        html.write('<html><body>')

        df = pd.read_pickle('title_terms.pkl')

        keywords = pd.read_csv('keywords.csv')['Term'].values[-100:]
        flags = pd.read_csv('keywords.csv')['Flag'].values[-100:]

        for keyword, flag in zip(keywords, flags):
            handle_query(keyword, flag)

        html.write('</body></html>')
