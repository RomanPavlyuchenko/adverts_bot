import asyncio
import pickle
import json
import aiohttp
import requests

from tgbot.models.tables import Campaigns, WBAccounts
from tgbot.services.wb.common import TIMEOUT


def get_cookies_phone(phone):
    arr_cook = {}
    for cookie in pickle.load(open(f'F:\работа\Ноябрь 2022\WB реклама мой бот\Старый бот\dump\cookies_{phone}', 'rb')):
        arr_cook[cookie['name']] = cookie['value']
    return arr_cook




# async def get_all_campaigns(phone):
#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         for i in category:
#             task1 = asyncio.create_task(parse_products(session, 0, i, published, 'DATE_PUBLISHED_DESC'))
#             tasks.append(task1)
#         res = await asyncio.gather(*tasks)


def get_all_campaigns(args: dict, important=True):
    if important:
        x = 5
    else:
        x = 1
    for i in range(x):
        try:
            phone = args['phone']
            wb_user_id = args['wb_user_id']
            headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Cookie: WBToken={args['WBToken']};x-supplier-id={args['x-supplier-id']};x-supplier-id-external={args['x-supplier-id']}
Referer: https://cmp.wildberries.ru/campaigns/list/all
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
X-User-Id: {wb_user_id}'''

            url = 'https://cmp.wildberries.ru/backend/api/v3/atrevds?pageNumber=1&pageSize=100&search=&status=%5B0,11,1,15,2,4,9,3,14,16,6,17,5,10,13,12,7,8%5D&order=createDate&direction=desc&type=%5B2,3,4,5,6,7%5D'
            headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
            print('start get_all_campaigns', phone)
            res = requests.get(url=url, headers=headers_, timeout=TIMEOUT)
            print('get_all_campaigns', res)
            if res.status_code == 200:
                print(res.json()['content'])
                return res.json()['content']
            else:
                return None
        except Exception as e:
            print('get_all_campaigns', e)
            return None


def get_active_campaigns():
    """GET"""
    url = 'https://cmp.wildberries.ru/backend/api/v3/atrevds?pageNumber=1&pageSize=100&search=&status=%5B1,15,2,4,9,3,14,16,6,17,5,10,13,12%5D&order=null&direction=null&type=%5B2,3,4,5,6,7%5D'


def get_pause_campaigns():
    """GET"""
    url = 'https://cmp.wildberries.ru/backend/api/v3/atrevds?pageNumber=1&pageSize=100&search=&status=%5B11%5D&order=pauseDate&direction=desc&type=%5B2,3,4,5,6,7%5D'


def get_archive_campaigns():
    """GET"""
    url = 'https://cmp.wildberries.ru/backend/api/v3/atrevds?pageNumber=1&pageSize=100&search=&status=%5B7,8%5D&order=disableDate&direction=desc&type=%5B2,3,4,5,6,7%5D'


def send_code_phone(phone: str):
    url = 'https://cmp.wildberries.ru/passport/api/v2/auth/login_by_phone'
    body = '{"phone":"79246049032","is_terms_and_conditions_accepted":true}'
    try:
        resp = requests.post(url, data=body).text
        token = json.loads(resp)
        token = token['token']
        return token
    except:
        return False
    return token

async def get_code_wb(WB3Token: str):
    headers = {"Host": "www.wildberries.ru",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
"Accept": "*/*",
"Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
"Accept-Encoding": "gzip, deflate, br",
"Referer": "https://www.wildberries.ru/lk/newsfeed/events",
# "x-requested-with": "XMLHttpRequest",
# "x-spa-version":"9.3.70.1",
"Origin": "https://www.wildberries.ru",
"Connection": "keep-alive",
"Cookie":  f"WILDAUTHNEW_V3={WB3Token}",
"Sec-Fetch-Mode": "cors",
"Sec-Fetch-Site": "same-origin",
"Content-Length": "0"}

    data = {}
    url = 'https://www.wildberries.ru/webapi/lk/newsfeed/events/data?'
    resp = requests.post(url=url, headers=headers, data=data).text
    resp = json.loads(resp)
    return resp



async def get_ad_info(campaign: Campaigns, args: dict):
    print('start get_ad_info')
    phone = args['phone']
    wb_user_id = args['wb_user_id']
    url = f'https://cmp.wildberries.ru/backend/api/v2/{campaign.type}/{campaign.campaign_id}/placement'
    print(url)
    headers_ = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
                'Accept': 'application/json',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'X-User-Id': str(args['wb_user_id']),
                'Cache-control': 'no-store',
                'Content-Type': 'application/json',
                'Connection': 'keep-alive',
                # 'Referer': f'https://cmp.wildberries.ru/campaigns/list/pause/edit/search/{campaign.campaign_id}',
                'Referer': f'https://cmp.wildberries.ru/campaigns/list/all/edit/{campaign.type}/{campaign.campaign_id}',
                'Cookie': f'WBToken={args["WBToken"]}; x-supplier-id-external={args["supplier"]}',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin'}
    print(headers_)
    res = requests.get(url=url, headers=headers_, timeout=TIMEOUT)
    print(res)
    print(res.text)
    data = {}
    try:
        res = res.json()

        place = res['place'][0]
    #data['entryPrices'] = place['placesInfo']['entryPrices']
    #data['estimatedPlaces'] = place['placesInfo']['estimatedPlaces']

        searchElements = []
        for info in place['searchElements']:
            searchElements.append({'brand': info['brand'], 'name': info['name'], 'nm': info['nm']})
        data['searchElements'] = searchElements
        data['keyWord'] = place['keyWord']
    except:
        carouselElements = []
        for info in place['carouselElements']:
            carouselElements.append({'brand': info['brand'], 'name': info['name'], 'nm': info['nm']})
        data['carouselElements'] = carouselElements
        data['subject'] = place['subject']
        data['kind'] = place['kind']
        data['kindId'] = place['kindId']

    data['subjectId'] = place['subjectId']
    data['price'] = place['price']
    return data

async def api_get_campaign_by_id(args: dict):
    print('api_get_campaign_by_id')
    campaign_id = args.get("company_id", args["campaign_id"])
    phone = args['phone']
    wb_user_id = args['wb_user_id']
    for company_type in ['search', 'carousel-auction', 'catalog']:
        try:
            await asyncio.sleep(1)
            url = f'https://cmp.wildberries.ru/backend/api/v2/{company_type}/{campaign_id}/placement'
            headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/all/edit/{company_type}/{campaign_id}
Cookie: WBToken={args['WBToken']};x-supplier-id={args['x-supplier-id']};x-supplier-id-external={args['x-supplier-id']}
sec-ch-ua: "Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36
X-User-Id: {wb_user_id}'''
            headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
            try:
                res = requests.get(url=url, headers=headers_, cookies=get_cookies_phone(phone), timeout=TIMEOUT)
            except Exception as e:
                print(e)
            print(res)
            print(res.text)
            print(res.status_code == 200)
            if res.status_code == 200:
                print('good')

                res = res.json()
                data = {}
                data['name'] = res['name']
                data['status'] = res['status']
                data['id'] = int(campaign_id)
                data['type'] = company_type
                place = res['place'][0]
                # data['entryPrices'] = place['placesInfo']['entryPrices']
                # data['estimatedPlaces'] = place['placesInfo']['estimatedPlaces']
                try:
                    info = place['searchElements'][0]
                    data['keyWord'] = place['keyWord']
                except:
                    info = place['carouselElements'][0]
                    data['subject'] = place['subject']
                data['brand'] = info['brand']
                data['nm'] = info['nm']
                data['subjectId'] = place['subjectId']
                data['price'] = place['price']

                return data
        except Exception as e:
            print(e)
    return None


def api_get_budget(args):
    phone = args['phone']
    wb_user_id = args['wb_user_id']
    headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/all/edit/{args["company_type"]}/{args.get("company_id", args['campaign_id'])}
sec-ch-ua: "Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36
Cookie: WBToken={args['WBToken']};x-supplier-id={args['supplier']};x-supplier-id-external={args['supplier']}
X-User-Id: {wb_user_id}'''
    headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}

    url = f'https://cmp.wildberries.ru/backend/api/v2/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}/budget'
    res = requests.get(url=url, headers=headers_, timeout=TIMEOUT)
    print('api_get_budget', res)
    print(res.text)
    if res.status_code == 200:
        return res.json()
    else:
        return None

def api_get_balance(args: dict):
    phone = args['phone']
    wb_user_id = args['wb_user_id']
    url = 'https://cmp.wildberries.ru/backend/api/v3/balance'
    headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/all
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
Cookie: WBToken={args['WBToken']};x-supplier-id={args['supplier']};x-supplier-id-external={args['supplier']}
X-User-Id: {wb_user_id}'''
    headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}

    res = requests.get(url=url, headers=headers_, timeout=TIMEOUT)
    print(res)
    print(res.text)
    return res.json()['content']['net']


def api_auth(args):
    phone = args['phone']
    url = 'https://cmp.wildberries.ru/passport/api/v2/auth/introspect'
    headers_ = '''Accept: application/json, text/plain, */*
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Connection: keep-alive
Host: cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/all
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'''
    headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}

    res = requests.get(url=url, headers=headers_, cookies=get_cookies_phone(phone), timeout=TIMEOUT)
    print(res)
    print(res.text)
    return res.json()


async def api_add_balance(args):

    phone = args['phone']
    wb_user_id = args['wb_user_id']
    url = f'https://cmp.wildberries.ru/backend/api/v2/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}/budget/deposit'
    headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Origin: https://cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/all/edit/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
Cookie: WBToken={args['WBToken']};x-supplier-id={args['supplier']};x-supplier-id-external={args['supplier']}
X-User-Id: {wb_user_id}'''
    headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
    payload = {'sum': args['append_balance'], 'type': 1}
    try:
        res = requests.post(url=url, headers=headers_, json=payload, timeout=TIMEOUT * 3)
        print(res)
        print(res.text)
        return True
    except Exception as e:
        print('api_add_balance', e)
        return False


def set_excluded_words(args: dict, words: list):
    """POST"""
    url = f'https://cmp.wildberries.ru/backend/api/v2/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}/set-excluded'
    headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Origin: https://cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/pause/edit/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
Cookie: WBToken={args['WBToken']};x-supplier-id={args['supplier']};x-supplier-id-external={args['supplier']}
X-User-Id: {args["wb_user_id"]}'''
    headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
   # payload = {'excluded': [{i: j} for i, j in zip(range(len(words)), words)]}
    payload = {'excluded': words}
    #print(payload)
    res = requests.post(url=url, headers=headers_, json=payload, timeout=TIMEOUT * 3)
    print('Send_set_exluced words', res)
    print(res.text)



def get_words_by_search(keyword):
    url = 'https://search.wb.ru/suggests/api/v3/hint'
    headers = '''User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36'''
    payload = {'query': keyword, 'gender': 'male', 'locale': 'ru', 'lang': 'ru'}
    headers = {i.split(':')[0]: i.split(': ')[1] for i in headers.split('\n')}
    res = requests.get(url=url, headers=headers, params=payload, timeout=TIMEOUT).json()
    result = []
    for i in res:
        if i['type'] == 'suggest':
            result.append(i)
    return result


def api_get_exist_keywords(args):
    phone = args['phone']
    wb_user_id = args['wb_user_id']
    url = f'https://cmp.wildberries.ru/backend/api/v2/search/{args.get("company_id", args["campaign_id"])}/words'
    headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/all/edit/search/{args.get("company_id", args["campaign_id"])}
sec-ch-ua: "Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36
Cookie: WBToken={args['WBToken']};x-supplier-id={args['supplier']};x-supplier-id-external={args['supplier']}
X-User-Id: {wb_user_id}'''
    headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
    res = requests.get(url=url, headers=headers_, timeout=TIMEOUT)
    print('api_get_exist_keywords', res)
    return res.json()['keywords'], res.json()['excluded']


def get_real_price(keyword):
    url = 'https://catalog-ads.wildberries.ru/api/v5/search'
    headers = '''User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'''
    payload = {'keyword': keyword}
    headers = {i.split(':')[0]: i.split(': ')[1] for i in headers.split('\n')}
    res = requests.get(url=url, params=payload, timeout=TIMEOUT).json()
    print(res['pages'][0]['positions'])
    for i in res['pages'][0]['positions']:
        print(i, res['adverts'][i]['id'], res['adverts'][i]['cpm'])
    # for i in res['adverts']:
    #     print(i['id'], i['cpm'])
    # print(res['pages'][0]['positions'])


async def api_stop_campaign(args: dict):
    try:
        url = f'https://cmp.wildberries.ru/backend/api/v2/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}/pause'
        headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/all/edit/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
Cookie: WBToken={args['WBToken']};x-supplier-id={args['supplier']};x-supplier-id-external={args['supplier']}
X-User-Id: {args["wb_user_id"]}'''
        headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
        res = requests.get(url=url, headers=headers_, timeout=TIMEOUT)
        print(res)
        return True
    except Exception as e:
        print('api_stop_campaign', e)
        return False


async def api_start_campaign(campaign: Campaigns, args: dict):
    phone = args['phone']
    wb_user_id = args['wb_user_id']
    url = f'https://cmp.wildberries.ru/backend/api/v2/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}/placement'
    headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Origin: https://cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/all/edit/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
Cookie: WBToken={args['WBToken']};x-supplier-id={args['supplier']};x-supplier-id-external={args['supplier']}
X-User-Id: {wb_user_id}'''
    ad_info = await get_ad_info(campaign, args)
    subjectId = ad_info['subjectId']
    price = ad_info['price']
    balance = api_get_budget(args)['total']

    if args["company_type"] == 'search':
        keyword = ad_info['keyWord']
        searchElements = [{'active': True, 'brand': i['brand'], 'name': i['name'], 'nm': i['nm']} for i in
                          ad_info['searchElements']]
        payload = {"budget": {"total": balance, "dailyMax": 0}, "minCPM": 50, "stepCPM": 1, 'name': 'трусы женские', 'status': 11, 'place': [
            {'keyWord': keyword, 'subjectId': subjectId, 'price': price,
             'searchElements': searchElements}]}

    if args["company_type"] == 'carousel-auction':
        subject = ad_info['subject']
        carouselElements = [{'active': True, 'brand': i['brand'], 'name': i['name'], 'nm': i['nm']} for i in
                            ad_info['carouselElements']]

        payload = {"budget": {"total": balance, "dailyMax": 0}, "minCPM": 50, "stepCPM": 1, "excludedBrands": [],
                   "locale": [643], "place": [
                {"subjectId": subjectId, "subject": subject, "kindId": ad_info['kindId'],
                 "kind": ad_info['kind'],
                 "price": price, "carouselElements": carouselElements,
                 "intervals": []}], "nmsCount": 1, "name": campaign.campaign_name, "status": 11}
    headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
    try:
        res = requests.put(url=url, headers=headers_, json=payload, timeout=TIMEOUT * 2)
        print(res)
        print(res.text)
        if res.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print('api_start_campaign', e)
        return False


def api_set_new_price(args):
    phone = args['phone']
    wb_user_id = args['wb_user_id']
    url = f'https://cmp.wildberries.ru/backend/api/v2/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}/save'
    headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Length: 603
Content-Type: application/json
Host: cmp.wildberries.ru
Origin: https://cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/all/edit/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
Cookie: WBToken={args['WBToken']};x-supplier-id={args['supplier']};x-supplier-id-external={args['supplier']}
X-User-Id: {wb_user_id}'''
    headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
    ad_info = {'subject': 'Юбки', 'brand': 'VIVANT', 'name': 'Юбка женская мини на запах с воланом', 'nm': 58949124, 'subjectId': 38, 'price': 51}
    data = {"budget":{"total":300,"dailyMax":0},"minCPM":50,"stepCPM":1,"excludedBrands":[],"locale":[643],"place":[{"subjectId":38,"subject":"Юбки","kindId":2,"kind":"для женщин","price":args['new_price'],"carouselElements":[{"nm":58949124,"name":"Юбка женская мини на запах с воланом","brand":"VIVANT"}],"intervals":[]}],"nmsCount":1,"name":"юбка волан хэллуин","status":11}
    res = requests.put(url=url, headers=headers_, json=data, timeout=TIMEOUT)
    print(res)


async def api_get_stat_campaign(args: dict):
    print('start api_get_stat_campaign')
    try:
        phone = args['phone']
        wb_user_id = args['wb_user_id']
        url = f'https://cmp.wildberries.ru/backend/api/v2/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}/stat'
        headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/all/edit/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
Cookie: WBToken={args['WBToken']};x-supplier-id={args['supplier']};x-supplier-id-external={args['supplier']}
X-User-Id: {wb_user_id}'''

        headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
        res = requests.get(url=url, headers=headers_, timeout=TIMEOUT)
        print(res)
        return res.json()
    except Exception as e:
        print('api_get_stat_campaign', e)





class SearchEngineAdvert:
    def __init__(self, selected_cards: list, list_all_adverts: list, positions: list):
        self._list_all_adverts = list_all_adverts
        self._positions = positions
        # self._query = query
        self._selected_cards = selected_cards

    def get_adverts_card(self):
        # format_query = self._format_query(self._query)
        # ads_cards = SelectedCard(format_query)
        # selected_adverts_first_page = ads_cards.get_card_id_selected_card()
        selected_adverts_first_page = self._selected_cards
        result_from_first_page = self._diff_selected_adverts_with_all_adverts(
            selected_adverts=selected_adverts_first_page,
            all_adverts=self._list_all_adverts,
            positions=self._positions[0]["positions"]
        )
        return result_from_first_page

    @staticmethod
    def _find_adverts_card_in_page(response) -> list:
        adverts = response.html.find(".advert-card-item")
        selected_adverts = []
        for advert in adverts:
            selected_adverts.append(advert.attrs.get("data-popup-nm-id"))
        return selected_adverts

    def _format_query(self, query):
        return "+".join(query.split())

    @staticmethod
    def _diff_selected_adverts_with_all_adverts(
            selected_adverts: list[str],
            all_adverts: list[dict],
            positions: list):
        result = []
        for index, position in enumerate(positions):
            for advert in all_adverts:
                try:
                    if int(selected_adverts[index]) == advert.get("id"):
                        result.append(Advert(position=position, card_id=int(selected_adverts[index]), cpm=advert["cpm"]))
                except IndexError:
                    break
        return result


def get_adverts_strange_method(query: str):  # , list_adverts: list, positions: list):
    resp = requests.get(f"https://catalog-ads.wildberries.ru/api/v5/search?keyword={query}")
    page_as_json = resp.json()
    sa = page_as_json.get("adverts")
    cpm_list = [b.get('cpm') for b in sa]
    adverts = [a for a in sa if a.get('cpm')]
    positions = page_as_json.get("pages")[0].get('positions')
    result = []
    for i, p in enumerate(positions):
        try:
            result.append({'position': p, 'card_id': int(adverts[i].get('advertId')), 'cpm': adverts[i].get('cpm')})
        except:
            pass
    text = f"Ваш запрос: <b>{query}</b>\n\nПозиции и цена:\n"  # <b>1-ая страница</b>\n"
    return result


async def api_save(campaign: Campaigns, args: dict):
    phone = args['phone']
    wb_user_id = args['wb_user_id']
    url = f'https://cmp.wildberries.ru/backend/api/v2/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}/save'
    headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Origin: https://cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/all/edit/{args["company_type"]}/{args.get("company_id", args["campaign_id"])}
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
Cookie: WBToken={args['WBToken']};x-supplier-id={args['supplier']};x-supplier-id-external={args['supplier']}
X-User-Id: {wb_user_id}'''
    ad_info = await get_ad_info(campaign, args)
    subjectId = ad_info['subjectId']
    price = ad_info['price']
    balance = api_get_budget(args)['total']

    if args["company_type"] == 'search':
        keyword = ad_info['keyWord']
        searchElements = [{'active': True, 'brand': i['brand'], 'name': i['name'], 'nm': i['nm']} for i in
                          ad_info['searchElements']]
        payload = {"budget": {"total": balance, "dailyMax": 0}, "minCPM": 50, "stepCPM": 1, 'name': 'трусы женские', 'status': 11, 'place': [
            {'keyWord': keyword, 'subjectId': subjectId, 'price': price,
             'searchElements': searchElements}]}

    if args["company_type"] == 'carousel-auction':
        subject = ad_info['subject']
        carouselElements = [{'active': True, 'brand': i['brand'], 'name': i['name'], 'nm': i['nm']} for i in
                            ad_info['carouselElements']]

        payload = {"budget": {"total": balance, "dailyMax": 0}, "minCPM": 50, "stepCPM": 1, "excludedBrands": [],
                   "locale": [643], "place": [
                {"subjectId": subjectId, "subject": subject, "kindId": ad_info['kindId'],
                 "kind": ad_info['kind'],
                 "price": price, "carouselElements": carouselElements,
                 "intervals": []}], "nmsCount": 1, "name": campaign.campaign_name, "status": 11}
    headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
    try:
        res = requests.put(url=url, headers=headers_, json=payload, timeout=TIMEOUT * 2)
        print(res)
        print(res.text)
        if res.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print('api_start_campaign', e)
        return False
