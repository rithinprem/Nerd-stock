import requests
import pandas as pd
import numpy as np
import json



def view_chart_api(script_code):
    l=[]
    url=''
    if script_code.isnumeric() is False:
        print("NSE---------------------",script_code)
        url = f"https://groww.in/v1/api/charting_service/v2/chart/delayed/exchange/NSE/segment/CASH/{script_code}?endTimeInMillis=1714780564504&intervalInMinutes=5&startTimeInMillis=1713119400000"
    else:
        print("BSE---------------------",script_code)
        url = f"https://groww.in/v1/api/charting_service/v2/chart/delayed/exchange/BSE/segment/CASH/{script_code}?endTimeInMillis=1714780564504&intervalInMinutes=5&startTimeInMillis=1713119400000"
    response = requests.get(url)
    print(response)
    response = response.json()
    print(response)
    df = pd.DataFrame(response['candles'],columns=['time','open','high','low','close','volume'])
    df.drop('volume',axis=1,inplace=True)
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
    print(l)
    return l

