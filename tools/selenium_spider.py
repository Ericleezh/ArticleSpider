# -*- coding: utf-8 -*-
__author__ = 'leeho'

from selenium import webdriver

# browser = webdriver.Chrome(executable_path="C:/Users/ASUS/Desktop/chromedriver.exe")
# browser.get("http://blog.csdn.net/cz9025/article/details/70160273")
# print(browser.page_source)
# browser.quit()

# 设置chromedriver不加载图片
options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
options.add_experimental_option("prefs",prefs)
browser = webdriver.Chrome(executable_path="C:/Users/ASUS/Desktop/chromedriver.exe",chrome_options=options)
browser.get("https://www.taobao.com")

# phantomjs 无界面浏览器，多进程情况下性能很差