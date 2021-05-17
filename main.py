import requests,argparse,time,sqlite3

BaseURL = "https://www.pixiv.net/en/artworks/"
UserURL = "https://www.pixiv.net/en/users/"
ProxyURL = "https://cdn.humanz.moe/pixiv/?pixivURL="
PixivIDList = {}

class PixivLewd:
    """
    docstring
    """
    def __init__(self,Session,Tag):
        self.Session = Session
        self.Tag = Tag.split(",")
        self.Ignore = None
        self.NiggerList = None
        self.WebHook = None

        print("Lewd tags: ", Tag)
        
    def AddWebhook(self,hook):
        print("Add discord webhook",hook)
        self.WebHook = hook

    def AddBlackList(self,nigger):
        self.NiggerList = nigger.lower().split(",")
        print("Add Nigg list",self.NiggerList)

    def AddSkip(self,skip):
        self.Ignore = skip.split(",")
        print("Ignore some hashtag",self.Ignore)

    def GetLewdFist(self):
        for Tag in self.Tag:
            PixivIDList[Tag] = []
            req = requests.get("https://www.pixiv.net/ajax/search/artworks/" + Tag + "?word=" + Tag + "&order=date_d&mode=r18&p=1&s_mode=s_tag&type=all&lang=en",headers=GetHeaders(self.Session))
            data = req.json()
            for PixivID in data['body']['illustManga']['data']:         
                PixivIDList[Tag].append(PixivID['id'])

    def IllustDetail(self,id):
        req = requests.get("https://www.pixiv.net/ajax/illust/"+id,headers=GetHeaders(self.Session))
        data = req.json()        
        return data["body"]

    def CheckLewd(self):
        """
        docstring
        """
        for Tag in self.Tag:
            print("Check "+Tag+" Lewd")
            req = requests.get("https://www.pixiv.net/ajax/search/artworks/" + Tag + "?word=" + Tag + "&order=date_d&mode=r18&p=1&s_mode=s_tag&type=all&lang=en",headers=GetHeaders(self.Session))
            data = req.json()
            for PixivID in data['body']['illustManga']['data']:
                if self.NiggerList != None:
                    for Nigg in self.NiggerList:
                        if Nigg.lower() == PixivID["userName"].lower():
                            print("Bann Arts "+PixivID['id'])
                            continue

                if self.Ignore != None:
                    for skp in self.Ignore:
                        if skp in PixivID['tags']:
                            print("Skip lur "+PixivID['id'])
                            continue
            
                if PixivID['id'] not in PixivIDList[Tag]:
                    print("New fanart "+BaseURL+PixivID['id'])
                    PixivIDList[Tag].append(PixivID['id'])
                    del PixivIDList[Tag][0]
                    IllustData = self.IllustDetail(PixivID['id'])                    
                    if self.WebHook != None:
                        Payload = {
                        "avatar_url": ProxyURL+PixivID["profileImageUrl"],
                          "embeds": [
                                {
                                "title": PixivID["title"],
                                "url": BaseURL+PixivID["id"],
                                "author": {
                                    "name": PixivID["userName"],
                                    "url": UserURL+IllustData['userId'],
                                    "icon_url": ProxyURL+PixivID["profileImageUrl"]
                                },
                                "image": {
                                    "url": ProxyURL+IllustData["urls"]["regular"]
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
    parser.add_argument('-b','--Banned',help="Ignore artis fanart(separated by commas)")
    parser.add_argument('-i','--Ignore',help="Skip hashtag(separated by commas)")
    args = parser.parse_args()
    Lewd = PixivLewd(args.Session,args.Tag)
    if args.Webhook != None:
        Lewd.AddWebhook(args.Webhook)
    if args.Banned != None:
        Lewd.AddBlackList(args.Banned)
    if args.Ignore != None:
        Lewd.AddSkip(args.Ignore)

    Lewd.GetLewdFist()
    while True:
        Lewd.CheckLewd()
        time.sleep(60)

main()   