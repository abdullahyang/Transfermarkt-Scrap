import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
basepage = "https://www.transfermarkt.com"

# TODO: Set the page of the national team competitions that you want to get as below
cpagelist = ["https://www.transfermarkt.com/weltmeisterschaft-2010/teilnehmer/pokalwettbewerb/WM10/saison_id/2009", "https://www.transfermarkt.com/europameisterschaft-2012/teilnehmer/pokalwettbewerb/EM12/saison_id/2011", "https://www.transfermarkt.com/weltmeisterschaft-2014/teilnehmer/pokalwettbewerb/WM14/saison_id/2013","https://www.transfermarkt.com/europameisterschaft-2016/teilnehmer/pokalwettbewerb/EM16/saison_id/2015", "https://www.transfermarkt.com/weltmeisterschaft-2018/teilnehmer/pokalwettbewerb/WM18/saison_id/2017", "https://www.transfermarkt.com/europameisterschaft-2020/teilnehmer/pokalwettbewerb/EM20/saison_id/2020"]


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

ppp = pd.read_csv('players.csv')
ppp['WM10'] = 0
ppp.set_index('id',drop=True, append=False, inplace=True)
pd = ppp.copy()
for cpage in cpagelist:
    pageSoup = connect(cpage)
    countries = pageSoup.find_all("td", {"class": "links no-border-links hauptlink"})
    year = cpage.split("/")[len(cpage.split("/"))-1]
    cname = cpage.split("/")[len(cpage.split("/"))-3]
    pd[cname] = 0
    npagelist = []
    for country in countries:
        npagelist.append(basepage + country.find("a")["href"] + "?saison_id=" + year)
    for npage in npagelist:
        pageSoup = connect(npage)
        pList = []
        temp = pageSoup.find_all("td", {"class": "posrela"})
        for tmp in temp:
            link = tmp.find("span", {"class": "hide-for-small"}).find("a")["href"]
            pList.append(link.split("/")[len(link.split("/"))-1])
        pList = list(set(pList))
        print(pList)
        for id in pList:
            if int(id) in pd.index.tolist():
                pd.loc[int(id), cname] = 1
pd.to_csv("players.csv")
