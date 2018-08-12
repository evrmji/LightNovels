from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import StaleElementReferenceException

import requests
from bs4 import BeautifulSoup

import re
import os
import time
from urllib.parse import urljoin
from urllib.request import HTTPError
from urllib.request import urlretrieve
from opencc import OpenCC

import mkepub





class LightNovel:


    def __init__(self, url, username, password):

        self.driver = webdriver.Firefox(firefox_profile=self.firefox_direct())

        self.driver.set_window_position(1920, -100)
        self.driver.set_window_size(900, 1600)
        self.driver.get(self.url)

        self.wait_xpath('//div[@id="main_message"]//table', 200)


        self.driver.find_element_by_xpath('//div[@id="main_message"]//input[@name="username"]').send_keys(username)
        self.driver.find_element_by_xpath('//div[@id="main_message"]//input[@name="password"]').send_keys(password)

        self.wait_xpath('//input[@id="seccodeverify_cSA"]')
        self.driver.find_element_by_xpath('//input[@id="seccodeverify_cSA"]').click()

        # Wait for Verification
        self.wait_xpath('//img[@src="static/image/common/check_right.gif"]')
        self.driver.find_element_by_xpath('//button[@name="loginsubmit"]').click()

        # Wait for click
        self.wait_xpath('//div[@id="postlist"]')
        self.driver.find_element_by_link_text('只看该作者').click()
        self.wait_xpath('//a[text()="显示全部楼层"]')
        self.wait_loading()

    # Difine network proxy
    def firefox_direct(self):
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('network.proxy.type', 0)

    # Wait for presense of xpath
    def wait_xpath(self, xpath, time=100):
        wait = WebDriverWait(self.driver, 100)
        wait.until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))

    # Wait for Loading
    def wait_loading(self):
        while self.driver.execute_script('return document.readyState;') != 'complete':
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.1)
        print('Load Complete.')

    # Check next page
    def nextpage(self, link_text):
        try:
            next_page = self.driver.find_element_by_link_text(link_text)
        except :
            print("It's the end of pages.")
            next_page = False
        return next_page

    # Get Title
    def get_title(self):
        try:
            title = self.driver.find_element_by_xpath('//span[@id="thread_subject"]').text
            title = opencc(title)
            title = title.replace('/', '\\')
        except Exception as e:
            print(e)
            title = 'Unknown'
        print("Title is {}".format(title))
        check_make_dir(title)
        return title


    # Get Content including images
    def get_content(self):

        # define variables
        title = self.get_title()
        content = ''
        image_srcs = []

        # Next Page
        while True:

            # Get Content and Images' src
            tds = self.driver.find_elements_by_xpath('//td[@class="t_f"]')
            for td in tds:

                # Add Content
                content += td.get_attribute('innerHTML')

                # Add Image srcs
                imgs = td.find_elements_by_tag_name('img')
                if imgs != []:
                    for img in imgs:
                        src = img.get_attribute('file')
                        if src not in image_srcs and src != None:
                            image_srcs.append(src)

            # Check Next
            next_page = self.nextpage('下一页')
            if next_page:
                next_page.click()
                self.driver.implicitly_wait(1)
                self.wait_loading()
            else:
                break

        content = opencc(content)

        content, images = get_images(title, content, image_srcs)

        return title, content, images

    # Quit Driver
    def driverquit(self):
        self.driver.quit()
        print('Driver quit.')

#               Content Tools

# Convert Traditional Chinese to Simplified
def opencc(content):
    openCC = OpenCC('t2s')
    content = openCC.convert(content)
    return content

# Name Number
def name_number(array, number):
    return (len(str(len(array) - 1)) - len(str(number))) * '0' + str(number)
    # must use return, otherwise it will be None

# Check and Make directory
def check_make_dir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)

# Replace <img>
def replace_img(src, replacement, content):
    for origin_text, replace_text in [('.', '\.'), ('?', '\?'), ('&', '\&')]:
        src = src.replace(origin_text, replace_text)
    return re.sub('<img.*?{}.*?>'.format(src), replacement, content)

# Get Images
def get_images(title, content, image_srcs):
    images = []
    if image_srcs != []:

        # Retrieve Images
        check_make_dir(title + '/images')

        for n, src in enumerate(image_srcs):
            try:
                # Make Image Name and  Image Path
                image_name = 'pic' + name_number(image_srcs, n) + '.' + \
                             src.split('.')[-1]
                image_path = 'images/' + image_name
                print(image_name + ": " + src)

                # Add and Retrieve Image
                urlretrieve(src, title + '/' + image_path)
                images.append(image_path)

                # Replace <img> in Content
                content = replace_img(src, '<img src="{}">'.format(image_path), content)

            except HTTPError:
                image_name = src.split('/')[-1]
                image_path = 'images/' + image_name
                content = replace_img(src, '<img src="{}">'.format(image_path), content)
                images.append(image_path)

            except Exception as e:
                print(e)
                content = replace_img(src, '', content)
                continue

    return  content, images

#               Make Html

# Make Html file
def make_html(title, content):
    # Write Html File in Title Folder with the same folder structure as epub
    try:
        with open('downloads/'+title + '/' + title + '.html', 'w') as file:
            file.write('''<html lang="cn">
            <head>
                <meta charset="utf-8">
            </head>
            <body>
                <div>
                    {}
                </div>
            </body>
        </html>'''.format(content))
        print('{} html file is done.'.format(title))
    except Exception as e:
        print(e)
        pass

#               Make Epub

# Split Chatpers with chapter titles
def finditer_titles(content):
    re.finditer('(?<=>).{0,5}?(章|尾声|后记|目录).*?(?=<)', content, re.MULTILINE)

# Modify Content
def modify_content(content):
    content = re.sub('</?(?!(img|br)).*?>', '', content)
    content = re.sub('<img.*?>', '\g<0></img>', content)
    content = re.sub('<br>', '<br></br>', content)
    content = re.sub('&nbsp;', ' ', content)
    return content

# Splite Chapters
def split_chapters(title, content):

    chapters = []
    chatper_title = title
    begining = 0


    finditer_results = finditer_titles(content)

    try:
        for match_result in finditer_results:
            if match_result.start() == begining:
                chatper_title = match_result.group()
            else:
                end = match_result.start() - 1
                if (end - begining) > 100:
                    print(chatper_title, begining)
                    if chatper_title == title:
                         chapter_content = modify_content(content[:end])
                    else:
                        chapter_content = '<h2>{}</h2>'.format(chatper_title) + modify_content(content[begining:end])
                    chapters.append((chatper_title, chapter_content))
                    chatper_title = match_result.group().strip(' ')
                    begining = match_result.end()

        if (len(content) - begining) > 100:
            chapters.append((chatper_title, modify_content(content[begining:])))
    except:
        chapters.append((title, modify_content(content)))


    return chapters

# Make Epub
def make_epub(title, content, images=[]):
    # Make Epub File
    book = mkepub.Book(title=title)
    if os.path.isfile(title + '.epub'):
        os.remove(title + '.epub')

    chapters = split_chapters(title, content)

    # Add Chapters
    for n, chapter in enumerate(chapters):
        book.add_page(title=chapter[0], content=chapter[1])

    if images != []:
        try:
            # Set Cover
            with open(title+'/'+images[0], 'rb') as image:
                book.set_cover(image.read())
        except:
            pass

        # Add Images
        for image_path in images:
            try:
                with open(title+'/'+image_path, 'rb') as image:
                    book.add_image(image_path.split('/')[-1], image.read())
            except Exception as e:
                print(e)
                continue

    # Save Book
    book.save('downloads/'+title + '.epub')
    print(title+'.epub file is done.' )
