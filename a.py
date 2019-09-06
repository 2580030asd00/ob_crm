# from selenium import webdriver
#
# #使用webkit无界面浏览器
# driver = webdriver.PhantomJS(executa_path=r'D:/python/phantomjs-2.1.1-windows/bin/phantomjs.exe')#如果路径为exe启动程序的路径 那么该路径需要加一个r
# #获取搜狐网滚动新闻页
# driver.get('http://news.sohu.com/scroll')



# import pandas as pd
#
# import numpy as np
#
# # df = pd.DataFrame({'a':1,'x':2})
# # print(df)
# s = pd.Series([1, 3, 5, np.nan, 6, 8])
#
# print(s)

# print('\n'.join([' '.join(['%s*%s=%-2s' % (j, i, i * j) for j in range(1, i + 1)]) for i in range(1, 10)]))

#导入selenium
from selenium import webdriver
# browser = webdriver.Firefox()
driver = webdriver.Chrome()

driver.get('https://www.baidu.com')
print(driver.page_source)

driver.close()
