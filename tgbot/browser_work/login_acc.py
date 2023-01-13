# import asyncio
# import os
# import pickle
# import time
#
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import logging
import json
import zipfile
import requests
# async def get_cookies(phone, driver):
#     driver.get('https://www.wildberries.ru/')
#     s = input()
#     await asyncio.sleep(1)
#     pickle.dump(driver.get_cookies(), open(f'cookies_{phone}', 'wb'))
#     await asyncio.sleep(5)
#     driver.close()
#
#
# def save_cookies(driver, phone):
#     time.sleep(1)
#     dir_ = os.path.abspath(os.curdir)
#     pickle.dump(driver.get_cookies(), open(f'browser_work\\cookies\\cookies_{phone}', 'wb'))
#     time.sleep(1)
#
#
# def set_cookies(driver, phone):
#     driver.get('https://www.wildberries.ru/')
#     dir_ = os.path.abspath(os.curdir)
#     for cookie in pickle.load(open(f'browser_work\\cookies\\cookies_{phone}', 'rb')):
#         driver.add_cookie(cookie)
#     time.sleep(1)
#     driver.refresh()
#     time.sleep(5)
#     return driver
#
#
# def get_open_browser():
#     #logging.getLogger('WDM').setLevel(logging.NOTSET)
#     user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
#     dir_ = os.path.abspath(os.curdir)
#     opts = Options()
#     opts.add_argument('--disable-logging')
#     opts.add_argument(f'user-agent={user_agent}')
#     opts.add_argument('--start-maximized')
#     #opts.headless = True
#     try:
#         driver = webdriver.Chrome(f'chromedriver.exe', options=opts)
#         driver.get('https://google.com')
#         return driver
#     except:
#         return False

import asyncio
import os
import pickle
import time

# from selenium import webdriver
# from seleniumwire import webdriver
from pathlib import Path

# import seleniumwire.undetected_chromedriver as webdriver
#from webdriver_manager.chrome import ChromeDriverManager
import logging
#import undetected_chromedriver as uc
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.services.db_queries import update_wb_account, get_wbaccount
from tgbot.utils.wb_api import api_auth


def get_cookies(phone, driver):
    driver.get('https://seller.wildberries.ru/')
    s = input()
    time.sleep(1)
    pickle.dump(driver.get_cookies(), open(f'cookies_{phone}', 'wb'))
    time.sleep(5)
    driver.close()


def save_cookies(driver, phone):

    time.sleep(1)
    cok = driver.get_cookies()
    print(cok)
    # for i in cok:
    #     print(i)
    pickle.dump(cok, open(f'F:\работа\Ноябрь 2022\WB реклама мой бот\Старый бот\dump\cookies_{phone}', 'wb'))
    time.sleep(1)


def set_cookies(driver, phone):
    seller = True
    if not seller:
        WILDAUTHNEW_V3_my = 'E64E6110F305C403E6369F38807E9955CD9EC7B4779692D6CE72C697F2FDE38379C4F8F92EF8992F49B80799A5861B492FD3D021350B2511E0B49C3D03C34C139FDBD3233BEB329167EDF2BC0CC680A9D9740922D93EEB9F0FA3B248BC95CAED9D2B72B99A55941EE99E0BD38CD087A946358AE4E271FD6EAA2E131487A923B96BEB9133BB929DFB5611B941FFDD192F7F6CF031AF70C7B66B570DCEFCCE8C7CE477B592B92F86E13FFF39E35DCC10CF8880828A5627F7D6E360F994BFD1C41C606A57AB88EE0DEADB21097D84658F4ABA98B66F633577A97FBE676BE551B4E87603C1753A18EA3573C312A52B610DE601270AAB1BABD1A804890DE36618D1881F93E31276A619759619E7A1576829F19D4AFD958BADDE290AA17121EDEECCBFD0C23EC69D4AAFCCF9A2472AC5C3C2FDF8AA8E18BADDCDF7AB1638BB46C1BE76190DDBD9C85FD64C70B7DC12F0098CAAA7170428'
        WILDAUTHNEW_V3_2 = '5D822EDA58EABF2D47539DA6C4072529B2F8982A5F639AF3CC16E0052368C94C3597A95C5DBDE5D6834769BD8BBD62FB96CAEA537B7D7E8E63932CD826163F2B224C2A97786928F86A2DCFFFC19E8BFA9BBD965A1BEAF0DAF3C859A184E2AE900ECA71907CBCD466389314A1DE4815BAA27802AB8C30665FC1B038B17503A0F329082D0A8AB7942928CB891FC166A1088A1F0AC3FBD3C4A7A91771AC6BA33B4E98F462D28D7A2EB5C2200AB92A31F817B04A4E749AECB3A5C2AEB5B1C3064CB3462472CC9244DC73372FF294F28D84B921580FA48601B4FF8622A8A17D3C7F8D693FBF9CA93644362BAAE5BE49B79B05ECEF1759836F33885C2376424E0FF2B5553E9BBE38F0A0C962E7DBADA5897A78EBFAB88AF833532BC0FFAC32A3CA901AA72B6926'
        driver.get('https://www.wildberries.ru/')
        c = 'BasketUID=62cf91b6-c80d-4fee-ac6e-e44c89c434d6; _wbauid=3717703611654951772; _ga=GA1.2.937760077.1654951773; ___wbu=5ea8e470-400c-4aa4-bb76-6d3b534cc520.1656610871; __bsa=basket-ru-42; SL_C_23361dd035530_DOMAIN=true; _gcl_au=1.1.336928433.1662749323; x-supplier-id-external=c9640da8-a840-5484-bb00-dee7d6df69dd; WILDAUTHNEW_V3=E64E6110F305C403E6369F38807E9955CD9EC7B4779692D6CE72C697F2FDE38379C4F8F92EF8992F49B80799A5861B492FD3D021350B2511E0B49C3D03C34C139FDBD3233BEB329167EDF2BC0CC680A9D9740922D93EEB9F0FA3B248BC95CAED9D2B72B99A55941EE99E0BD38CD087A946358AE4E271FD6EAA2E131487A923B96BEB9133BB929DFB5611B941FFDD192F7F6CF031AF70C7B66B570DCEFCCE8C7CE477B592B92F86E13FFF39E35DCC10CF8880828A5627F7D6E360F994BFD1C41C606A57AB88EE0DEADB21097D84658F4ABA98B66F633577A97FBE676BE551B4E87603C1753A18EA3573C312A52B610DE601270AAB1BABD1A804890DE36618D1881F93E31276A619759619E7A1576829F19D4AFD958BADDE290AA17121EDEECCBFD0C23EC69D4AAFCCF9A2472AC5C3C2FDF8AA8E18BADDCDF7AB1638BB46C1BE76190DDBD9C85FD64C70B7DC12F0098CAAA7170428; __wbl=cityId%3D0%26regionId%3D0%26city%3D%D0%B3%20%D0%A5%D0%B8%D0%BC%D0%BA%D0%B8%2C%20%D0%91%D0%B8%D0%B1%D0%BB%D0%B8%D0%BE%D1%82%D0%B5%D1%87%D0%BD%D0%B0%D1%8F%20%D0%A3%D0%BB%D0%B8%D1%86%D0%B0%2016%26phone%3D84957755505%26latitude%3D55%2C894361%26longitude%3D37%2C478212%26src%3D1; __store=117673_122258_122259_125238_125239_125240_6159_507_3158_117501_120602_120762_6158_124731_121709_130744_204939_159402_2737_117986_1733_686_132043_161812_1193_206968_206348_205228_172430_117442_117866; __region=80_68_64_83_4_38_33_70_82_69_86_75_30_40_48_1_22_66_31_71; __pricemargin=1.0--; __cpns=12_3_18_15_21; __dst=-1029256_-51490_12358263_123585548; __tm=1666899481; __sppfix=4; um=uid%3Dw7TDssOkw7PCu8K5wrfCsMK5wrTCsMKzwrA%253d%3Aproc%3D100%3Aehash%3D8249bb93d039be873a02732ef40a8424; _gid=GA1.2.1180592939.1666888682'
        driver.add_cookie({'name': 'WILDAUTHNEW_V3', 'value': WILDAUTHNEW_V3_my})
        driver.add_cookie({'name': 'x-supplier-id-external', 'value': '31f02447-2e52-418e-9cd0-fc714b75cda3'})
        driver.refresh()
        driver.get('https://www.wildberries.ru/')
        time.sleep(0)
    else:
        driver.get('https://cmp.wildberries.ru/campaigns/list/all')
        #x-supplier-id-external=c9640da8-a840-5484-bb00-dee7d6df69dd
        for cookie in pickle.load(open(f'F:\работа\Ноябрь 2022\WB реклама мой бот\Старый бот\dump\cookies_{phone}', 'rb')):
            try:
                cookie['domain'] = cookie['domain'].replace('www', '')
                driver.add_cookie(cookie)
            except Exception as e:
                print(cookie, e)
        driver.refresh()
        driver.get('https://cmp.wildberries.ru/campaigns/list/all')
    return driver

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


async def auth_account(session: AsyncSession, wb3token, supplier):
    """Авторизует аккаунт через wb3token и supplier"""
    headers = {'Cookie': f'WILDAUTHNEW_V3={wb3token}', 'Content-Type': 'application/json; charset=utf-8',
               'Accept-Encoding': 'gzip, deflate, br',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
               'Connection': 'keep-alive', }
    url = 'https://seller.wildberries.ru/passport/api/v2/auth/wild_v3_upgrade'
    data = {
        "device": "Macintosh"
    }
    data = json.dumps(data)
    print(headers)
    req = requests.post(url, headers=headers, data=data)

    WBToken = req.cookies.get_dict()['WBToken']
    print(WBToken)
    headers = {'Cookie': f'WBToken={WBToken};x-supplier-id={supplier};x-supplier-id-external={supplier}',
               'Content-Type': 'application/json; charset=utf-8', 'Accept-Encoding': 'gzip, deflate, br',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
               'Connection': 'keep-alive'}
    url = 'https://seller.wildberries.ru/passport/api/v2/auth/introspect'
    res = requests.get(url, headers=headers).text
    print(res)
    user_id = json.loads(res)
    args = {'WBToken':WBToken, 'wb_user_id': user_id['userID']}
    return 200, args


    # try:
    #     driver = get_open_browser()
    #     print('got driver')
    #     driver.get('https://www.wildberries.ru/')
    #     print(f'open wildberries  {wb3token}')
    #     driver.add_cookie({'name': 'WILDAUTHNEW_V3', 'value': wb3token})
    #     driver.add_cookie({'name': 'x-supplier-id-external', 'value': supplier})
    #     print('enter cookie')
    #     driver.refresh()
    #     save_cookies(driver, phone)
    #     print('save cookies')
    #     driver.get('https://cmp.wildberries.ru/campaigns/list/all')
    #     for cookie in pickle.load(open(f'F:\работа\Ноябрь 2022\WB реклама мой бот\Старый бот\dump\cookies_{phone}', 'rb')):
    #         try:
    #             cookie['domain'] = cookie['domain'].replace('www', '')
    #             driver.add_cookie(cookie)
    #         except Exception as e:
    #             print(cookie, e)
    #     print('load cookies')
    #     driver.refresh()
    #     driver.get('https://cmp.wildberries.ru/campaigns/list/all')
    #     check = 0
    #     print('start load after get')
    #     while check < 60:
    #         try:
    #             el = driver.find_element(By.CLASS_NAME, 'table--column--item')
    #             break
    #         except:
    #             await asyncio.sleep(2)
    #             check += 2
    #             print('wait')
    #     if check >= 60:
    #         driver.close()
    #         return False, None
    #     print('find')
    #    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "table--column--item item-0 ng-star-inserted"))).click()
    #     save_cookies(driver, phone)
    #     args = {'phone': phone}
    #     #s = input()
    #     res = api_auth(args)
    #     WBToken = res['sessionID']
    #     user_id = res['userID']
    #     args['wbtoken'] = WBToken
    #     args['wb_user_id'] = user_id
    #     args['wb3token'] = wb3token
    #     driver.close()
    #     print('Out login_acc')
    #     return True, args
    # except Exception as e:
    #     print(e)
    #     return False, None


def update_cookies(phone):
    driver = get_open_browser()
    driver = set_cookies(driver, phone)
    save_cookies(driver, phone)
    driver.close()


def add_new_cookies(phone, wb_cookie):
    cookies = pickle.load(open(f'F:\работа\Ноябрь 2022\WB реклама мой бот\Старый бот\dump\cookies_{phone}', 'rb'))
    for cookie in cookies:
        try:
            if cookie['name'] == 'WBToken':
                cookie['value'] = wb_cookie
        except:
            pass
    pickle.dump(cookies, open(f'F:\работа\Ноябрь 2022\WB реклама мой бот\Старый бот\dump\cookies_{phone}', 'wb'))



def get_open_browser():
    from seleniumwire import webdriver
    # logging.getLogger('WDM').setLevel(logging.NOTSET)
    print('open browser')
    # if len(user_agent) < 10:
    #     user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    # if len(proxy) > 10:
    #     part1, part2 = proxy.split('@')
    #     username, password = part1.split(':')
    #     ip, port = part2.split(':')
    #
    #     proxy = f'{username}:{password}@{ip}:{port}'
    #     options = {
    #         'proxy': {
    #             'https': f'https://{proxy}',
    #         },
    #         "backend": "mitmproxy",
    #         "disable_capture": True,
    #         "verify_ssl": False,
    #         "connection_keep_alive": False,
    #         "max_threads": 3,
    #         "connection_timeout": None,
    #         '--user-agent': user_agent,
    #         'mitm_http2': False
    #     }
    # else:
    # PROXY = '109.172.114.4:45785'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    options = {
            'disable_capture': True,
            '--user-agent': user_agent,
            'mitm_http2': False,
        }

    proxy_ip = "109.172.115.216"
    proxy_port = "50100"
    proxy_user = "Danilelmeyev"
    proxy_pass = "ZJDyT94Hpr"

    options_s = {
        'proxy': {
            "http": f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}/",
            "https": f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}/",
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    # add_proxy_zip()
    # pluginfile = 'proxy_auth_plugin.zip'
    # chrome_options.add_extension(pluginfile)
    # options_s = {
    #     'proxy': {
    #         'http': 'http://Danilelmeyev:ZJDyT94Hpr@109.172.115.216:50100',
    #         'https': 'https://Danilelmeyev:ZJDyT94Hpr@109.172.115.216:50100',
    #         'no_proxy': 'localhost,127.0.0.1'
    #     }
    # }

    # chrome_options.headless = True
    # print('GET BROW')
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=options_s)
    # options=chrome_options,
    #driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options, seleniumwire_options=options)
    print('GET BROW')
    driver.maximize_window()
    print('good')
    driver.get('https://www.google.com/')
    return driver


# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
#
# def get_open_browser():
#     PROXY = '109.172.114.4:45785'
#
#     options = webdriver.ChromeOptions()
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     options.add_argument("start-maximized")
#     options.add_argument("disable-infobars")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--proxy-server=%s" % PROXY)
#     options.headless = True
#     driver = webdriver.Chrome("/usr/bin/chromedriver", options=options)
#     #driver = webdriver.Chrome("/usr/bin/chromedriver", options=options)
#     #options.add_argument("--proxy-server=%s" % PROXY)
#     # options.headless = True
#     # print(2)
#     #
#     # driver = webdriver.Chrome(executable_path='/var/bots/chromedriver', options=options)
#     print('good')
#     return driver
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium import webdriver

# EXE_PATH = r'F:\работа\Ноябрь 2022\WB реклама мой бот\Старый бот\chromedriver.exe' # EXE_PATH это путь до ранее загруженного нами файла chromedriver.exe
# driver = webdriver.Chrome(executable_path=EXE_PATH)

def start_registration(driver, phone):
    try:
        driver.get('https://seller.wildberries.ru/')
        time.sleep(10)
        text = driver.find_element(By.CLASS_NAME, 'SimpleInput--vVIag')

        for i in str(phone):
            text.send_keys(i)
            time.sleep(0.1)

        time.sleep(5)
        el = driver.find_element(By.CLASS_NAME, 'Button--main---tdBh')
        el.click()
    except Exception as e:
        print(e)
        return driver, False
    return driver, True


def enter_code(driver, code):
    try:
        text = driver.find_element(By.CLASS_NAME, 'Accept-code__form-input--OAwQc')
        text.clear()
        time.sleep(0.5)
        for i in str(code):
            text.send_keys(i)
            time.sleep(0.1)
        time.sleep(5)
    except Exception as e:
        print(e)
        return False
    return driver


def check_code(driver):
    find = 'False'
    check = 0
    while check < 60:
        check += 1
        print(check)
        for i in driver.find_elements(By.CLASS_NAME, 'Button-link--list-item__04ggM6eg-E'):
            try:
                if i.get_attribute('href') == 'https://seller.wildberries.ru/new-goods':
                    return 'True'
            except:
                pass
        time.sleep(1)
    for i in driver.find_elements(By.CLASS_NAME, 'color-Violet--EA6MO'):
        try:
            if i.text == 'Неверные данные доступа':
                find = 'Code error'
        except:
            pass

    return find


def resend_code(driver):
    btn = driver.find_element(By.ID, 'requestCode')
    btn.click()
    #return driver


def check_valid_acc(phone):
    res = api_auth({'phone': phone})
    try:
        WBToken = res['sessionID']
        user_id = res['userID']
        return True
    except:
        return False


async def update_wbtoken(session: AsyncSession, phone: int):
    wbacc = await get_wbaccount(session, phone)
    complete, args = await save_cookie_from_wb3token(session, phone, wbacc.wb3token)
    if complete:
        await update_wb_account(session, phone, args)
        return True
    else:
        return False
