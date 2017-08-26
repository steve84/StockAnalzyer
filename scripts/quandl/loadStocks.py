import requests
import urllib.parse
import json
import argparse
from datetime import datetime

from bs4 import BeautifulSoup
import quandl
import psycopg2

# Argument parser
parser = argparse.ArgumentParser(description='Load stock definitions to data tables.')
parser.add_argument('-n', dest='maxItems', type=int, help='number of stocks to load')
parser.add_argument('-u', dest='db_user', help='user name of the database')
parser.add_argument('-p', dest='db_pwd', help='database password')
parser.add_argument('-d', dest='db_name', help='database name')
parser.add_argument('--host', dest='db_host', help='database name')

maxItems = parser.parse_args().maxItems
db_user = parser.parse_args().db_user
db_pwd = parser.parse_args().db_pwd
db_name = parser.parse_args().db_name
db_host = parser.parse_args().db_host

conn = psycopg2.connect("dbname=%s user=%s host=%s" % (db_name, db_user, db_host))
cur = conn.cursor()

totalHits = -1
page = 1
totalPages = 1
pageSize = 100

baseUrl = 'https://www.quandl.com/api/v3/datasets.json'
databaseCode = 'RB1'
apiKey = 'c-7-dq_SdcLs_6me4Azt'

# Program logic
noneStr = lambda s: '' if s is None else str(s)

totalProcessed = 0
totalInserted = {'countries': 0, 'branches': 0, 'stocks': 0}

existing_countries = dict()
existing_branches = dict()

while page <= totalPages:
    query_params = dict()
    query_params['database_code'] = databaseCode
    query_params['per_page'] = pageSize
    query_params['sort_by'] = 'id'
    query_params['page'] = page
    query_params['api_key'] = apiKey

    link = baseUrl + '?' +  urllib.parse.urlencode(query_params)
    response = requests.get(link)
    if response.status_code == 200:
        json_response = response.json()
        if totalHits < 0:
            totalHits = json_response['meta']['total_count']
            totalPages = json_response['meta']['total_pages']
        
        page = json_response['meta']['next_page']
        
        stocks = json_response['datasets']
        
        for stock in stocks:
            if stock['frequency'] == 'annual':
                print(stock['description'])
                description_html = BeautifulSoup(stock['description'], 'html.parser')
                description_html_parts = description_html.findAll('p')
                for part in description_html_parts:
                    if part.find('b') is None:
                        name_parts = part.text.split('for ')
                        if len(name_parts) == 2:
                            stock['name'] = name_parts[1].strip()
                    else:
                        if part.find('b').text.find('Country') > -1:
                            stock['country'] = part.text.replace('Country:', '').strip()
                        if part.find('b').text.find('ISIN') > -1:
                            stock['isin'] = part.text.replace('ISIN:', '').strip()
                        if part.find('b').text.find('YF Ticker') > -1:
                            stock['symbol'] = part.text.replace('YF Ticker:', '').strip()
                        if part.find('b').text.find('Sector:') > -1:
                            stock['branch'] = part.text.replace('Sector:', '').strip()
                        if part.find('b').text.find('Sector Group:') > -1:
                            stock['branch_group'] = part.text.replace('Sector Group:', '').strip()
                        if part.find('b').text.find('Reference Currency') > -1:
                            stock['currency'] = part.text.replace('Reference Currency:', '').strip()

                if 'newest_available_date' in stock.keys() and stock['newest_available_date'] is not None:
                    newest_date = datetime.strptime(stock['newest_available_date'], '%Y-%m-%d')
                    stock['business_year_end'] = newest_date.strftime('%d.%m.')
                else:
                    stock['business_year_end'] = 'n.a.'
                stock['quandl_rb1_id'] = int(stock['dataset_code'].split('_')[0])
                stock['country_id'] = None
                stock['branch_id'] = None
                    
                # select
                if not noneStr(stock['country']) in existing_countries.keys():
                    cur.execute("""SELECT * FROM tcountry WHERE name = %(country)s;""", stock)
                    country = cur.fetchone()
                    if not country:
                        # insert
                        cur.execute("""INSERT INTO tcountry (name) VALUES (%(country)s) RETURNING country_id;""", stock)
                        stock['country_id'] = cur.fetchone()[0]
                        totalInserted['countries'] += 1
                    else:
                        stock['country_id'] = country[0]
                    if stock['country']:
                        existing_countries[noneStr(stock['country'])] = stock['country_id']
                else:
                    stock['country_id'] = existing_countries[noneStr(stock['country'])]

                # select
                if not (noneStr(stock['branch']) + noneStr(stock['branch_group']))  in existing_branches.keys():
                    cur.execute("""SELECT * FROM tbranch WHERE name = %(branch)s;""", stock)
                    branch = cur.fetchone()
                    if not branch:
                        # insert
                        cur.execute("""INSERT INTO tbranch (name, branch_group) VALUES (%(branch)s, %(branch_group)s) RETURNING branch_id;""", stock)
                        stock['branch_id'] = cur.fetchone()[0]
                        totalInserted['branches'] += 1
                    else:
                        stock['branch_id'] = branch[0]
                    if stock['branch']:
                        existing_branches[noneStr(stock['branch']) + noneStr(stock['branch_group'])] = stock['branch_id']
                else:
                    stock['branch_id'] = existing_branches[noneStr(stock['branch']) + noneStr(stock['branch_group'])]

                # select
                cur.execute("""SELECT * FROM tstock WHERE isin = %(isin)s;""", stock)
                if cur.rowcount == 0:
                    # insert
                    cur.execute("""INSERT INTO tstock (name, isin, business_year_end, branch_id, country_id, currency, quandl_rb1_id) VALUES (%(name)s, %(isin)s, %(business_year_end)s, %(branch_id)s, %(country_id)s, %(currency)s, %(quandl_rb1_id)s);""", stock)
                    totalInserted['stocks'] += 1
                    totalProcessed += 1

            if maxItems and totalProcessed >= maxItems:
                break
        if maxItems and totalProcessed >= maxItems:
            break
    
    else:
        break


conn.commit();
conn.close();

print('Totally processed: %s' % str(totalProcessed))
print('Inserts to country table: %s' % str(totalInserted['countries']))
print('Inserts to branch table: %s' % str(totalInserted['branches']))
print('Inserts to stock table: %s' % str(totalInserted['stocks']))