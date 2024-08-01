import requests,argparse,time,sqlite3

BaseURL = "https://www.pixiv.net/en/artworks/"
UserURL = "https://www.pixiv.net/en/users/"
ProxyURL = "https://storage.humanz.moe/pixiv/?pixivURL="

CreateDB = """
CREATE TABLE IF NOT EXISTS "Pixiv" (
	"id"	INTEGER NOT NULL,
	"IlustID"	TEXT NOT NULL,
	"AuthorID"	TEXT NOT NULL,
	"PicURL"	TEXT NOT NULL,
	"Hashtag"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);"""
class PixivLewd:
    """
    docstring
    """
    def __init__(self,Session,Tag):
        self.Session = Session
        self.Tag = Tag.split(",")
        self.SqlConn = sqlite3.connect('./Pixiv.sql')
        self.Ignore = None
        self.NiggerList = None
        self.WebHook = None
        self.BannedList = []
        Conn = self.SqlConn.cursor()
        Conn.execute(CreateDB)
        self.SqlConn.commit()

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
        self.SqlCursor = self.SqlConn.cursor()
        for Tag in self.Tag:
            req = requests.get("https://www.pixiv.net/ajax/search/artworks/" + Tag + "?word=" + Tag + "&order=date_d&mode=r18&p=1&s_mode=s_tag&type=all&lang=en",headers=GetHeaders(self.Session))
            data = req.json()
            for PixivID in data['body']['illustManga']['data']:   
                self.SqlCursor.execute("select id from Pixiv where IlustID=:PixivID",{"PixivID": PixivID['id']})
                result  = self.SqlCursor.fetchall()
                if len(result) == 0:                
                    IllustData = self.IllustDetail(PixivID['id'])
                    self.SqlCursor.execute("insert into Pixiv values (?,?,?,?,?)", (None,PixivID["id"],IllustData['userId'],IllustData["urls"]["original"],Tag))      
        self.SqlConn.commit()

    def IllustDetail(self,id):
        req = requests.get("https://www.pixiv.net/ajax/illust/"+id,headers=GetHeaders(self.Session))
        data = req.json()        
        return data["body"]

    def CheckLewd(self):
        """
        docstring
        """
        self.SqlCursor = self.SqlConn.cursor()
        for Tag in self.Tag:
            print("Check "+Tag+" Lewd")
            req = requests.get("https://www.pixiv.net/ajax/search/artworks/" + Tag + "?word=" + Tag + "&order=date_d&mode=r18&p=1&s_mode=s_tag&type=all&lang=en",headers=GetHeaders(self.Session))
            data = req.json()
            for PixivID in data['body']['illustManga']['data']:
                if PixivID['id'] in self.BannedList:
                    continue
                
                if self.NiggerList != None:
                    for Nigg in self.NiggerList:
                        if Nigg.lower() == PixivID["userName"].lower():
                            self.BannedList.append(PixivID['id'])
                            print("Bann Arts "+PixivID['id'])
                            continue

                if self.Ignore != None:
                    for skp in self.Ignore:
                        if skp in PixivID['tags']:
                            print("Skip lur "+PixivID['id'])
                            self.BannedList.append(PixivID['id'])
                            continue

                self.SqlCursor.execute("select id from Pixiv where IlustID=:PixivID",{"PixivID": PixivID['id']})
                result  = self.SqlCursor.fetchall()
                if len(result) == 0:
                    print("New fanart "+BaseURL+PixivID['id'])
                    IllustData = self.IllustDetail(PixivID['id'])                                        
                    self.SqlCursor.execute("insert into Pixiv values (?,?,?,?,?)", (None,PixivID["id"],IllustData['userId'],IllustData["urls"]["original"],Tag))      
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
        self.SqlConn.commit()
        
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