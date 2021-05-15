### Pixiv RSS
simpe pixiv r-18 RSS  
```
usage: main.py [-h] -s SESSION -t TAG [-w WEBHOOK] [-b BANNED] [-i IGNORE]

Pixi Lewd RSS

optional arguments:
  -h, --help            show this help message and exit
  -s SESSION, --Session SESSION
                        Pixivi SessionID
  -t TAG, --Tag TAG     Pixiv tag(separated by commas)
  -w WEBHOOK, --Webhook WEBHOOK
                        Discord webhook
  -b BANNED, --Banned BANNED
                        Ignore artis fanart(separated by commas)
  -i IGNORE, --Ignore IGNORE
                        Skip hashtag(separated by commas)
```
Example:  
`python main.py -s 21304697_6VBvZ4pQvnj9XXXXXXXX -t GenshinImpact,Hololive,Nijisanji -w https://discord.com/api/webhooks/XXXXXXXXX/XXXXXXXX  -b 'dot takeshi' -i 'loli,gore'`

#### Get sessionID
to get pixiv session id you must login,after login open Inspect in browser and find storage then find `PHPSESSID` in name col and copy the value  
remember to keep safe your session id **DONT SHARE YOUR SESSION ID**

#### Note
for tag i would recommend you using japanese hashtag rather than latin