import requests
from bs4 import BeautifulSoup
import json
import re

class GOOGLEFIN:

    def __init__(self,stock_name):
        self.stock_name=stock_name
        self.url = f"https://www.google.com/finance/quote/{stock_name}"
        self.__headers={'accept':'*/*',
                        'accept-language':'en-US,en;q=0.9',
                        'sec-ch-ua':'"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                        }

    def stockinfo(self):
        response = requests.get(self.url,headers=self.__headers)
        soup = BeautifulSoup(response.text,'html.parser')
        df=[]
        for tr in soup.find_all('div',{'class':'P6K39c'}):
            df.append(tr.get_text())
        columns = ['Previous Close','Day Range','Year Range','Market Cap','Avg Volume','P/E Ratio','Dividend Yeild','Primary Exchange']
        data=json.dumps(dict(zip(columns,df)))
        json_object = json.loads(data)
        try:
            stock_knowledge =    soup.find('div',{'class':"bLLb2d"}).get_text()[:-10]
        except Exception as e:
            stock_knowledge=""

        try:
          current_price = soup.find('div',{'class':'YMlKec fxKbKc'}).get_text()
          current_price = float(re.sub('[^0-9.]', '', current_price))
        except Exception as e:
          current_price = ''

        return json_object,stock_knowledge,current_price
    

   
        
