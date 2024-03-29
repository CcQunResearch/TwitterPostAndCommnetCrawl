# -*- coding: utf-8 -*-
# @Time    :
# @Author  :
# @Email   :
# @File    : Spider.py
# @Software: PyCharm
# @Note    :
import json

from utils import write_tweet
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import re
import os

username = ''
password = ''

level_limit = 4  # 评论的深度限制
# tweet_num_limit = 50  # 一次提取的帖子url的数量
reply_num_limit = 800  # 截取的一级评论限制数量

driver_path = r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'

twitter_login_url = 'https://twitter.com/'


class Xpath():
    def __init__(self):
        # 登录
        self.login_button = '//a[@data-testid="loginButton"]'
        self.username_input = '//input[@autocomplete="username"]'
        self.goto_password_button = '//div[@class="css-18t94o4 css-1dbjc4n r-sdzlij r-1phboty r-rs99b7 r-ywje51 r-usiww2 r-2yi16 r-1qi8awa r-1ny4l3l r-ymttw5 r-o7ynqc r-6416eg r-lrvibr r-13qz1uu"]'
        self.password_input = '//input[@autocomplete="current-password"]'
        self.final_login_button = '//div[@data-testid="LoginForm_Login_Button"]'

        self.show_more_replies_button = '//div[@role="button" and @class="css-18t94o4 css-1dbjc4n r-1777fci r-1pl7oy7 r-1ny4l3l r-o7ynqc r-6416eg r-13qz1uu"]'
        self.show_offensive_reply_button = '//div[@role="button" and @class="css-18t94o4 css-1dbjc4n r-1niwhzg r-42olwf r-sdzlij r-1phboty r-rs99b7 r-15ysp7h r-4wgw6l r-1ny4l3l r-ymttw5 r-f727ji r-j2kj52 r-o7ynqc r-6416eg r-lrvibr"]'
        self.tweet_place = '//div[@data-testid="cellInnerDiv"]'
        self.tweet_article = '//article[@data-testid="tweet"]'
        self.source_article = '//article[@data-testid="tweet" and @tabindex="-1"]'
        self.source_use_id = './/div[@class="css-1dbjc4n r-18u37iz r-1wbh5a2"]'
        self.tweet_url_place = './/div[@class="css-1dbjc4n r-18u37iz r-1q142lx"]/a'  # tweet发布时间的xpath，从这里获取tweet的url
        self.tweet_text = './/div[@data-testid="tweetText"]'
        self.time = './/time'
        self.parent_user_id = './/a[@dir="ltr"]'  # 匹配所回复的用户id，也有可能匹配带#的话题超链接
        self.reply_num = './/div[@data-testid="reply"]//span[@data-testid="app-text-transition-container"]'

        self.sub_line = './/div[@class="css-1dbjc4n r-1awozwy r-1hwvwag r-18kxxzh r-1b7u577"]/div'  # 表示回复关系的竖线
        self.unfold_thread_button = './/a[@class="css-4rbku5 css-18t94o4 css-1dbjc4n r-1loqt21 r-t2kpel r-1ny4l3l r-1udh08x r-ymttw5 r-1vvnge1 r-o7ynqc r-6416eg"]'  # "Show this thread"按钮


locator = Xpath()


def find(driver, xpath):
    return driver.find_element_by_xpath(xpath)


def finds(driver, xpath):
    return driver.find_elements_by_xpath(xpath)


def login():
    options = ChromeOptions()
    chrome_options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(driver_path, options=options, chrome_options=chrome_options)
    # driver.maximize_window()

    # driver.get(twitter_login_url)
    # print('正在打开推特登录页面......')
    #
    # WebDriverWait(driver, 20).until(lambda driver: finds(driver, locator.login_button))
    # print("成功打开推特登录页面")
    #
    # login_button = find(driver, locator.login_button)
    # driver.execute_script("arguments[0].click();", login_button)
    #
    # WebDriverWait(driver, 20).until(lambda driver: finds(driver, locator.username_input))
    # username_input = find(driver, locator.username_input)
    # username_input.send_keys(username)
    # print("成功输入账号")
    #
    # goto_password_button = find(driver, locator.goto_password_button)
    # driver.execute_script("arguments[0].click();", goto_password_button)
    #
    # WebDriverWait(driver, 20).until(lambda driver: finds(driver, locator.password_input))
    # password_input = find(driver, locator.password_input)
    # password_input.send_keys(password)
    # print("成功输入密码")
    #
    # final_login_button = find(driver, locator.final_login_button)
    # driver.execute_script("arguments[0].click();", final_login_button)
    # print("成功登录")

    return driver


# 检查article下面的article是不是一个回复, 如果是则返回true (home页面)
def next_is_sub(tweet_article):
    sub_line = tweet_article.find_elements_by_xpath(locator.sub_line)
    unfold_thread_button = tweet_article.find_elements_by_xpath(locator.unfold_thread_button)
    return len(sub_line) == 2 and len(unfold_thread_button) == 0


def wait_reply(*args):
    check_have_smr_button = finds(driver, locator.show_more_replies_button)
    if len(check_have_smr_button) > 0:
        driver.execute_script("arguments[0].click();", check_have_smr_button[0])
    check_have_sor_button = finds(driver, locator.show_offensive_reply_button)
    if len(check_have_sor_button) > 0:
        driver.execute_script("arguments[0].click();", check_have_sor_button[0])
    tweet_articles = finds(args[0], locator.tweet_article)
    tabindexes = [tweet_article.get_attribute('tabindex') for tweet_article in tweet_articles]
    return len(tabindexes) > 0 and tabindexes[-1] == "0"


def wait_new_reply(*args):
    try:
        check_have_smr_button = finds(driver, locator.show_more_replies_button)
        if len(check_have_smr_button) > 0:
            driver.execute_script("arguments[0].click();", check_have_smr_button[0])
        check_have_sor_button = finds(driver, locator.show_offensive_reply_button)
        if len(check_have_sor_button) > 0:
            driver.execute_script("arguments[0].click();", check_have_sor_button[0])
        # time.sleep(0.2)
        tweet_articles = finds(args[0], locator.tweet_article)
        tid_set = get_articles_tid_set(tweet_articles)
    except StaleElementReferenceException:
        return False
    return not tid_set.issubset(global_tid_set)


def scrolling(driver, location):
    js = f"var q=document.documentElement.scrollTop={location}"
    driver.execute_script(js)


def get_articles_tid_set(tweet_articles):
    tid_set = set()
    for tweet_article in tweet_articles:
        tweet_url_places = tweet_article.find_elements_by_xpath(locator.tweet_url_place)
        if len(tweet_url_places) > 0:
            tid_set.add(tweet_url_places[0].get_attribute('href').split('/')[-1])
    return tid_set


def get_article_url(tweet_article):
    return tweet_article.find_element_by_xpath(locator.tweet_url_place).get_attribute('href')


def get_comment(tweet_article, temp_comment_id, source_uid, source_tid, level):
    parent_user_ids = tweet_article.find_elements_by_xpath(locator.parent_user_id)
    reply_num_str = tweet_article.find_element_by_xpath(locator.reply_num).get_attribute('innerText')
    reply_num = int(reply_num_str.replace(",", "")) if len(reply_num_str) > 0 else 0
    tweet_texts = tweet_article.find_elements_by_xpath(locator.tweet_text)
    if len(parent_user_ids) > 0 and parent_user_ids[0].get_attribute(
            'innerText') == f'@{source_uid}' and len(tweet_texts) > 0:
        content = tweet_article.find_element_by_xpath(locator.tweet_text).get_attribute('innerText')
        if len(content) > 0:
            comment_timestr = tweet_article.find_element_by_xpath(locator.time).get_attribute('datetime')
            comment_url = get_article_url(tweet_article)
            comment = {
                "level": level,
                "temp comment id": temp_comment_id,
                "parent": source_tid,
                "content": content,
                "time": datetime.strptime(comment_timestr, "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%y-%m-%d %H:%M'),
                "timestamp": int(time.mktime(time.strptime(comment_timestr, "%Y-%m-%dT%H:%M:%S.%fZ"))),
                "tweet url": comment_url,
                "user id": comment_url.split('/')[-3],
                "tweet id": comment_url.split('/')[-1],
                "reply num": reply_num,
                "children": None
            }
            return comment
        else:
            return None
    else:
        return None


# def get_source_twitter_urls(driver):
#     tweet_urls = set()
#
#     driver.get(twitter_home_url)
#     WebDriverWait(driver, 20).until(lambda driver: finds(driver, locator.tweet_place))
#
#     scrolling_location = 0
#     loop_num = 0
#     while 1:
#         if loop_num > 100:
#             break
#         loop_num += 1
#
#         tweet_articles = finds(driver, locator.tweet_article)
#
#         drop_next = False
#         for tweet_article in tweet_articles:
#             if drop_next:
#                 if not next_is_sub(tweet_article):
#                     drop_next = False
#                 continue
#             if next_is_sub(tweet_article):
#                 drop_next = True
#
#             reply_num_str = tweet_article.find_element_by_xpath(locator.reply_num).get_attribute('innerText')
#             reply_num = int(reply_num_str.replace(",", "")) if len(reply_num_str) > 0 else 0
#             tweet_urls.add(
#                 (tweet_article.find_element_by_xpath(locator.tweet_url_place).get_attribute('href'), reply_num))
#
#         if len(tweet_urls) > 50:
#             break
#
#         scrolling_location += 1200
#         scrolling(driver, scrolling_location)
#         time.sleep(1)
#
#     return tweet_urls


def crawl_tweet(driver, tweet_url, reply_num_max, level=1):
    reply_num_max = reply_num_max if reply_num_max <= reply_num_limit else reply_num_limit

    driver.get(tweet_url)

    try:
        WebDriverWait(driver, 15).until(wait_reply)
    except Exception:
        pass

    source_article = find(driver, locator.source_article)
    source_timestr = source_article.find_element_by_xpath(locator.time).get_attribute('datetime')
    uid = source_article.find_element_by_xpath(locator.source_use_id).get_attribute('innerText')[1:]
    tweet_url_split = tweet_url.split('/')
    tweet_url_split[-3] = uid
    source = {
        "content": source_article.find_element_by_xpath(locator.tweet_text).get_attribute('innerText'),
        "time": datetime.strptime(source_timestr, "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%y-%m-%d %H:%M'),
        "timestamp": int(time.mktime(time.strptime(source_timestr, "%Y-%m-%dT%H:%M:%S.%fZ"))),
        "tweet url": '/'.join(tweet_url_split),
        "user id": uid,
        "tweet id": tweet_url.split('/')[-1]
    }

    tweet_articles = finds(driver, locator.tweet_article)

    global global_tid_set
    global_tid_set = get_articles_tid_set(tweet_articles)
    global no_new_time
    no_new_time = 0

    source_index = 0
    for i, tweet_article in enumerate(tweet_articles):
        if tweet_article.get_attribute('tabindex') == "-1":
            source_index = i
            break
    if source_index + 1 < len(tweet_articles):
        tweet_articles = tweet_articles[source_index + 1:]
    else:
        return {"source": source, "comment": []}

    comments = []

    temp_comment_id = 0
    for tweet_article in tweet_articles:
        comment = get_comment(tweet_article, temp_comment_id, source["user id"], source["tweet id"], level)
        if comment:
            temp_comment_id += 1
            comments.append(comment)

    scrolling_location = 0
    while 1:
        if len(comments) >= reply_num_max:
            break

        scrolling_location += 1200
        scrolling(driver, scrolling_location)
        time.sleep(0.2)

        try:
            WebDriverWait(driver, 6).until(wait_new_reply)
        except TimeoutException:
            if level == 1:
                no_new_time += 1
                if no_new_time > 0:
                    # print(TimeoutException)
                    # print('breaking!!!!!!!!!!')
                    break
            else:
                break

        now_tweet_articles = finds(driver, locator.tweet_article)
        for tweet_article in now_tweet_articles:
            tweet_url_places = tweet_article.find_elements_by_xpath(locator.tweet_url_place)
            if len(tweet_url_places) > 0:
                tid = tweet_url_places[0].get_attribute('href').split('/')[-1]
                if tid not in global_tid_set:
                    global_tid_set.add(tid)

                    comment = get_comment(tweet_article, temp_comment_id, source["user id"], source["tweet id"], level)
                    if comment:
                        temp_comment_id += 1
                        comments.append(comment)

    global_tid_set = set()
    no_new_time = 0

    if level < level_limit:
        for comment in comments:
            if comment["reply num"] > 0:
                comment["children"] = crawl_tweet(driver, comment["tweet url"], comment["reply num"], level=level + 1)[
                    "comment"]
        new_comments = []
        temp_comment_id = 0
        for comment in comments:
            comment["temp comment id"] = temp_comment_id
            children = comment["children"]
            comment["children"] = None
            new_comments.append(comment)
            temp_comment_id += 1

            if children:
                for sub_comment in children:
                    sub_comment["level"] = level
                    sub_comment["temp comment id"] = temp_comment_id
                    new_comments.append(sub_comment)
                    temp_comment_id += 1

        return {"source": source, "comment": new_comments}
    else:
        return {"source": source, "comment": comments}


def save_standard_json(tweet, label, filepath):
    source = tweet["source"]
    source["theme"] = topic
    source["label"] = label
    source_tid = source["tweet id"]
    comments = tweet["comment"]
    tid_2_index = {}
    commnet_id = 0
    new_comments = []
    for comment in comments:
        if comment["parent"] == source_tid:
            parent = -1
        else:
            parent = tid_2_index[comment["parent"]]
            new_comments[parent]["children"].append(commnet_id)
        new_comment = {
            "comment id": commnet_id,
            "parent": parent,
            "children": [],
            "user id": comment["user id"],
            "tweet id": comment["tweet id"],
            "content": comment["content"],
            "time": comment["time"],
            "timestamp": comment["timestamp"]
        }

        new_comments.append(new_comment)
        tid_2_index[comment["tweet id"]] = len(new_comments) - 1

        commnet_id += 1

    write_tweet({"source": source, "comment": new_comments}, filepath)


if __name__ == '__main__':
    driver = login()

    data_dir = 'Twitter15'
    topic = 'No theme'

    label_dict = {
        'true': 0,
        'false': 1,
        'unverified': 2,
        'non-rumor': 3
    }

    labels = []
    tweet_urls = []
    label_file = r'D:\Project\Research\TwitterPostAndCommnetCrawl\rumor_detection_acl2017\twitter15\label.txt'
    f = open(label_file, "r", encoding='UTF-8')
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        label, tweet_id = line.split(':')[0], line.split(':')[1]
        labels.append(label_dict[label])
        tweet_urls.append('https://twitter.com/user/status/' + tweet_id)

    # print(tweet_urls)
    # print(len(tweet_urls))

    for i, tweet_url in enumerate(tweet_urls):
        try:
            # tweet_url = 'https://twitter.com/WHO/status/752965545528528898'
            # tweet_url = 'https://twitter.com/BBCBreaking/status/689722724470620161'
            print(tweet_url)
            tidjson = tweet_url.split('/')[-1] + '.json'
            if os.path.exists(os.path.join(data_dir, tidjson)):
                print('pass')
                continue

            tweet = crawl_tweet(driver, tweet_url, 800)
            save_standard_json(tweet, labels[i], os.path.join(data_dir, f'{tweet["source"]["tweet id"]}.json'))
            print(f'{tweet["source"]["tweet id"]}.json')
        except Exception:
            print('exception')
            continue
