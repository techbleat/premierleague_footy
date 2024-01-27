import requests
import time
import random

from bs4 import BeautifulSoup

from prometheus_client import start_http_server
from prometheus_client.core import  GaugeMetricFamily, REGISTRY

class CustomCollector(object):
    team_data_link = {}
    
    def __init__(self):
        url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        headers = {'User-Agent': 'Mozilla/5.0'}
        info = requests.get(url,headers=headers).text

        # Parsing World Cup Links into a data frame
        soup = BeautifulSoup(info, "html.parser")
        print (soup)
        table = soup.find("table", id="results2023-202491_overall")
        table_body = table.find("tbody")
        rows = table_body.find_all("tr")
        
        for row in rows:
            line = str(row)
            href_line = line[line.find("href=") :]
            team_url = (
                "https://fbref.com"
                + href_line[href_line.find("/") : href_line.find('">')]
            )
            team_name = href_line[href_line.find('">') : href_line.find("</a")][2:]
            self.team_data_link[team_name] = team_url
            print (team_name, team_url)
     
    def collect(self):
        
        #for club in self.team_data_link.keys():
        liverpool = ["Liverpool", 'Arsenal']
        for club in liverpool:
            time.sleep(3)
            info = requests.get(self.team_data_link[club]).text
            soup = BeautifulSoup(info, "html.parser")
            table = soup.find("table", id="stats_standard_9")
            table_body = table.find("tbody")

            rows = table_body.find_all("tr")
            for row in rows:
                players_stat = {}
                cells = row.find_all("td")

                players_stat ["player"] = row.find("th").find('a').contents[0]
                players_stat ["starts"] = cells[3].text or 0
                players_stat ["minutes_played"] = cells[5].text.replace(',','') or 0
                players_stat ["goals_scored"] = cells[7].text or 0
                players_stat ["assists"] = cells[8].text or 0
                
                player_name = ""
                for data_key in players_stat.keys():
                    if  data_key == "player":
                            player_name = players_stat ["player"] 
                    else :
                            #print(row.find("th").find('a').contents[0], cells[3].text,cells[5].text,cells[6].text,cells[7].text,cells[8].text)
                            gauge = GaugeMetricFamily(data_key, '', labels=['club',"name"])
                            gauge.add_metric([club,player_name], players_stat[data_key])
                            yield gauge

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    try:
        REGISTRY.register(CustomCollector())
    except TypeError:
        print("Error")
    start_http_server(8000)
    while True:
        #main()
        time.sleep(random.randrange(1,10))
