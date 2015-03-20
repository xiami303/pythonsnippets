#coding=utf-8  
# http://www.darkbull.net/python/bd/%E5%86%99%E4%B8%AA%E5%9B%BE%E7%89%87%E8%9C%98%E8%9B%9B%E7%8E%A9%E7%8E%A9/

  
import os  
import sys  
import re  
import urllib  
  
URL_REG = re.compile(r'(https://[^///]+)', re.I)  
IMG_REG = re.compile(r''']*?src=([/'"])([^\1]*?)\1''', re.I)
IMG_REG2 = re.compile(r''']*?background-image:([/'"])([^\1]*?)\1''', re.I)  




def download(dir, url):  
    '''''下载网页中的图片 
     
    @dir 保存到本地的路径 
    @url 网页url 
    '''  
    global URL_REG, IMG_REG  
      
    m = URL_REG.match(url)  
    if not m:   
        print '[Error]Invalid URL: ', url  
        return  
    host = m.group(1)  
      
    if not os.path.isdir(dir):  
        os.mkdir(dir)  
      
    # 获取html,提取图片url  
    html = urllib.urlopen(url).read()  
    imgs = [item[1].lower() for item in IMG_REG.findall(html)]  
    f = lambda path:path if path.startswith('http://') else \
    host + path if path.startswith('/') else url + '1/' + path  
    imgs = list(set(map(f, imgs)))  
    print '[Info]Find %d images.' % len(imgs)  
      
    # 下载图片  
    for idx, img in enumerate(imgs):  
        name = img.split('/')[-1]  
        path = os.path.join(dir, name)  
        try:   
            print '[Info]Download(%d): %s'% (idx + 1, img)  
            urllib.urlretrieve(img, path)  
        except:   
            print "[Error]Cant't download(%d): %s" % (idx + 1, img)  
    


    # 获取图片使用background-page 设置的情况
    imgs2 = [item[1].lower() for item in IMG_REG2.findall(html)]  
    f = lambda path:path if path.startswith('https://') else \
    host + path if path.startswith('/') else url + '1/' + path  
    imgs2 = list(set(map(f, imgs2)))  
    print '[Info2]Find %d images.' % len(imgs2)  
     # 下载图片  
    for idx, img in enumerate(imgs2):  
        name = img.split('/')[-1]  
        path = os.path.join(dir, name)  
        try:   
            print '[Info]Download(%d): %s'% (idx + 1, img)  
            urllib.urlretrieve(img, path)  
        except:   
            print "[Error]Cant't download(%d): %s" % (idx + 1, img)  
    



    # 获取css， 下载css


    # 读取css里的background-page, 下载对应图片


    # 获取js，下载js



def main():  
    if len(sys.argv) != 3:  
        print 'Invalid argument count.'  
        return  
    dir, url = sys.argv[1:]  
    download(dir, url)  
  
if __name__ == '__main__':  
    download('D://Imgs', 'http://www.163.com')  
    #download('D://Imgs', 'https://www.dreamtrips.com/results.html')
    #main()
