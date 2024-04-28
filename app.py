from flask import Flask, render_template,request,Response
import plotly.express as px   #for plotting
import plotly.io as pio
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import logging              #for logging
import concurrent.futures   #multithreading
import time
import threading


#internal imports
from GROWW import GROWW
from GOOGLEFIN import GOOGLEFIN
from graph import plot



app = Flask(__name__)
blocked_user_agents = ["Go-http-client/1.1"]

@app.before_request
def block_user_agent():
    user_agent = request.headers.get('User-Agent')
    if user_agent in blocked_user_agents:
        abort(403)

json_object = None

@app.route('/')
def index():
    global json_object


    URLS = [ "https://trendlyne.com/portfolio/bulk-block-deals/54044/vanguard-fund/",
            "https://trendlyne.com/portfolio/bulk-block-deals/53902/government-of-singapore/",
            "https://trendlyne.com/portfolio/bulk-block-deals/597533/icici-group-portfolio/",
            "https://trendlyne.com/portfolio/bulk-block-deals/597531/sbi-group-portfolio/",
            "https://trendlyne.com/portfolio/bulk-block-deals/597532/hdfc-group-portfolio/",
            "https://trendlyne.com/portfolio/bulk-block-deals/53945/kotak-mahindra-group-portfolio/"
            ]

    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com/',  # Add the referer of the website you're scraping data from
        'Upgrade-Insecure-Requests': '1',
    }


    def load_url(url):
        response = requests.get(url,headers=headers)
        soup = BeautifulSoup(response.text,'html.parser')
        list_col_name=soup.find_all('tr')[0].find_all('th')
        list_rows = soup.find_all('tr')[1:]
        result = []
        result.append([col.text for col in list_col_name])
        result[0].append("Stock Link")

        for tr in list_rows:
            temp=[]
            for td in tr.find_all('td'):
                temp.append(td.get_text().strip())
            temp.append("https://trendlyne.com"+tr.find('a')['href'])
            result.append(temp)
        return result


    

    def main():
            df = None
            executor =concurrent.futures.ThreadPoolExecutor(max_workers=len(URLS))
            results = executor.map(load_url, URLS)
            for result in results:
                if df is None:
                    df = pd.DataFrame(result[1:],columns=result[0])
                else:
                    df = pd.concat([df,pd.DataFrame(result[1:],columns=result[0])],ignore_index=False)
                
            return df


    df = main()

    df.Date = pd.to_datetime(df.Date)
    df['Percentage Traded %'] = df['Percentage Traded %'].str.replace('%','')
    df['Percentage Traded %'] = pd.to_numeric(df['Percentage Traded %'],errors='coerce')
    df.sort_values(['Date','Percentage Traded %'],ascending=False,inplace=True)
    df.Date = df.Date.astype('str')
    df=df.reset_index()
    df.drop('index',axis=1,inplace=True)
    df['stock_id'] = df.index
    json_string = df[:150].to_json(orient='records')
    json_object = json.loads(json_string)

    
    return render_template('index.html', data=json_object)


@app.route('/stock/<stock_id>')
def stock_details(stock_id):
    stock_id = int(stock_id)
    for stock in json_object:
        if stock['stock_id']==stock_id:
            stock_name = stock['Stock']
            stock_link = stock['Stock Link']
    headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Referer': 'https://www.google.com/', 
    'Upgrade-Insecure-Requests': '1'}

    response = requests.get(stock_link,headers=headers)
    soup = BeautifulSoup(response.text,'html.parser')
    e = soup.find('p',{'class':'fs075rem gr'}).get_text().strip().replace(" ","").replace("\n","")[4:].split("|")  
    eq = e[0]   #eq = equity

    if eq.isnumeric() is False:   #its NSE stock
        groww = GROWW(eq)         #object creation for GROWW for chart preparation
        df = []
        def thread1(groww):
            dfresult = groww.df()
            df.append(dfresult)
        t1 = threading.Thread(target=thread1,args=[groww])
        t1.start()
       
        o = GOOGLEFIN(f'{eq}:NSE')
        stock_info_knowledge=[]
        def thread2(o):
            stock_info,stock_knowledge = o.stockinfo()
            if stock_info:
                stock_info_knowledge.append(stock_info)
            else:
                eq = e[1].split(':')[1] 
                o = GOOGLEFIN(f'{eq}:BOM')
                stock_info,stock_knowledge = o.stockinfo()
                stock_info_knowledge.append(stock_info)
                if stock_knowledge:
                    stock_info_knowledge.append(stock_knowledge)
                else:
                    stock_info_knowledge.append('')
                return 
            
            if stock_knowledge:
                stock_info_knowledge.append(stock_knowledge)
            else:
                stock_info_knowledge.append('')
        
        t2 = threading.Thread(target=thread2,args=[o])
        t2.start()
        

        t1.join()
        t2.join()

        df = df[0]
        stock_info = stock_info_knowledge[0]
        stock_knowledge = stock_info_knowledge[1]


        graphHTML = plot(df)   #plot using plotly


    else:                         #BSE stock
        groww = GROWW(eq)         #object creation for GROWW for chart preparation
        df = []
        def thread1(groww):
            dfresult = groww.df()
            df.append(dfresult)
        t1 = threading.Thread(target=thread1,args=[groww])
        t1.start()
       
        o = GOOGLEFIN(f'{eq}:BOM')
        stock_info_knowledge=[]
        def thread2(o):
            stock_info,stock_knowledge = o.stockinfo()
            stock_info_knowledge.append(stock_info)
            if stock_knowledge:
                stock_info_knowledge.append(stock_knowledge)
            else:
                stock_info_knowledge.append('')
        
        t2 = threading.Thread(target=thread2,args=[o])
        t2.start()
        

        t1.join()
        t2.join()

        df = df[0]
        stock_info = stock_info_knowledge[0]
        stock_knowledge = stock_info_knowledge[1]


        graphHTML = plot(df)   #plot using plotly

    return render_template('graph.html', graphHTML=graphHTML,stock_name=stock_name,stock_info=stock_info,stock_knowledge=stock_knowledge)



@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    # Perform search logic here, for simplicity, just filter data based on query
    url = f"https://groww.in/v1/api/search/v3/query/global/st_p_query?page=0&query={query}&size=6&web=true"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com/',
        'Upgrade-Insecure-Requests': '1'}

    results = []
    response = requests.get(url,headers=headers)
    for stock in response.json()['data']['content']:
        results.append(stock)

    # Create a Flask Response object for the search results
    search_response = Response(json.dumps({'results': results}), content_type='application/json')

    # Add headers to prevent caching
    search_response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    search_response.headers['Pragma'] = 'no-cache'
    search_response.headers['Expires'] = '0'

    return search_response


@app.route('/result/<result>')
def result(result):
        print("--------------------------",result)
        eq=result.split('. ')[1]
        print("entered in to result-----------------------,",eq)
        groww = GROWW(eq)         #object creation for GROWW for chart preparation
        df = []
        def thread1(groww):
            dfresult = groww.df()
            df.append(dfresult)
        t3 = threading.Thread(target=thread1,args=[groww])
        t3.start()
       
        o = GOOGLEFIN(f'{eq}:BOM')
        stock_info_knowledge=[]
        def thread2(o):
            stock_info,stock_knowledge = o.stockinfo()
            stock_info_knowledge.append(stock_info)
            if stock_knowledge:
                stock_info_knowledge.append(stock_knowledge)
            else:
                stock_info_knowledge.append('')
        
        t4 = threading.Thread(target=thread2,args=[o])
        t4.start()
        

        t3.join()
        t4.join()

        df = df[0]
        stock_info = stock_info_knowledge[0]
        stock_knowledge = stock_info_knowledge[1]

        stock_name =result.split('. ')[0]
        graphHTML = plot(df)   #plot using plotly

        return render_template('graph.html', graphHTML=graphHTML,stock_name=stock_name,stock_info=stock_info,stock_knowledge=stock_knowledge)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
