import requests
from bs4 import BeautifulSoup
import re
from simplify_Chinese import OpenCC
from urllib.parse import urljoin
import os
from urllib.request import urlretrieve
from PIL import Image
import pytesseract

def make_html(url,
             title_tag='h3',
             content_class='d_post_content',
             replacements=[(r'<img.+tb2.bdstatic.com/tb/editor/images/face.+',''),
                           (r'   +', '  '),
                           (r'===+', '  ')],
              txt_replacements=[('<br/>', '\n'),
                                ('</div>', '\n'),
                                (r'<.*?>', ''),
                                (r'&lt;(.*?)&gt;', r'<\1>'),]):

    #   Baidu Only Master
    if not re.search('see_lz=1', url):
        url = urljoin(url, "?see_lz=1")

    #   Get Book Page Resources
    resources = requests.get(url).content
    soup = BeautifulSoup(resources, "html.parser")

    #   Get Book Page Title
    try:
        title = soup.find_all(title_tag)[0].text
        openCC = OpenCC('t2s')
        title = openCC.convert(title)
    except (TypeError, IndexError):
        title = "unknow title"
    print(title)

    #   Get All Pages
    url_list = [url]
    for a in soup.find_all('a'):
        url = urljoin(url, a.get('href'))
        if url in url and url != url and url not in url_list:
            url_list.append(url)

    #   Get Page Contents

    contents = str()
    for url in url_list:
        resources = requests.get(url).content
        soup = BeautifulSoup(resources, "html.parser")

        #   Contents
        for content in soup.find_all("div", class_=content_class):
            content = str(content)
            print(content)
            for replacement in replacements:
                content = re.sub(replacement[0], replacement[1], content)
            openCC = OpenCC('t2s')
            content = openCC.convert(content)
            contents += content

        #   Images
        imgs = soup('img')

        i = 0
        images = []
        for img in imgs:
            src = img['src']
            if src.startswith('https://imgsa.baidu.com/forum'):
                i += 1
                img_number = (len(str(len(imgs))) - len(str(i))) * '0' + str(i)
                img_name = img_number + '.' + src.split('.')[-1]
                images.append((img_name, src))
                print(img_name+'  '+src)

                contents = re.sub(src, img_name, contents)

    # write html file

    beginning = '<head><meta charset="UTF-8"></head><body>'
    ending = '</body>'
    contents = beginning+'<h3>'+title+'</h3>\n<div>'+contents+'</div>'+ending

    return title, contents, images

    # Make Text File

    soup = BeautifulSoup(open(title+'/'+title+'.html').read(), 'html.parser')
    txt_contents = str(soup)

    # replace image files
#    for img_name in img_names:
#        img = Image.open(title+'/'+img_name)
#        img_content = pytesseract.image_to_string(img, lang='chi_sim')
#        if len(img_content)>100:
#            print(img_content)
#            txt_contents = re.sub('<.+?'+img_name+'.+?>', '\n'+img_content+'\n', txt_contents)

    # replace html code
#    for txt_replacement in txt_replacements:
#        txt_contents = re.sub(txt_replacement[0], txt_replacement[1], txt_contents)
#
#    # write text file
#    file = open(title+'/'+title+'.txt', 'w+')
#    file.write(txt_contents)
#    file.close()


