import requests
import pandas as pd
import numpy as np


class NSE:
    def __init__(self,stock_link,timeout=10):
        self.stock_link=stock_link
        self.timeout=timeout
        self.url = "https://www.nseindia.com"
        self.__headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
                      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                      'Accept-Language': 'en-US,en;q=0.5',
                      'Connection': 'keep-alive'}
        self.__cookies=None

    def cookies(self):
      try:
        response = requests.get(self.url,headers=self.__headers,timeout=self.timeout)
        self.__cookies = dict(response.cookies)
        return self.__cookies

      except Exception as e:
        return None

    def headers(self):
      return self.__headers

    def link(self):
      return self.stock_link
    

    def df(self,nse):
        response=requests.get(nse.link(),headers=nse.headers(),cookies=nse.cookies())
        df = pd.DataFrame(response.json()['grapthData'])
        if df.empty:
           return None
        df.columns = ['Timestamp','Price']
        df.Timestamp = pd.to_datetime(df.Timestamp,unit='ms')

        return df