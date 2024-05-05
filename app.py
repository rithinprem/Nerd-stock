from flask import Flask, render_template,request,Response,abort
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures   #multithreading
import threading
import re


#internal imports
from GROWW import GROWW
from GOOGLEFIN import GOOGLEFIN
from graph import plot
from view_chart import view_chart_api



app = Flask(__name__)
blocked_user_agents = ["Go-http-client/1.1"]

@app.before_request
def block_user_agent():
    user_agent = request.headers.get('User-Agent')
    if user_agent in blocked_user_agents:
        abort(403)

json_object = None #for search when user clicks view stock 
data = dict() #for week_month_year_pentyear chart --threading
script_code = dict()

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
    df['Date'] = df['Date'].dt.strftime('%d-%b-%Y')
    df.Date = df.Date.astype('str')
    df=df.reset_index()
    df.drop('index',axis=1,inplace=True)
    df['stock_id'] = df.index
    json_string = df[:150].to_json(orient='records')
    json_object = json.loads(json_string)

    
    return render_template('index.html', data=json_object)


@app.route('/stock/<stock_id>')
def stock_details(stock_id):
    global script_code
    global data
    global script_code
    script_code.clear()
    data.clear()
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

    price_details = []
    if eq.isnumeric() is False:
        o = GOOGLEFIN(f'{eq}:NSE')
        stock_info_knowledge=[]
        stock_info,stock_knowledge,current_price = o.stockinfo()
        price_details.append(current_price)
        if not stock_info:
            print("BSE stock",e)
            eq = e[1].split(':')[1]
            price_details = []
            o = GOOGLEFIN(f'{eq}:BOM')
            stock_info_knowledge=[]
            stock_info,stock_knowledge,current_price = o.stockinfo()
            price_details.append(current_price)
    else:
        price_details = []
        o = GOOGLEFIN(f'{eq}:BOM')
        stock_info_knowledge=[]
        stock_info,stock_knowledge,current_price = o.stockinfo()
        price_details.append(current_price)


    Previous_Close = stock_info['Previous Close']
    price_details.append(float(re.sub('[^0-9.]', '', Previous_Close)))

    stock_info_knowledge.append(stock_info)
    if stock_knowledge:
        stock_info_knowledge.append(stock_knowledge)
    else:
        stock_info_knowledge.append('')

    if eq.isnumeric():        #BSE
        script_code['BSE']=eq
    else:                     #NSE
        script_code['NSE']=eq

    groww = GROWW(eq)         #object creation for GROWW for chart preparation
    df= groww.df()
    data['daily'] = df
    def target_function(groww):
        global data
        result = groww.df_week_month_year_pentyear()
        data.update(result)

    t = threading.Thread(target=target_function,args=[groww])
    t.start()
    t.join()
    print(data)

    
    stock_info = stock_info_knowledge[0]
    stock_knowledge = stock_info_knowledge[1]
    current_price = price_details[0]
    previous_price = price_details[1]
    day_change = str(abs(round((current_price - previous_price)/previous_price*100,2)))+"%"
    flag = (1 if (current_price-previous_price)>0 else -1)  #whether stock change is negative or positive
    data['flag_daily'] = flag
    script_code["stock_name"] = stock_name

    # print("Current price",current_price)
    # print("Previous price",previous_price)
    # print("Day change",day_change)
    # print(stock_knowledge)


    graphHTML =  plot(df,flag)   #plot using plotly

    return render_template('graph.html', graphHTML=graphHTML,stock_name=stock_name,stock_info=stock_info,stock_knowledge=stock_knowledge,current_price=current_price,day_change=day_change,flag=flag,script_code=script_code)



@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    # Perform search logic here, for simplicity, just filter data based on query
    url = f"https://groww.in/v1/api/search/v3/query/global/st_p_query?page=0&query={query}&size=6&web=true"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
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
        global data
        global script_code
        script_code.clear()
        data.clear()
        flag_nse = True
        price_details = []
        eq = result.split("|")[2]
        o = GOOGLEFIN(f'{eq}:NSE')
        stock_info_knowledge=[]
        stock_info,stock_knowledge,current_price = o.stockinfo()
        price_details.append(current_price)
        if not stock_info:
          price_details = []
          flag_nse = False
          eq = result.split("|")[1]
          o = GOOGLEFIN(f'{eq}:BOM')
          stock_info_knowledge=[]
          stock_info,stock_knowledge,current_price = o.stockinfo()
          price_details.append(current_price)


        Previous_Close = stock_info['Previous Close']
        price_details.append(float(re.sub('[^0-9.]', '', Previous_Close)))

        stock_info_knowledge.append(stock_info)
        if stock_knowledge:
            stock_info_knowledge.append(stock_knowledge)
        else:
            stock_info_knowledge.append('')

        eq=(result.split('|')[2] if flag_nse else result.split('|')[1])

        if eq.isnumeric():        #BSE
            script_code['BSE']=eq
        else:                     #NSE
            script_code['NSE']=eq

        groww = GROWW(eq)         #object creation for GROWW for chart preparation
        df= groww.df()

        data['daily'] = df
        def target_function(groww):
            global data
            result = groww.df_week_month_year_pentyear()
            data.update(result)

        t = threading.Thread(target=target_function,args=[groww])
        t.start()
        

        
        stock_info = stock_info_knowledge[0]
        stock_knowledge = stock_info_knowledge[1]
        current_price = price_details[0]
        previous_price = price_details[1]
        day_change = str(abs(round((current_price - previous_price)/previous_price*100,2)))+"%"
        flag = (1 if (current_price-previous_price)>0 else -1)  #whether stock change is negative or positive
        data['flag_daily']=flag

        # print("Current price",current_price)
        # print("Previous price",previous_price)
        # print("Day change",day_change)
        # print(stock_knowledge)

        stock_name = result.split("|")[0]
        script_code["stock_name"] = stock_name


        graphHTML =  plot(df,flag)   #plot using plotly

        return render_template('graph.html', graphHTML=graphHTML,stock_name=stock_name,stock_info=stock_info,stock_knowledge=stock_knowledge,current_price=current_price,day_change=day_change,flag=flag,script_code=script_code)

    

@app.route('/get-data', methods=['GET'])
def get_data():
    global data
    # Get the 'timeframe' from the query string
    timeframe = request.args.get('timeframe', 'default')  # Default value if 'timeframe' not provided
    if timeframe == 'daily':
        result = plot(data['daily'],flag=data['flag_daily'])
    elif timeframe == 'weekly':
        df = data['weekly']
        flag = (1 if (df.tail(1).Price.values[0] - df[0:1].Price.values[0])>0 else -1)
        print("Flag--------------------",flag)
        print("Start Price-------------",df[0:1].Price.values[0])
        print("End Price-------------",df.tail(1).Price.values[0])

        result = plot(df,flag,timeframe)
    elif timeframe == 'monthly':
        df = data['monthly']
        flag = (1 if (df.tail(1).Price.values[0] - df[0:1].Price.values[0])>0 else -1)
        result = plot(df,flag,timeframe)
    elif timeframe == '1y':
        df = data['1y']
        flag = (1 if (df.tail(1).Price.values[0] - df[0:1].Price.values[0])>0 else -1)
        result = plot(df,flag,timeframe)
    else:
        df = data['5y']
        flag = (1 if (df.tail(1).Price.values[0] - df[0:1].Price.values[0])>0 else -1)
        result = plot(df,flag,timeframe)

    # Return data as a simple response
    return result


@app.route("/view_chart/<scriptcode>")
def view_chart(scriptcode):
    global script_code
    stock_name = script_code["stock_name"]
    response = view_chart_api(scriptcode)
    return render_template('view_chart.html',view_chart_api_result = response,stock_name=stock_name)


if __name__ == '__main__':
    app.run(debug=True,host='192.168.29.170')
