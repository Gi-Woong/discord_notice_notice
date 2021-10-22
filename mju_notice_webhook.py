import requests
import json
import feedparser
import datetime as dt
import os, sys

#말그대로 rss를 파싱해주는 것
def RSS_PARSE():
  parsed_rss = feedparser.parse('https://www.mju.ac.kr/bbs/mjukr/141/rssList.do')
  rss = parsed_rss.entries
  return rss

#content를 받고 정리해서 돌려줌
def RSS_CONTENT(rss): 
  title = "{}".format(str(rss.title))

  #요약 및 두괄식
  summary=str(rss.description).split(".",maxsplit=1)[0]
  first_sen=str(rss.description).split("다.",maxsplit=1)[0]
  if len(summary)<=4:
    description=""
  elif len(first_sen)>50:
    description =summary[:50]+"⋯"
  else:
    description=first_sen+"다."
  
  link = str(rss.link)
  
  published = rss.published #게시 날짜
  date = ':'.join(published.split(":")[:-1])
  kor_date=dt.datetime.strptime(date,"%Y-%m-%d %H:%M")-dt.timedelta(hours=9)#디스코드가 GMT를 사용해서 그만큼 빼줘야 함.
  kor_date=str(kor_date)
  return title, description, link, kor_date

#포스트 리퀘스트를 보내기
def REQUEST_POST(data, webhook_url):
  r=requests.post(
    webhook_url,
    data=json.dumps(data),
    headers={'Content-Type' : 'application/json'})

#공지형식의 임베드 구조 만들고 포스트 하기
def POST_rss(rss, webhook_url):
  title, description, link, date = RSS_CONTENT(rss)
  data = {
    "content":"",
    "embeds" : [
      {
        "title" : title,
        "description" : description,
        "url" : link,
        "color" : "598634",
        "author" : {
          "name" : "일반공지",
          "url" : "https://www.mju.ac.kr/mjukr/255/subview.do",
          "icon_url": "https://cdn.discordapp.com/attachments/762346328621580291/848727804622667806/unknown.png"
        },
        "timestamp" :  date + ".000Z"
      }
    ]
  }
  REQUEST_POST(data, webhook_url)# post request

def main():
  recent_path = "./recent.json"
  rsss = RSS_PARSE()
  for webhook_url in sys.argv[1:]:
    if os.path.isfile(recent_path):
      recent = open(recent_path, "r", encoding="utf-8").readlines()
      recent = json.loads("\n".join(recent))
      #제목과 summary가 다르면 webhook에 보내기
      for rss in rsss:
        if recent["title"] != rss["title"] or recent["summary"] != rss["summary"]:
          POST_rss(rss, webhook_url)
        else:
          break
  with open(recent_path, "w", encoding="utf-8") as w:
    w.write(json.dumps(rsss[0]))
    w.close()

if __name__ == '__main__':
    main()