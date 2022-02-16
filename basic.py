import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
basepage = "https://www.transfermarkt.com"

# TODO: Set the page of the leagues that you want to get as below
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

LeagueData = pd.DataFrame(columns=['League Name', 'League level', 'Number of teams', 'PlayersNo.', 'Foreigners', 'avg-Market value', 'UEFA coefficient', 'avg-Age', 'Total Value', 'page'])
TeamData = pd.DataFrame(columns=['Club Name', 'League', 'Squad size', 'Average age', 'Foreigners', 'National team players', 'Stadium', 'Total Value', 'Current Ranking in League', 'page', 'id'])
TeamData.set_index('id',drop=True, append=False, inplace=True)
PlayerData = pd.DataFrame(columns=['Player Name', 'Club', 'League', 'Birth Date', 'Birth Place', 'Age', 'Height', 'Citizenship', 'Position', 'Foot', 'Player agent', 'Joined Date', 'Contract expires', 'Last contract extension', 'Outfitter', 'Value', 'page', 'id'])
PlayerData.set_index('id',drop=True, append=False, inplace=True)
ManagerData = pd.DataFrame(columns=['Manager Name', 'Club', 'League', 'Birth Date', 'Birth Place', 'Age', 'Citizenship', 'Avg. term as coach', 'Coaching Licence', 'Preferred formation', 'Matches', 'Wins', 'Draws', 'Losses', 'Goals', 'Points', 'PPM', 'page', 'id'])
ManagerData.set_index('id',drop=True, append=False, inplace=True)
lcnt = 0
tcnt = 0
pcnt = 0
mcnt = 0
trigger = 1
for page in lpageList:
    pageSoup = connect(page)
    LeagueName = pageSoup.find("h1", {"class": "spielername-profil"}).text
    if LeagueName == "":
        continue
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
        if TeamName == "Hebei FC":
            trigger = 1
        if trigger == 0:
            continue
        tid = tpage.split("/")[tpage.split("/").index("verein")+1].split("?")[0]
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
        TeamData.loc[tid] = [TeamName, LeagueName, TeamLines[1], TeamLines[3], TeamLines[5], TeamLines[7], TeamLines[9], tTotalValue, tRanking, tpage]
        tcnt = tcnt + 1
        TeamData.to_csv("teams1.csv")

        temp = pageSoup.find("div", {"class": "box box-slider viewport-tracking", "data-viewport": "Mitarbeiter"})
        if temp.find("b", {"itemprop": "jobTitle"}).text == "Manager" or "Caretaker Manager":
            cpage = basepage + temp.find("a")["href"]
        mpageSoup = connect(cpage)
        temp = mpageSoup.find("table", {"class": "auflistung"}).text.strip().split("\n")
        mpage = cpage
        mid = mpage.split("/")[mpage.split("/").index("trainer") + 1].split("?")[0]
        ManagerLines = []
        while '' in temp:
            temp.remove('')
        for tmp in temp:
            ii = tmp.strip()
            ManagerLines.append(ii.replace("\xa0", " ").strip("€"))
        while '' in ManagerLines:
            ManagerLines.remove('')
        print(ManagerLines)
        ManagerName = mpageSoup.find("h1", {"itemprop": "name"}).text
        mclub = mpageSoup.find("span", {"itemprop": "affiliation"}).find("a")["title"]
        mleague = ""
        if mclub != "Without Club":
            mleague = mpageSoup.find("div", {"class": "dataZusatzDaten"}).find("span",
                                                                              {"class": "dataValue"}).text.strip()
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
        mpageSoup = connect(cpage)
        mres = ["", "", "", "", "", "", ""]
        if len(mpageSoup.find_all("div", {"class": "large-4 columns"})) > 0:
            if mpageSoup.find("div", {"class": "large-4 columns"}).find("tbody").text.strip().split("\n")[0] != "0":
                mres = mpageSoup.find("div", {"class": "large-4 columns"}).find("tbody").text.strip().split("\n")
        ManagerData.loc[mid] = [ManagerName, mclub, mleague, mbd, mbp, mage, mctz, matac, mcl, mpf, mres[0], mres[1],
                                 mres[2], mres[3], mres[4], mres[5], mres[6], mpage]
        mcnt = mcnt + 1
        ManagerData.to_csv("managers1.csv")

        temp = pageSoup.find("table", {"class": "items"}).find("tbody").find_all("div", {
            "class": "di nowrap"})
        ppageList = []
        for tmp in temp:
            ppageList.append(basepage + tmp.find("a")["href"])
        ppageList = list(set(ppageList))
        print(ppageList)
        for ppage in ppageList:
            pageSoup = connect(ppage)
            #print(pageSoup)
            temp = pageSoup.select_one('div.info-table.info-table--right-space').text.split("\n")
            pid = ppage.split("/")[ppage.split("/").index("spieler") + 1].split("?")[0]
            PlayerLines = []
            while '' in temp:
                temp.remove('')
            for tmp in temp:
                ii = tmp.strip()
                PlayerLines.append(ii.replace("\xa0", " ").strip("€"))
            while '' in PlayerLines:
                PlayerLines.remove('')
            PlayerName = pageSoup.find("h1", {"itemprop": "name"}).text.strip()
            print(PlayerLines)

            pclub = ""
            if PlayerLines.count("Current club:") > 0:
                pclub = PlayerLines[PlayerLines.index("Current club:") + 1]
            pleague = ""
            if len(pageSoup.find_all("span", {"class": "mediumpunkt"})) > 0:
                pleague = pageSoup.find("span", {"class": "mediumpunkt"}).text.strip()
            pbd = ""
            if PlayerLines.count("Date of birth:")>0:
                pbd = PlayerLines[PlayerLines.index("Date of birth:")+1]
            pbp = ""
            if PlayerLines.count("Place of birth:") > 0:
                pbp = PlayerLines[PlayerLines.index("Place of birth:") + 1]
            p_age = PlayerLines[PlayerLines.index("Age:") + 1]
            pht = ""
            if PlayerLines.count("Height:") > 0:
                pht = PlayerLines[PlayerLines.index("Height:") + 1]
            pctz = ""
            if PlayerLines.count("Citizenship:") > 0:
                pctz = PlayerLines[PlayerLines.index("Citizenship:") + 1]

            ppos = ""
            if PlayerLines.count("Position:") > 0:
                ppos = PlayerLines[PlayerLines.index("Position:") + 1]
            pft = ""
            if PlayerLines.count("Foot:") > 0:
                pft = PlayerLines[PlayerLines.index("Foot:") + 1]
            pagt = ""
            if PlayerLines.count("Player agent:") > 0:
                pagt = PlayerLines[PlayerLines.index("Player agent:") + 1]
            pjd = ""
            if PlayerLines.count("Joined:") > 0:
                pjd = PlayerLines[PlayerLines.index("Joined:") + 1]
            pce = ""
            if PlayerLines.count("Contract expires:") > 0:
                pce = PlayerLines[PlayerLines.index("Contract expires:") + 1]
            plce = ""
            if PlayerLines.count("Date of last contract extension:") > 0:
                plce = PlayerLines[PlayerLines.index("Date of last contract extension:") + 1]
            poft = ""
            if PlayerLines.count("Outfitter:") > 0:
                poft = PlayerLines[PlayerLines.index("Outfitter:") + 1]
            pvalue = ""
            if len(pageSoup.find_all("div", {"class": "dataMarktwert"})) > 0:
                pvalue = pageSoup.find("div", {"class": "dataMarktwert"}).find("a").text.split()[0].strip("€")
            PlayerData.loc[pid] = [PlayerName, pclub, pleague, pbd, pbp, p_age, pht, pctz, ppos, pft, pagt, pjd, pce, plce, poft, pvalue, ppage]
            pcnt = pcnt + 1
            PlayerData.to_csv("players.csv")
    LeagueData.to_csv("leagues.csv")


