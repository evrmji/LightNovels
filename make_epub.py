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
from urllib.request import URLError
from urllib.request import urlretrieve

from opencc import OpenCC
import mkepub


class LightNovel:

    def __init__(self, url, username='', password=''):

        self.url = url
        self.driver = webdriver.Firefox(firefox_profile=self.firefox_direct())

        try_time = 0
        while try_time < 3:
            try:
                self.driver.set_window_position(1920, -100)
                self.driver.set_window_size(900, 1600)
                self.driver.get(self.url)

                self.wait_xpath('//div[@id="main_message"]//table', 200)

                self.driver.find_element_by_xpath('//div[@id="main_message"]//input[@name="username"]').send_keys(
                    username)
                self.driver.find_element_by_xpath('//div[@id="main_message"]//input[@name="password"]').send_keys(
                    password)

                self.wait_xpath('//input[@id="seccodeverify_cSA"]')
                self.driver.find_element_by_xpath('//input[@id="seccodeverify_cSA"]').click()

                # Wait for Verification
                self.wait_xpath('//img[@src="static/image/common/check_right.gif"]')
                self.driver.find_element_by_xpath('//button[@name="loginsubmit"]').click()

                # Wait for click
                self.wait_xpath('//div[@id="postlist"]')
                try:
                    self.driver.find_element_by_link_text('只看该作者').click()
                    self.wait_xpath('//a[text()="显示全部楼层"]')
                except:
                    pass
                self.wait_loading()
                break

            except:
                try_time += 1
                pass

    def drive_get(self, url):
        try_time = 0
        while try_time < 3:
            try:
                self.driver.get(url)
                try:
                    self.driver.find_element_by_link_text('只看该作者').click()
                    self.wait_xpath('//a[text()="显示全部楼层"]')
                except:
                    pass
                self.wait_loading()
                break

            except:
                try_time += 1
                pass

    # Difine network proxy
    def firefox_direct(self):
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('network.proxy.type', 0)

    # Wait for presense of xpath
    def wait_xpath(self, xpath, time=100):
        wait = WebDriverWait(self.driver, 100)
        wait.until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))

    # Wait for Loading
    def wait_loading(self, max_wait_time=5):
        wait_time = 0
        while self.driver.execute_script('return document.readyState;') != 'complete' and wait_time < max_wait_time:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait_time += 0.1
            time.sleep(0.1)
        print('Load Complete.')

    # Check next page
    def nextpage(self, link_text):
        try:
            next_page = self.driver.find_element_by_link_text(link_text)
        except:
            print("It's the end of pages.")
            next_page = False
        return next_page

    # Get Title
    def get_title(self):
        try:
            title = self.driver.find_element_by_xpath('//span[@id="thread_subject"]').text
            title = convert_chinese(title)
            title = title.replace('/', '\\')
        except Exception as e:
            print(e)
            title = 'Unknown'
        print("Title is {}".format(title))
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

        content = convert_chinese(content)

        content, images = get_images(title, content, image_srcs)

        print('{} content geted.'.format(title))
        return title, content, images

    # Quit Driver
    def driver_quit(self):
        self.driver.quit()
        print('Driver quit.')


#               Content Tools

# Convert Traditional Chinese to Simplified
def convert_chinese(content):
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
        check_make_dir('downloads/' + title + '/images')

        for n, src in enumerate(image_srcs):
            try:
                # Make Image Name and  Image Path
                image_name = title + name_number(image_srcs, n) + '.' + \
                             src.split('.')[-1]
                image_path = 'downloads/' + title + '/images/' + image_name
                print(image_name + ": " + src)

                # Add and Retrieve Image
                # urlretrieve(src, image_path)
                images.append(image_path)
                print('Downloaded.')

                # Replace <img> in Content
                content = replace_img(src, '<img src="{}">'.format('images/' + image_name), content)

            except (HTTPError, URLError) as e:
                # when recieve these errors, just download all images from info of firefox
                print(e)
                image_name = src.split('/')[-1]
                image_path = 'downloads/' + title + '/images/' + image_name
                content = replace_img(src, '<img src="{}">'.format('images/' + image_name), content)
                images.append(image_path)

            except Exception as e:
                print(e)
                content = replace_img(src, '', content)
                continue

    return content, images


#               Make Html

# Make Html file
def make_html(title, content):
    # Write Html File in Title Folder with the same folder structure as epub
    try:
        check_make_dir('downloads/' + title)
        with open('downloads/' + title + '/' + title + '.html', 'w+') as file:
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

# Modify Content
def modify_content(content):
    content = re.sub('</?(?!(img|br)).*?>', '', content)
    content = re.sub('<img.*?>', '\g<0></img>', content)
    content = re.sub('<br>', '<br></br>', content)
    content = re.sub('&nbsp;', ' ', content)
    return content


# Splite Chapters
def split_chapters(pattern, content, length=100):
    chapters = []
    chapter_title = ''
    begining = 0

    finditer_result = re.finditer(pattern, content)
    # print(finditer_result)       <callable_iterator object at 0x10c6373c8>
    try:
        for match_result in finditer_result:
            # first match is in begining
            if match_result.start() == begining:
                chapter_title = match_result.group()
                continue
            else:
                # get the split content end position from this match's begining
                end = match_result.start()
                # add title to content in addChapter
                chapter_content = modify_content(content[begining:end])
                # get second title and content
                print(chapter_title, begining)
                chapters.append((chapter_title, chapter_content))
                # give next loop's second title and begining from this match
                chapter_title = match_result.group().strip(' ')
                begining = match_result.end()
        # after loops, begining is last match'es end
        chapters.append((chapter_title, modify_content(content[begining:])))

        # after get chapters list, arrangement is needed
        new_chapters = []
        title_list = []
        content_plus = ''
        for chapter_title, chapter_content in chapters:
            if len(chapter_content) < length:
                title_list.append(chapter_title)
                content_plus += chapter_content
            else:
                if len(title_list) > 0:
                    new_chapters.append((title_list[0], content_plus))
                    title_list = []
                    content_plus = ''
                new_chapters.append((chapter_title, chapter_content))

        return new_chapters

    except Exception as e:
        print(e)
        return None


# Double Split Chapters
def double_split(title, content):
    chapters = []
    first_chapters = split_chapters('(?<=>).{0,5}?(章|尾声|后记|目录).*?(?=<)', content, 300)
    if first_chapters:
        for first_title, first_content in first_chapters:
            second_chapters = split_chapters('(?<=>)\d{1,3}(?=<)', first_content)
            if second_chapters:
                chapters.append((first_title, second_chapters))
            else:
                chapters.append((first_title, modify_content(first_content)))
    else:
        chapters.append((title, modify_content(content)))
    return chapters


# Add Chapters
def addChapter(book, book_title, chapters):
    for title, content in chapters:
        if title == '':
            title = book_title
        # content is a string
        if isinstance(content, str):
            book.add_page(title=title, content='<h1>{}</h1>'.format(title) + content)
        # content is a list of titles and contents
        if isinstance(content, list):
            if content[0][0] != '':
                # if first secondary title is not blank
                first = book.add_page(title=title, content='<h1>{}</h1>'.format(title))
                for title2, content2 in content:
                    book.add_page(title=title2, content='<h2>{}</h2>'.format(title2) + content2, parent=first)
            else:
                # else first secondary title is blank
                first = book.add_page(title=title, content='<h1>{}</h1>'.format(title) + content[0][1])
                for title2, content2 in content[1:]:
                    book.add_page(title=title2, content='<h2>{}</h2>'.format(title2) + content2, parent=first)


# Set Cover
def setCover(book, image):
    try:
        with open(image, 'rb') as img:
            book.set_cover(img.read())
    except Exception as e:
        print('Cover failed: {}'.format(e))
        pass


# Get Images
def setImages(book, images):
    for image_path in images:
        try:
            with open(image_path, 'rb') as image:
                book.add_image(image_path.split('/')[-1], image.read())
        except Exception as e:
            print('{} failed: \n{}'.format(image_path, e))
            continue


# Make Epub
def make_epub(title, content, images=[]):
    check_make_dir('downloads/' + title)
    print('Making Epub...')
    # Make Epub File
    if os.path.isfile('downloads/' + title + '.epub'):
        os.remove('downloads/' + title + '.epub')
    book = mkepub.Book(title=title)
    # Split Chapters
    chapters = double_split(title, content)
    # Add Chapters
    addChapter(book, title, chapters)
    # Add Images
    if images != []:
        try:
            setCover(book, images[0])
            setImages(book, images)
        except Exception as e:
            print(e)
            pass

    # Save Book
    book.save('downloads/' + title + '.epub')
    print(title + '.epub file complete.')


# Get epub of multi urls
def collect_epubs(url_list, username='mk2016a', password='123456Qz'):
    # Get list
    list = []
    url = url_list[0]
    novel = LightNovel(url, username='mk2016a', password='123456Qz')
    title, content, images = novel.get_content()
    list.append((title, content, images))
    # open urls in the same driver
    for url in url_list[1:]:
        novel.drive_get(url)
        title, content, images = novel.get_content()
        list.append((title, content, images))
    novel.driver_quit()

    # Make Epub
    print('Making epub...')
    book_name = '{} All.epub'.format(list[0][0])
    if os.path.isfile('downloads/' + book_name):
        os.remove('downloads/' + book_name)
    book = mkepub.Book(book_name)
    # get chapters
    chapters = []
    for title, content, images in list:
        chapters = split_chapters('(?<=>).{0,5}?(章|尾声|后记|目录).*?(?=<)', content)
        if chapters:
            first = book.add_page(title, '<h1>{}</h1>'.format(title))
            for title2, content2 in chapters:
                book.add_page(title=title2, content='<h2>{}</h2>'.format(title2) + content2, parent=first)
        else:
            first = book.add_page(title, '<h1>{}</h1>'.format(title) + content)
        setImages(book, images)
    print(list[0][2][0])
    setCover(book, list[0][2][0])
    book.save('downloads/' + book_name)
    print('{} file complete.'.format(book_name))


novel = LightNovel('https://www.lightnovel.cn/forum.php?mod=viewthread&tid=930679&highlight=为美好')
title, content, images = novel.get_content()
make_html(title, content)
make_epub(title, content, images)
novel.driver_quit()

# url_list = ['https://www.lightnovel.cn/forum.php?mod=viewthread&tid=915987&highlight=为美好',
#            'https://www.lightnovel.cn/forum.php?mod=viewthread&tid=928655&highlight=为美好',
#            'https://www.lightnovel.cn/forum.php?mod=viewthread&tid=930675&highlight=为美好',
#            'https://www.lightnovel.cn/forum.php?mod=viewthread&tid=935285&highlight=为美好']
# collect_epubs(url_list)

