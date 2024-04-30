import numpy as np
import pandas as pd
import json
import requests
from pytz import timezone



class GROWW:
    def __init__(self,eq):
        self.eq=eq
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
                      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                      'Accept-Language': 'en-US,en;q=0.5',
                      'Connection': 'keep-alive'}
        
    def df(self):
        if self.eq.isnumeric() is False:
            url = f"https://groww.in/v1/api/charting_service/v2/chart/delayed/exchange/NSE/segment/CASH/{self.eq}/daily?intervalInMinutes=1&minimal=true"
            data=requests.get(url,headers=self.headers)
            data = data.json()['candles']
            df = pd.DataFrame(data,columns=['Timestamp','Price'])
            df.Timestamp = pd.to_datetime([entry[0] for entry in data], unit='s', utc=True).tz_convert('Asia/Kolkata')

        else:
            url = f"https://groww.in/v1/api/charting_service/v2/chart/delayed/exchange/BSE/segment/CASH/{self.eq}/daily?intervalInMinutes=1&minimal=true"
            data=requests.get(url,headers=self.headers)
            data = data.json()['candles']
            df = pd.DataFrame(data,columns=['Timestamp','Price'])
            df.Timestamp = pd.to_datetime([entry[0] for entry in data], unit='s', utc=True).tz_convert('Asia/Kolkata')

        return df



    
    