import os
import requests
import json
import time
import re
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def init():
    url = 'http://www.u17.com/comic_list/th99_gr99_ca99_ss99_ob0_ac0_as0_wm0_co99_ct99_p1.html?order=2'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get(url)
    with open('cookies.data','r') as f:
        cookies = json.loads(f.read())
    for cookie in cookies:
        browser.add_cookie(cookie)
    browser.get(url)
    return browser

def get_comic(browser,tag):
    #select tag comic
    tag_btn = browser.find_element_by_css_selector(tag)
    tag_btn.click()
    #end select
    pages = browser.find_elements_by_css_selector('#page_section a')[-1].text
    pages = int(pages)+1
    for page in range(1,2):
        print('comics in page 1:')
        page_input = browser.find_element_by_css_selector('.input_txt')
        page_input.send_keys(page)
        page_btn = browser.find_element_by_css_selector('.btn_go')
        page_btn.click()
        wait = WebDriverWait(browser,10)
        wait.until(EC.visibility_of_all_elements_located)
        time.sleep(0.5)
        comics = browser.find_elements_by_css_selector('#all_comic_list .tit')
        for comic in comics[21:22]:
            name = comic.text
            comic.send_keys(Keys.ENTER)
            parse_comic(browser,name)

def parse_comic(browser,name):
    print('parse comic: '+name)
    browser.switch_to_window(browser.window_handles[1])
    wait = WebDriverWait(browser,10)
    wait.until(EC.presence_of_all_elements_located)
    filepath = 'comic/'
    if not os.path.exists(filepath+name):
        os.mkdir(filepath+name)
    filepath = filepath+name+'/'
    divs = browser.find_elements_by_css_selector('.chapterlist_box div')
    for div in divs:
        if div.get_attribute('class')=='zhenhunjie_slide_open':
            div.click()
    chapters = browser.find_elements_by_css_selector('#chapter li a')
    for chapter in chapters:
        title = chapter.get_attribute('title').strip()
        path = filepath+title
        if not os.path.exists(path):
            os.mkdir(path)
        chapter = chapter.get_attribute('href')
        html = get_html(browser,chapter)
        print('download comic:' + name +' chapter: '+ title)
        download_comic(path,html)
        print(title+' download success')
    browser.close()
    browser.switch_to_window(browser.window_handles[0])
    print(name+'download success!')

def get_html(browser,chapter):
    url = 'http://www.u17.com/chapter_vip/' + get_url(chapter) + 'shtml'
    browser.execute_script('window.open()')
    browser.switch_to_window(browser.window_handles[2])
    browser.get(url)
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_all_elements_located)
    html = browser.page_source
    browser.close()
    browser.switch_to_window(browser.window_handles[1])
    return html

def get_url(url):
    pattern = '.*?chapter/(.*?)html'
    pattern = re.compile(pattern)
    url = re.findall(pattern,url)
    return url[0]

def download_comic(path,html):
    doc = pq(html)
    pics = doc('.cur_pic').items()
    page = 0
    for pic in pics:
        page = page+1
        url = pic.attr('xsrc')
        save_img(path,page,url)

def save_img(path,page,url):
    response = requests.get(url)
    if response.status_code == 200:
        path = '{}/{}.jpg'.format(path,str(page).zfill(3))
        if not os.path.exists(path):
            with open(path,'wb') as f:
                f.write(response.content)

def main():
    print('init')
    browser = init()
    print('init success')
    tag = '#iv_4'
    get_comic(browser,tag)

if __name__ == '__main__':
    print('start!')
    main()
