# #coding:utf-8
import urllib


url = "https://www.dreamtrips.com/trips/details/10001/see-the-sights-in-south-korea"
#url = "https://www.dreamtrips.com/results.html"
response=urllib.urlopen(url)
html= response.read()


filehandler = open(r'dealpage.html', 'w')
filehandler.write(html)
filehandler.close()
