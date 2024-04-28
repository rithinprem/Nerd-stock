import requests
import pandas as pd
import numpy as np
import json


class BSE:
    def __init__(self,stock_link,timeout=10):
        self.stock_link=stock_link
        self.timeout=timeout
        self.__headers={'accept':'*/*',
                        'accept-language':'en-US,en;q=0.9',
                        'origin':'https://www.bseindia.com',
                        'referer':'https://www.bseindia.com/',
                        'sec-ch-ua':'"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                        }

    def headers(self):
      return self.__headers

    def link(self):
      return self.stock_link
    

    def df(self,bse):
        response=requests.get(bse.link(),headers=bse.headers())
        print(bse.link())
        dic = response.json()['Data']
        dic = json.loads(dic)
        df = pd.DataFrame(dic)
        df.drop('vole',axis=1,inplace=True)
        df.dttm = pd.to_datetime(df.dttm)
        df.vale1 = pd.to_numeric(df.vale1,errors='coerce')
        df.columns=['Timestamp','Price']

        return df
    

