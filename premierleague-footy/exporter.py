import requests
import time
import random

from bs4 import BeautifulSoup

from prometheus_client import start_http_server
from prometheus_client.core import  GaugeMetricFamily, REGISTRY

class CustomCollector(object):
    team_data_link = {}
    players_img= {}
    
    def __init__(self):
        url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        headers = {'User-Agent': 'Mozilla/5.0'}
        info = requests.get(url,headers=headers).text

        # Parsing World Cup Links into a data frame
        soup = BeautifulSoup(info, "html.parser")
        #print (soup)
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
            #print (team_name, team_url)
    def _extract_image(self,link,player_name):
        
        #only extract for White, Saka,
        # for others default to https://cdn.britannica.com/68/195168-050-BBAE019A/football.jpg
        players_to_fetch_image = ["Bukayo Saka","Declan Rice", "William Saliba", "Ben White","Aaron Ramsdale"]
        if player_name in players_to_fetch_image:

           url = "https://fbref.com" + link
           headers = {'User-Agent': 'Mozilla/5.0'}
           info = requests.get(url,headers=headers).text
           soup = BeautifulSoup(info, "html.parser")
           div = soup.find("div", id="info")
           img = div.find("img")
           self.players_img [player_name] = img['src'] 
        else:
            self.players_img [player_name] = "https://cdn.britannica.com/68/195168-050-BBAE019A/football.jpg"
        return self.players_img [player_name]
            
        
    def collect(self):
        
        #for club in self.team_data_link.keys():
        club_subset = ['Arsenal']
        for club in club_subset:
            time.sleep(3)
            info = requests.get(self.team_data_link[club]).text
            soup = BeautifulSoup(info, "html.parser")
            table = soup.find("table", id="stats_standard_9")  
            table_body = table.find("tbody")

            rows = table_body.find_all("tr")
            img_extract_count = 0
            for row in rows:
                players_stat = {}
                cells = row.find_all("td")        
                players_stat ["player"] = row.find("th").find('a').contents[0]
                players_stat ["starts"] = cells[3].text or 0
                players_stat ["minutes_played"] = cells[5].text.replace(',','') or 0
                players_stat ["goals_scored"] = cells[7].text or 0
                players_stat ["assists"] = cells[8].text or 0
                player_href = row.find("th").find('a').get('href') 
                
                short_image = ""
                if not (players_stat ["player"] in self.players_img.keys()):
                    if img_extract_count < 4:
                      short_image = self._extract_image (player_href,players_stat ["player"] )
                      img_extract_count = img_extract_count + 1
                else:
                    short_image = self.players_img [players_stat ["player"]] 
                        
             
                player_name = ""
                for data_key in players_stat.keys():
                    if  data_key == "player":
                            player_name = players_stat ["player"] 
                    else :
                            #print(row.find("th").find('a').contents[0], cells[3].text,cells[5].text,cells[6].text,cells[7].text,cells[8].text)
                            gauge = GaugeMetricFamily(data_key, '', labels=['club','player','image'])
                            gauge.add_metric([club,player_name,short_image], players_stat[data_key])
                            yield gauge
                            
        
        for row in rows:
            line = str(row)
            href_line = line[line.find("href=") :]
            team_url = (
                "https://fbref.com"
                + href_line[href_line.find("/") : href_line.find('">')]
            )
            team_name = href_line[href_line.find('">') : href_line.find("</a")][2:]
            self.team_data_link[team_name] = team_url
        
    

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
