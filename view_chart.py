import requests
import pandas as pd
import numpy as np
import json
import datetime
from dateutil.relativedelta import relativedelta
from datetime import timezone




def view_chart_api(script_code,timeframe='1d'):
    current_date_time = datetime.datetime.now()
    l=[]
    if script_code.isnumeric() is False:
        segment = 'NSE'
    else:
        segment = 'BSE'

    print("Current-",current_date_time,"Before-",int((current_date_time - datetime.timedelta(days=14)).timestamp()))

    url_1d_5d_1m_3m=[f"https://groww.in/v1/api/charting_service/v2/chart/delayed/exchange/{segment}/segment/CASH/{script_code}?endTimeInMillis={int(current_date_time.timestamp()*1000)}&intervalInMinutes=1&startTimeInMillis={int((current_date_time - datetime.timedelta(days=30)).timestamp()* 1000)}",
                f"https://groww.in/v1/api/charting_service/v2/chart/delayed/exchange/{segment}/segment/CASH/{script_code}?endTimeInMillis={int(current_date_time.timestamp()*1000)}&intervalInMinutes=5&startTimeInMillis={int((current_date_time - datetime.timedelta(days=30)).timestamp()* 1000)}",
                f"https://groww.in/v1/api/charting_service/v2/chart/delayed/exchange/{segment}/segment/CASH/{script_code}?endTimeInMillis={int(current_date_time.timestamp()*1000)}&intervalInMinutes=30&startTimeInMillis={int((current_date_time - relativedelta(years=2)).timestamp()* 1000)}",
                f"https://groww.in/v1/api/charting_service/v2/chart/delayed/exchange/{segment}/segment/CASH/{script_code}?endTimeInMillis={int(current_date_time.timestamp()*1000)}&intervalInMinutes=60&startTimeInMillis={int((current_date_time - relativedelta(months=10)).timestamp()* 1000)}",
                    ]

    if timeframe=='1d':
        url = url_1d_5d_1m_3m[0]
    elif timeframe=='5d':
        url = url_1d_5d_1m_3m[1]
    elif timeframe=='1m':
        url = url_1d_5d_1m_3m[2]
    elif timeframe=='3m':
        url = url_1d_5d_1m_3m[3]


    response = requests.get(url)
    response = response.json()
    df = pd.DataFrame(response['candles'],columns=['time','open','high','low','close','volume'])
    df.drop('volume',axis=1,inplace=True)
    df['time'] = df.time + 19800
    
    def filter(x):
        dic = dict()
        dic['time'] =  int(x['time'])
        dic['open'] = x['open']
        dic['high'] = x['high']
        dic['low'] = x['low']
        dic['close'] = x['close']
        l.append(dic)
        return 

    df.apply(filter,axis=1)

    return l

