import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# TODO: Set the page of the leagues of coaches you want as below
lpageList = ["https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1", "https://www.transfermarkt.com/primera-division/startseite/wettbewerb/ES1", "https://www.transfermarkt.com/1-bundesliga/startseite/wettbewerb/L1", "https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1", "https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1", "https://www.transfermarkt.com/liga-portugal-bwin/startseite/wettbewerb/PO1", "https://www.transfermarkt.com/premier-liga/startseite/wettbewerb/RU1", "https://www.transfermarkt.com/eredivisie/startseite/wettbewerb/NL1", "https://www.transfermarkt.com/super-lig/startseite/wettbewerb/TR1", "https://www.transfermarkt.com/chinese-super-league/startseite/wettbewerb/CSL"]


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




headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
basepage = "https://www.transfermarkt.com"

LeagueData = pd.DataFrame(columns=['League Name', 'League level', 'Number of teams', 'PlayersNo.', 'Foreigners', 'avg-Market value', 'UEFA coefficient', 'avg-Age', 'Total Value', 'page'])
TeamData = pd.DataFrame(columns=['Club Name', 'League', 'Squad size', 'Average age', 'Foreigners', 'National team players', 'Stadium', 'Total Value', 'Current Ranking in League', 'page'])
ManagerData = pd.DataFrame(columns=['Manager Name', 'Club', 'League', 'Birth Date', 'Birth Place', 'Age', 'Citizenship', 'Avg. term as coach', 'Coaching Licence', 'Preferred formation', 'Matches', 'Wins', 'Draws', 'Losses', 'Goals', 'Points', 'PPM', 'page'])
lcnt = 0
tcnt = 0
mcnt = 0
for page in lpageList:
    pageSoup = connect(page)
    LeagueName = pageSoup.find("h1", {"class": "spielername-profil"}).text
    pheader = pageSoup.find_all("table", {"class": "profilheader"})
    LeagueInfo = pheader[0].text+pheader[1].text
    ll = LeagueInfo.split("\n")
    LeagueLines = []
    while '' in ll:
        ll.remove('')
    for i in ll:
        ii = i.strip()
        LeagueLines.append(ii.replace("\xa0"," "))
    while '' in LeagueLines:
        LeagueLines.remove('')
    print(LeagueLines)
    print(LeagueName)
    TotalValue = pageSoup.find("div", {"class": "marktwert"}).find("a").text
    LeagueData.loc[lcnt]=[LeagueName, LeagueLines[1], LeagueLines[3], LeagueLines[5], LeagueLines[7], LeagueLines[9].strip("€"), LeagueLines[11], LeagueLines[15], TotalValue.strip("€"), page]
    lcnt = lcnt+1
    tpageList = []
    temp = pageSoup.find("table", {"class": "items"}).find("tbody").find_all("td", {"class": "zentriert no-border-rechts"})
    for tmp in temp:
        tpageList.append(basepage+tmp.find("a")["href"])
    for tpage in tpageList:
        pageSoup = connect(tpage)
        TeamName = pageSoup.find("h1", {"itemprop": "name"}).text.strip()
        if TeamName == "CD Santa Clara":
            trigger = 1
        if trigger == 0:
            continue
        temp = pageSoup.find("div", {"class": "dataBottom"}).text.split("\n")
        TeamLines = []
        while '' in temp:
            temp.remove('')
        for tmp in temp:
            ii = tmp.strip()
            TeamLines.append(ii.replace("\xa0", " ").strip("€"))
        while '' in TeamLines:
            TeamLines.remove('')
        print(TeamLines)
        tTotalValue = pageSoup.find("div", {"class": "dataMarktwert"}).find("a").text.split()[0].strip("€")
        tRanking = pageSoup.find("div", {"class": "dataZusatzDaten"}).find("span", {"class": "dataValue"}).text.strip()
        print(tRanking)
        TeamData.loc[tcnt] = [TeamName, LeagueName, TeamLines[1], TeamLines[3], TeamLines[5], TeamLines[7], TeamLines[9], tTotalValue, tRanking, tpage]
        tcnt = tcnt + 1
        TeamData.to_csv("teams1.csv")
        temp = pageSoup.find("div", {"class": "box box-slider viewport-tracking", "data-viewport": "Mitarbeiter"})
        if temp.find("b", {"itemprop": "jobTitle"}).text == "Manager" or "Caretaker Manager":
            cpage = basepage + temp.find("a")["href"]
        pageSoup = connect(cpage)
        temp = pageSoup.find("table", {"class": "auflistung"}).text.strip().split("\n")
        mpage = cpage
        ManagerLines = []
        while '' in temp:
            temp.remove('')
        for tmp in temp:
            ii = tmp.strip()
            ManagerLines.append(ii.replace("\xa0", " ").strip("€"))
        while '' in ManagerLines:
            ManagerLines.remove('')
        print(ManagerLines)
        ManagerName = pageSoup.find("h1", {"itemprop": "name"}).text
        mclub = pageSoup.find("span", {"itemprop": "affiliation"}).find("a")["title"]
        mleague = ""
        if mclub != "Without Club":
            mleague = pageSoup.find("div", {"class": "dataZusatzDaten"}).find("span", {"class": "dataValue"}).text.strip()
        mbd = ""
        if ManagerLines.count("Date of Birth:") > 0:
            mbd = ManagerLines[ManagerLines.index("Date of Birth:") + 1]
        mbp = ""
        if ManagerLines.count("Place of Birth:") > 0:
            mbp = ManagerLines[ManagerLines.index("Place of Birth:") + 1]
        mage = ""
        if ManagerLines.count("Age:") > 0:
            mage = ManagerLines[ManagerLines.index("Age:") + 1]
        mctz = ""
        if ManagerLines.count("Citizenship:") > 0:
            mctz = ManagerLines[ManagerLines.index("Citizenship:") + 1]
        matac = ""
        if ManagerLines.count("Avg. term as coach:") > 0:
            matac = ManagerLines[ManagerLines.index("Avg. term as coach:") + 1]
        mcl = ""
        if ManagerLines.count("Coaching Licence:") > 0:
            mcl = ManagerLines[ManagerLines.index("Coaching Licence:") + 1]
        mpf = ""
        if ManagerLines.count("Preferred formation:") > 0:
            mpf = ManagerLines[ManagerLines.index("Preferred formation:") + 1]
        cpage = cpage.replace("profil", "leistungsdatenDetail")
        pageSoup = connect(cpage)
        mres = ["","","","","","",""]
        if len(pageSoup.find_all("div", {"class": "large-4 columns"})) > 0:
                if pageSoup.find("div", {"class": "large-4 columns"}).find("tbody").text.strip().split("\n")[0] != "0":
                    mres = pageSoup.find("div", {"class": "large-4 columns"}).find("tbody").text.strip().split("\n")
        ManagerData.loc[mcnt] = [ManagerName, mclub, mleague, mbd, mbp, mage, mctz, matac, mcl, mpf, mres[0], mres[1], mres[2], mres[3], mres[4], mres[5], mres[6], mpage]
        mcnt = mcnt+1
        ManagerData.to_csv("managers.csv")
    LeagueData.to_csv("leagues.csv")


