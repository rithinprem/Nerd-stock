import requests
import brotli

query = "info"

url = f"https://groww.in/v1/api/search/v3/query/global/st_p_query?page=0&query={query}&size=6&web=true"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Referer': 'https://www.google.com/',
    'Upgrade-Insecure-Requests': '1'
}

results = []
response = requests.get(url,headers=headers)
for stock in response.json()['data']['content']:
	results.append(stock['search_id'])

print(results)