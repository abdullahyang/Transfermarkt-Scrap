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

trigger = 1
ppp = pd.read_csv('players.csv')
ppp.set_index('id',drop=True, append=False, inplace=True)
players = ppp.copy()
lpageList = players['page'].tolist()
nlpageList = []
for page in lpageList:
    page = page.replace("profil", "leistungsdaten")
    page = page+"/saison/ges/plus/1#gesamt"
    nlpageList.append(page)

headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
basepage = "https://www.transfermarkt.com"

for page in nlpageList:
    pageSoup = connect(page)
    try:
        total1 = pageSoup.find("table", {"class": "items"}).find("tfoot").find_all("td", {"class": "zentriert"})
        total2 = pageSoup.find("table", {"class": "items"}).find("tfoot").find_all("td", {"class": "rechts"})
        total = []
        for temp in total1:
            total.append(temp.text)
        for temp in total2:
            total.append(temp.text)
        total.remove('Total :')


        id = page.split('/')[page.split('/').index("saison")-1]
        if id == 741295:
            trigger = 1
        if trigger == 0:
            continue
        print(id)
        print(total)
        if players.loc[int(id), 'Position'] != "Goalkeeper":
            players.loc[int(id), 'Appearences'] = total[0]
            players.loc[int(id), 'Goals'] = total[1]
            players.loc[int(id), 'Assists'] = total[2]
            players.loc[int(id), 'Own Goals'] = total[3]
            players.loc[int(id), 'Subtitutions on'] = total[4]
            players.loc[int(id), 'Subtitutions off'] = total[5]
            players.loc[int(id), 'Yellow cards'] = total[6]
            players.loc[int(id), 'Second yellow cards'] = total[7]
            players.loc[int(id), 'Red cards'] = total[8]
            players.loc[int(id), 'Penalty goals'] = total[9]
            players.loc[int(id), 'Minutes per goal'] = total[10]
            players.loc[int(id), 'Minutes played'] = total[11]
        if players.loc[int(id), 'Position'] == "Goalkeeper":
            players.loc[int(id), 'Appearences'] = total[0]
            players.loc[int(id), 'Goals'] = total[1]
            players.loc[int(id), 'Own Goals'] = total[2]
            players.loc[int(id), 'Subtitutions on'] = total[3]
            players.loc[int(id), 'Subtitutions off'] = total[4]
            players.loc[int(id), 'Yellow cards'] = total[5]
            players.loc[int(id), 'Second yellow cards'] = total[6]
            players.loc[int(id), 'Red cards'] = total[7]
            players.loc[int(id), 'Goals conceded'] = total[8]
            players.loc[int(id), 'Clean sheets'] = total[9]
            players.loc[int(id), 'Minutes played'] = total[10]
    except:continue
    #print(players)
    players.to_csv("players1.csv")

