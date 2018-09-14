# -*- coding: utf-8 -*-
# In your virtualenv: pip install selenium
import time,random,datetime,requests
from threading import Thread
from selenium import webdriver
from colorama import Fore, Back
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

#SETTINGS
queries=[u'Кредит',u'Кредитная карта',u'кредитная карта',u'Кредитка',u'кредитка',u'Взять кредитную карту',u'Получить кредитную карту']
proxies={}
urls={
	'google': {
		'url': 'https://google.ru',
		'input': {'type': By.ID, 'param': 'lst-ib'},
		'src_btn': {'type': By.CLASS_NAME, 'param': "lsb"},
		'ad_link': {'type': By.XPATH,
					'param': "//div[@class='ad_cclk']//a[contains(text(), 'Тинькофф')]"}
	},
	'yandex-banner': {
		'url': 'https://ya.ru',
		'input': {'type': By.ID, 'param': 'text'},
		'src_btn': {'type': By.XPATH, 'param': "html/body/table/tbody/tr[2]/td/form/div[2]/button"},
		'ad_link': {'type': By.XPATH, 'param': "//img[contains(@title, 'Тинькофф')]"}
	},
	'yandex-link': {
		'url': 'https://ya.ru',
		'input': {'type': By.ID, 'param': 'text'},
		'src_btn': {'type': By.XPATH, 'param': "html/body/table/tbody/tr[2]/td/form/div[2]/button"},
		'ad_link': {'type': By.XPATH, 'param': "//li[@aria-label='Реклама']//a[contains(text()[2], 'Тинькофф')]"}
	},
	'mail-link': {
		'url': 'https://go.mail.ru',
		'input': {'type': By.ID, 'param': 'q'},
		'src_btn': {'type': By.XPATH, 'param': ".//*[@id='MSearch-submit']/button"},
		'ad_link': {'type': By.XPATH, 'param': ".//*[@id='js-topBlock']//a[contains(text()[2], 'Тинькофф')]"}
	}
}
''' 'mail-banner': {
				   'url': 'https://go.mail.ru',
				   'input': {'type': By.ID, 'param': 'q'},
				   'src_btn': {'type': By.XPATH, 'param': ".//*[@id='MSearch-submit']/button"},
				   'ad_link': {'type': By.XPATH, 'param': "//img[contains(@title, 'Тинькофф')]"}
			   },'''
sleep_error=1

random.seed()
def rnd_sleep():
	n = random.random()
	addToLog("sleep for seconds: "+str(n),'DEBUG')
	time.sleep(n)
	return

def rnd_do(driver):
	actions = ActionChains(driver)
	body=driver.find_element_by_tag_name('body')
	start_x=random.randint(17,100)
	rnd_sleep()
	start_y = random.randint(15, 100)
	steps=random.randint(10, 50)
	step=0
	w_size=driver.get_window_size()
	try:
		while steps>step:
			print "Windows size->%s x %s Move to ->%s x %s" %(w_size['width'],w_size['height'],start_x+step,start_y+step)
			if start_x+step<w_size['width'] and start_y+step<w_size['height']:
				#actions.move_by_offset(start_x+step, start_y+step).perform()
				rnd_sleep()
				if random.randint(0,1):
					try:
						if random.randint(0, 1):
							act=Keys.ARROW_DOWN
						else:
							act = Keys.ARROW_UP
						driver.find_element_by_tag_name('body').send_keys( act )
						rnd_sleep()
					except Exception, e:
						addToLog(u"Не могу двигаться %s!!! Текст ошибки:%s" % (act,str(e)), 'ERROR')
			step=step+1

	except Exception, e:
		addToLog(u"Аварийное завершение иммитации!!! Текст ошибки:%s" % (str(e)), 'ERROR')
	return

def checkProxy():
	global proxies
	for key in proxies:
		if 'Russian' in proxies[key]['country'] :
			addToLog("%s -> %s" % (key, proxies[key]), 'SHOW')
			profile = webdriver.FirefoxProfile()
			profile.set_preference("network.proxy.type", 1)
			profile.set_preference("network.proxy.http", proxies[key]['ip'])
			profile.set_preference("network.proxy.http_port", int(proxies[key]['port']))
			profile.set_preference("network.proxy.ssl", proxies[key]['ip'])
			profile.set_preference("network.proxy.ssl_port", int(proxies[key]['port']))
			profile.update_preferences()
			driver = webdriver.Firefox(executable_path='./geckodriver',firefox_profile=profile)
			try:
				driver.set_page_load_timeout(30)
				driver.get('http://www.lagado.com/proxy-test')
				#chk_el=WebDriverWait(driver, 55).until(EC.visibility_of_element_located((By.CLASS_NAME, 'ip-info-entry__value')))
				data_ret=proxies[key]
				del proxies[key]
				driver.quit()
				return data_ret
			except Exception, e:
				addToLog(u"ОШИБКА Proxy!!!", 'ERROR')
				if driver:
					driver.quit()
		else:
			addToLog("No Russian %s -> %s" % (key, proxies[key]), 'SHOW')

	return None

def input_to_el(el,text,nowait=False):
	for char in text:
		if not nowait:
			rnd_sleep()
		el.send_keys(char)
	return

def addToLog(msg,type):
		dataTime = time.time()
		verbose_str=u"[%s] %s %s" %(datetime.datetime.fromtimestamp(dataTime).strftime('%Y-%m-%d %H:%M:%S'),type,msg)
		if type=="ERROR":
			print(Fore.RED+verbose_str)
		elif type == "SHOW":
			print(Fore.GREEN+verbose_str)

def getProxies():
	addToLog(u"Получаем прокси", 'SHOW')
	try:
		r = requests.get("http://194.87.92.4/cgi-bin/tgbin/proxies3.pl")
		prdata =r.content.split('\n')
		cnt=0
		for pdata in prdata:
			sp_data=pdata.split(' ')
			if len(sp_data)>2:
				try:
					proxies[cnt]={'ip': sp_data[0].split(':')[0],'port': sp_data[0].split(':')[1],'status': sp_data[1],'country':sp_data[2]}
					cnt=cnt+1
				except Exception, e:
					addToLog(u"Прокси не добавлен" % (str(e)), 'ERROR')
	except Exception, e:
		addToLog(u"Ошибка получения прокси", 'ERROR')
		print e


getProxies()

def checkBrowsers():
		chrome =False
		firefox = False
		try:
			chrome=webdriver.Chrome(executable_path='./chromedriver')
			chrome.quit()
		except Exception, e:
			addToLog(u"Браузер Chrome не обнаружен" % (str(e)), 'ERROR')
		try:
			firefox= webdriver.Firefox(executable_path='./geckodriver')
			firefox.quit()
		except Exception, e:
			addToLog(u"Браузер Firefox не обнаружен" % (str(e)), 'ERROR')
		if chrome and firefox:
			return 0
		elif chrome:
			return 1
		elif firefox:
			return 2

def main():
	global proxies
	addToLog(u"Старт главного потока", 'SHOW')
	step=0
	browsers=checkBrowsers()
	next_pr=None
	#browsers = 2
	while 1:
		try:
			if browsers==0:
				addToLog(u"Выбираем браузер", 'SHOW')
				if random.randint(0, 1):
					if step > 0:
						while not next_pr:
							next_pr = checkProxy()
							if len(proxies) == 0:
								getProxies()
						chrome_options = webdriver.ChromeOptions()
						chrome_options.add_argument('--proxy-server=%s:%s'%(next_pr['ip'],int(next_pr['port'])))
						driver = webdriver.Chrome(executable_path='./chromedriver')
						next_pr = None
					else:
						driver = webdriver.Chrome(executable_path='./chromedriver')
				else:
					if step > 0:
						while not next_pr:
							next_pr = checkProxy()
							if len(proxies) == 0:
								getProxies()
						profile = webdriver.FirefoxProfile()
						profile.set_preference("network.proxy.type", 1)
						profile.set_preference("network.proxy.http", next_pr['ip'])
						profile.set_preference("network.proxy.http_port", int(next_pr['port']))
						profile.set_preference("network.proxy.ssl", next_pr['ip'])
						profile.set_preference("network.proxy.ssl_port", int(next_pr['port']))
						profile.update_preferences()
						driver = webdriver.Firefox(executable_path='./geckodriver', firefox_profile=profile)
						next_pr = None
					else:
						driver = webdriver.Firefox(executable_path='./geckodriver')
			elif browsers==1:
				if step > 0:
					while not next_pr:
						next_pr = checkProxy()
						if len(proxies) == 0:
							getProxies()
					chrome_options = webdriver.ChromeOptions()
					chrome_options.add_argument('--proxy-server=%s:%s' % (next_pr['ip'], int(next_pr['port'])))
					driver = webdriver.Chrome(executable_path='./chromedriver')
					next_pr = None
				else:
					driver = webdriver.Chrome(executable_path='./chromedriver')
			elif browsers==2:
				if step > 0:
					while not next_pr:
						next_pr=checkProxy()
						if len(proxies)==0:
							getProxies()
					profile = webdriver.FirefoxProfile()
					profile.set_preference("network.proxy.type", 1)
					profile.set_preference("network.proxy.http", next_pr['ip'])
					profile.set_preference("network.proxy.http_port", int(next_pr['port']))
					profile.set_preference("network.proxy.ssl", next_pr['ip'])
					profile.set_preference("network.proxy.ssl_port", int(next_pr['port']))
					profile.update_preferences()
					driver = webdriver.Firefox(executable_path='./geckodriver',firefox_profile=profile)
					next_pr=None
				else:
					driver = webdriver.Firefox(executable_path='./geckodriver')


			if random.randint(0, 1):
				driver.set_window_size(random.randint(800,1200), random.randint(600,700))
			else:
				driver.maximize_window()
			step=step+1
			for name_url in urls:
				driver.implicitly_wait(1)

				driver.get(urls[name_url]['url'])
				rnd_sleep()
				search = WebDriverWait(driver, 10).until(
					EC.visibility_of_element_located((urls[name_url]['input']['type'], urls[name_url]['input']['param'])))
				rnd_sleep()
				search.click()
				input_to_el(search, random.choice(queries))
				rnd_sleep()
				ok_btn = WebDriverWait(driver, 5).until(
					EC.visibility_of_element_located((urls[name_url]['src_btn']['type'],  urls[name_url]['src_btn']['param'])))
				rnd_sleep()
				ok_btn.click()
				try:
					ad_link=WebDriverWait(driver, 10).until(
						EC.visibility_of_element_located((urls[name_url]['ad_link']['type'],  urls[name_url]['ad_link']['param'])))
					rnd_do(driver)
					rnd_sleep()
					ad_link.click()
					rnd_sleep()
					rnd_sleep()
					rnd_sleep()
					driver.switch_to.window(driver.window_handles[1])
					rnd_do(driver)
					time.sleep(random.randint(60, 100))
					driver.close()
					driver.switch_to.window(driver.window_handles[0])
				except Exception, e:
					addToLog(u"Рекламная ссылка не найдена", 'ERROR')
				time.sleep(5)
				addToLog(u"Шаг главного потока %s" % (step), 'SHOW')
				time.sleep(random.randint(5,15))
			driver.quit()
		except Exception, e:
			if driver:
				driver.quit()
			addToLog(u"ОШИБКА ГЛАВНОГО ПОТОКА!!!", 'ERROR')
			print e
 
Thread(target=main).start()
