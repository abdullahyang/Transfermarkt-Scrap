import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re



def connect(page):
    try:
        pageTree = requests.get(page, headers=headers)
        pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
        return pageSoup
    except:
        print("Problem detected! Wait for 3 seconds...")
        time.sleep(3)
        pageSoup = connect(page)
    return pageSoup


ppp = pd.read_csv('players.csv', usecols=['page'])
lpageList = ppp['page'].tolist()
for page in lpageList:
    page.replace("profil", "marktwertverlauf")

headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
basepage = "https://www.transfermarkt.com"

ValueData = pd.DataFrame(columns=['id', 'Club', 'Age', 'Value', 'Date'])
vcnt = 0
trigger = 0
for page in lpageList:
    pageSoup = connect(page)
    pattern = re.compile(r"Highcharts.setOptions")
    script = str(pageSoup.find("script", text=pattern)).split("\n")
    id = page.split("/")[len(page.split("/"))-1]
    print(id)
    for line in script:
        line = line.strip()
        if line.find("'series':[{'type':'area','name':'Marktwert'") != -1:
            #print(line)
            temp = line.split("'data':")[1].split(",'credits'")[0].split("'")
            print(temp)
            PlayerLines = []
            while '' in temp:
                temp.remove('')
            for tmp in temp:
                ii = tmp.strip()
                PlayerLines.append(ii.replace("\\x20", " ").replace("\\u20AC", ""))
            while '' in PlayerLines:
                PlayerLines.remove('')
            print(PlayerLines)
            while 'verein' in PlayerLines:
                idx = PlayerLines.index("verein")
                club = ""
                age = ""
                value = ""
                date = ""
                club = PlayerLines[PlayerLines.index("verein") + 2]
                age = PlayerLines[idx + 6]
                value = PlayerLines[idx + 10]
                date = PlayerLines[idx + 14]
                PlayerLines[idx] = "okay"
                ValueData.loc[vcnt] = [id, club, age, value, date]
                vcnt = vcnt+1
    ValueData.to_csv("values.csv")


