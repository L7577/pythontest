###
# 参考：https://zhuanlan.zhihu.com/p/45645693
# 图片网站：http://letsfilm.org/archives/51186/
###

import urllib.request
import urllib.parse
import re

def open_url(url):
  req=urllib .request .Request (url)   
  #req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0')
  req.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
  page=urllib .request .urlopen(req)
  html=page .read().decode('utf-8')
  #print(html)
  return html

def get_img(html):
  #p=r'<img src="([^"]+\.jpg)"'
  p=r'<a href="([^"]+\.jpg)"'
  print(p)
  imglist=re.findall(p,html )
  print(imglist)
  for each in imglist :
    print(each)
    filename=each.split("/")[-1]
    print(filename)
    photo=urllib .request .urlopen(each )
    w=photo.read()
    f=open('/home/l/test/pythontest/image/'+filename,'wb')
    f.write(w)
    f.close()

if __name__=='__main__':
  for i in range(1,11):
    if i==1:
      url="http://letsfilm.org/archives/51186"
    else:
      url="http://letsfilm.org/archives/51186/"+str(i)
    print(url)
    get_img(open_url(url))