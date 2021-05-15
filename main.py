import requests,argparse,schedule,time

BaseURL = "https://www.pixiv.net/en/artworks/"
ProxyURL = "https://cdn.humanz.moe/pixiv/?pixivURL="

class PixivLewd:
    """
    docstring
    """
    def __init__(self,Session,Tag):
        self.Session = Session
        self.Tag = Tag.split(",")
        self.ListLewd = []
        print("Lewd tags: ", Tag)
        
    def AddWebhook(self,hook):
        self.WebHook = hook

    def GetLewdFist(self):
        for Tag in self.Tag:
            req = requests.get("https://www.pixiv.net/ajax/search/artworks/" + Tag + "?word=" + Tag + "&order=date_d&mode=r18&p=1&s_mode=s_tag&type=all&lang=en",headers=GetHeaders(self.Session))
            data = req.json()
            for PixivID in data['body']['illustManga']['data']:
                self.ListLewd.append(PixivID['id'])
    def CheckLewd(self):
        """
        docstring
        """
        for Tag in self.Tag:
            req = requests.get("https://www.pixiv.net/ajax/search/artworks/" + Tag + "?word=" + Tag + "&order=date_d&mode=r18&p=1&s_mode=s_tag&type=all&lang=en",headers=GetHeaders(self.Session))
            data = req.json()
            for PixivID in data['body']['illustManga']['data']:
                if PixivID['id'] not in PixivID:
                    print("New fanart "+BaseURL+PixivID['id'])
                    self.ListLewd.append(PixivID['id'])
                    if self.WebHook != None:
                        Payload = {
                        "avatar_url": ProxyURL+PixivID["profileImageUrl"],
                          "embeds": [
                                {
                                "title": PixivID["title"],
                                "url": BaseURL+PixivID["id"],
                                "author": {
                                    "name": PixivID["userName"],
                                    "icon_url": ProxyURL+PixivID["profileImageUrl"]
                                },
                                "image": {
                                    "url": ProxyURL+PixivID["url"]
                                }
                                }
                            ]
                        }
                        result = requests.post(self.WebHook,json=Payload)
                        try:
                            result.raise_for_status()
                        except requests.exceptions.HTTPError as err:
                            print(err)
                        else:
                            print("Payload delivered successfully, code {}.".format(result.status_code))                        
                        

        
def GetHeaders(s :str):
    palabapakkau = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
        'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'Accept-Language':'en-US,en;q=0.5',
        'Dnt':'1',
        'Upgrade-Insecure-Requests':'1',
        'Connection':'keep-alive',
        'Cookie': 'PHPSESSID='+s,
        'Cache-Control': 'max-age=0',
        'Te':'Trailers'
    }
    return palabapakkau   


def main():
    parser = argparse.ArgumentParser(description='Pixi Lewd RSS')
    parser.add_argument('-s','--Session', required=True,help="Pixivi SessionID")
    parser.add_argument('-t','--Tag',required=True,help="Pixiv tag(separated by commas)")
    parser.add_argument('-w','--Webhook',help="Discord webhook")
    args = parser.parse_args()
    Lewd = PixivLewd(args.Session,args.Tag)
    if args.Webhook != "":
        Lewd.AddWebhook(args.Webhook)

    Lewd.GetLewdFist()
    schedule.every(1).hours.do(Lewd.CheckLewd)
    while True:
        schedule.run_pending()
        time.sleep(1)
main()   