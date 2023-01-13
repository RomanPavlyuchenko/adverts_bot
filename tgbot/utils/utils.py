import asyncio
import json
import re
from bs4 import BeautifulSoup
import httpx
import requests
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.models.tables import Campaigns, WBAccounts
from tgbot.services.db_queries import add_default_campaign, get_wbaccount, update_campaign
from tgbot.services.wb import common
from tgbot.services.wb.common import TIMEOUT
from tgbot.services.wb.wb import get_adverts_by_query_search, get_adverts_by_scu_inline
from tgbot.utils.wb_api import get_all_campaigns, api_get_budget, get_words_by_search, \
    api_get_exist_keywords, get_ad_info, get_cookies_phone, get_adverts_strange_method, get_code_wb

c = 'BasketUID=62cf91b6-c80d-4fee-ac6e-e44c89c434d6; _wbauid=3717703611654951772; _ga=GA1.2.937760077.1654951773; ___wbu=5ea8e470-400c-4aa4-bb76-6d3b534cc520.1656610871; __bsa=basket-ru-42; SL_C_23361dd035530_DOMAIN=true; _gcl_au=1.1.336928433.1662749323; __pricemargin=1.0--; __sppfix=; x-supplier-id-external=c9640da8-a840-5484-bb00-dee7d6df69dd; WILDAUTHNEW_V3=E64E6110F305C403E6369F38807E9955CD9EC7B4779692D6CE72C697F2FDE38379C4F8F92EF8992F49B80799A5861B492FD3D021350B2511E0B49C3D03C34C139FDBD3233BEB329167EDF2BC0CC680A9D9740922D93EEB9F0FA3B248BC95CAED9D2B72B99A55941EE99E0BD38CD087A946358AE4E271FD6EAA2E131487A923B96BEB9133BB929DFB5611B941FFDD192F7F6CF031AF70C7B66B570DCEFCCE8C7CE477B592B92F86E13FFF39E35DCC10CF8880828A5627F7D6E360F994BFD1C41C606A57AB88EE0DEADB21097D84658F4ABA98B66F633577A97FBE676BE551B4E87603C1753A18EA3573C312A52B610DE601270AAB1BABD1A804890DE36618D1881F93E31276A619759619E7A1576829F19D4AFD958BADDE290AA17121EDEECCBFD0C23EC69D4AAFCCF9A2472AC5C3C2FDF8AA8E18BADDCDF7AB1638BB46C1BE76190DDBD9C85FD64C70B7DC12F0098CAAA7170428; __wbl=cityId%3D0%26regionId%3D0%26city%3D%D0%B3%20%D0%A5%D0%B8%D0%BC%D0%BA%D0%B8%2C%20%D0%91%D0%B8%D0%B1%D0%BB%D0%B8%D0%BE%D1%82%D0%B5%D1%87%D0%BD%D0%B0%D1%8F%20%D0%A3%D0%BB%D0%B8%D1%86%D0%B0%2016%26phone%3D84957755505%26latitude%3D55%2C894361%26longitude%3D37%2C478212%26src%3D1; __store=117673_122258_122259_125238_125239_125240_6159_507_3158_117501_120602_120762_6158_124731_121709_130744_204939_159402_2737_117986_1733_686_132043_161812_1193_206968_206348_205228_172430_117442_117866; __region=80_68_64_83_4_38_33_70_82_69_86_75_30_40_48_1_22_66_31_71; __cpns=12_3_18_15_21; __dst=-1029256_-51490_12358263_123585548; __tm=1665973886; WBToken=AqGpjCmizpW1DKKsyrUMMoCwfEnF5ldEcFu1It818yNDl6Lvt7unRcQc3kh_x4J7083RyxmiMvdNQzkoIwV8y1jT'
cookies = {i.split('=')[0]: i.split('=')[1] for i in c.split('; ')}


class CampaignIsActive:

    campaigns = {} #{'is_active': is_active, 'pos': pos, 'price': price}

    def __init__(self):
        name = 'bot'

    def add_campaign(self, campaign_id, is_active, pos):
        try:
            _ = self.campaigns[campaign_id]
        except:
            self.campaigns[campaign_id] = {'is_active': is_active, 'pos': pos, 'price': 0}

    def get_is_active_campaign(self, campaign_id):
        return self.campaigns[campaign_id]['is_active']

    def set_is_active_campaign(self, campaign_id, is_active):
        self.campaigns[campaign_id]['is_active'] = is_active

    def get_pos_campaign(self, campaign_id):
        return self.campaigns[campaign_id]['pos']

    def set_pos_campaign(self, campaign_id, pos):
        self.campaigns[campaign_id]['pos'] = pos

    def get_price_campaign(self, campaign_id):
        return self.campaigns[campaign_id]['price']

    def set_price_campaign(self, campaign_id, price):
        self.campaigns[campaign_id]['price'] = price

    def del_campaigns(self, campaign_id):
        del self.campaigns[campaign_id]


campaign_is_active = CampaignIsActive()




def get_companies_by_name(phone, name):
    res = []
    for i in get_all_campaigns(phone):
        print(i)
        if name in i['campaignName']:
            res.append({'id': i['id'], 'name': i['campaignName'], 'type': i['categoryName']})
    return res


def get_company_info(params: dict):
    # res = get_ad_info(params)
    try:
        print('запустился апи бюджет')
        balance = api_get_budget(params)['total']
        res = {'balance': balance}
        return res
    except:
        return None

async def auth():
    wb3 = '7E9CFC7379820C6C3A7D11392DBA507009FCFBA4AD6D965FE4E241DF5E0E86BB20032F7990F38B3945634C6962B9F3228269E5C805F3F6E3AD1411238CF9662D86A1987AC74DB420D7E566D0F67FA0C4BAF39CAAC2F23CA00257426A3E07BB598EED9F2EE372C3E8547624033FA64D6B6F341B22666C78ADA916A7C7210B46CE0A494F135B51C5D3B0D7A9C21361D909827D772BB4FF6DF4E27E6784FBE348625219AAE9C92C61D569E972E006552EFE1F155C5C0B02D9D553A1697EE1B9EB6B1CB122CCC3CE0EFE7402FE5E632B171F83B5CB5DAA9DBA7893084B514B7C5A4A4C10CA6796BA9C4D097D41F748CB80841C9F9AB314E6E45064AA4A3D9EC460F372881FC265A0EEFB1316D913C6A305B681CF2A4309BA1EDAA4CC6B0C65E3DDEB6C165060CF4DC5C26ECAF5A0D9C476D487007B9A'
    phone = '+79181015645'
    token = await send_code_phone(phone)
    code_data = await get_code_wb(wb3)
    code = await parse_code(code_data)
    WBToken = await send_code_auth(code, token)
    return 200, WBToken

async def send_code_phone(phone: str):
    url = 'https://cmp.wildberries.ru/passport/api/v2/auth/login_by_phone'
    body = '{"phone":"79181015645","is_terms_and_conditions_accepted":true}'
    try:
        resp = requests.post(url, data=body).text
        token = json.loads(resp)
        token = token['token']
        return token
    except:
        return False
    return token

async def send_code_auth(code, token):
    url = 'https://cmp.wildberries.ru/passport/api/v2/auth/login'
    data = {"options":{"notify_code":f"{code}"}, "token": f"{token}","device":"Windows,Mozilla Firefox 109.0"}
    data = json.dumps(data)
    try:
        resp = requests.post(url, data=data)
        WBToken = resp.cookies.get_dict()['WBToken']
        return WBToken
    except:
        return False

async def parse_code(data):
    for i in data['value']['events']:
        soup = BeautifulSoup(i['message'], 'html.parser')
        code_all = soup.findAll('span')
        code = re.findall(r'\d+', code_all[1].get_text())
        return code[0]



async def update_campaign_balance(session, args: dict):
    try:
        balance = api_get_budget(args)['total']
        args['balance'] = balance
        await update_campaign(session, args['campaign_id'], args)
    except Exception as e:
        print('utils, update_campaign_balance', e)


def make_auto_pay():
    pass


def check_phone(phone) -> int:
    phone = phone.replace('+', '')
    if len(phone) == 11:
        if phone[0] not in ['7', '8']:
            return 0
        else:
            phone = phone[1:]
            # phone = '8' + phone
            try:
                return int(phone)
            except:
                return 0

    elif len(phone) == 10:
        try:
            # phone = '8' + phone
            return int(phone)
        except:
            return 0
    else:
        return 0


def generate_keywords(search_phrase) -> dict:
    res = get_words_by_search(search_phrase)
    result = {}
    for i in range(len(res)):
        result[i] = {'keyword': res[i]['name']}
    return result


def get_exist_phrases_and_excluded(args) -> [dict, list]:
    try:
        args['campaign_id'] = args['company_id']
        print(args)
        keywords, excluded = api_get_exist_keywords(args)
        print(keywords, excluded)
        result = {}
        for i in range(len(keywords)):
            result[i] = {'keyword': keywords[i]['keyword'], 'count': keywords[i]['count']}

        return result, excluded
    except Exception as e:
        print('get_exist_phrases_and_excluded', e)
        return None, None


async def set_new_price_campaign(campaign: Campaigns, wbacc: WBAccounts):
    # Referer: https://cmp.wildberries.ru/campaigns/list/all/edit/{campaign.type}/{campaign.campaign_id}
    url = f'https://cmp.wildberries.ru/backend/api/v2/{campaign.type}/{campaign.campaign_id}/save'
    headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Length: 603
Content-Type: application/json
Host: cmp.wildberries.ru
Origin: https://cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/pause/edit/search/{campaign.campaign_id}
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
Cookie: WBToken={wbacc.wbtoken};x-supplier-id={wbacc.supplier_id};x-supplier-id-external={wbacc.supplier_id}
X-User-Id: {wbacc.wb_user_id}'''
    headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
    args = {'phone': wbacc.phone, 'wb_user_id': wbacc.wb_user_id, 'WBToken':wbacc.wbtoken, 'supplier':wbacc.supplier_id}
    ad_info = await get_ad_info(campaign, args)
    print('ad_info', ad_info)
    subjectId = ad_info['subjectId']
    price = ad_info['price']

    max_pos = await get_position_by_limit(campaign)
    need_pos = campaign.place
    result = ''
    if max_pos != 0:
        if need_pos >= max_pos:  # all good
            new_price = await get_price_by_position(campaign, need_pos)
            print(f'old price {price}, new price {new_price}')
            result = f'good:{need_pos}'
            # return f'GOOD, old price {price}, new price {new_price}'
        else:  # need change position down
            new_price = await get_price_by_position(campaign, max_pos) #NONE ???
            print(f'OUT OF LIMIT {campaign.limit}, old price {price}, new price {new_price}, new_pos {max_pos}')
            result = f'down:{max_pos}'
            # return f'OUT OF LIMIT {campaign.limit}, old price {price}, new price {new_price}, new_pos {max_pos}'
        campaign_is_active.set_price_campaign(campaign.campaign_id, new_price)
        if int(price) == int(new_price):
            print('price the same')
            return True, result


        if campaign.type == 'search':
            keyword = ad_info['keyWord']
            searchElements = [{'active': True, 'brand': i['brand'], 'name': i['name'], 'nm': i['nm']} for i in ad_info['searchElements']]
            payload = {'name': 'трусы женские', 'status': 9, 'place': [
                {'keyWord': keyword, 'subjectId': subjectId, 'price': new_price,
                'searchElements': searchElements}]}

        if campaign.type == 'carousel-auction':
            subject = ad_info['subject']
            carouselElements = [{'active': True, 'brand': i['brand'], 'name': i['name'], 'nm': i['nm']} for i in ad_info['carouselElements']]

            payload = {"minCPM": 50, "stepCPM": 1, "excludedBrands": [],
                       "locale": [643], "place": [
                    {"subjectId": subjectId, "subject": subject, "kindId": ad_info['kindId'],
                     "kind": ad_info['kind'],
                     "price": new_price, "carouselElements": carouselElements,
                     "intervals": []}], "nmsCount": 1, "name": campaign.campaign_name, "status": 9}

        if campaign.type == 'catalog':
            pass
        print(payload)
        res = requests.put(url=url, headers=headers_, json=payload, timeout=TIMEOUT * 2)
        print('#########\n\n\nset_new_price_campaign', campaign.campaign_id, res, '\n\n\n#########')
        print(res.text)
        if res.status_code == 200:
            return True, result
        else:
            return False, result
    else:  # out of limit
        #await stop_campaign(campaign)
        print(f'OUT OF LIMIT {campaign.limit}, stop campaign')
        result = 'out of limit'
        return False, result
        # return f'OUT OF LIMIT {campaign.limit}, stop campaign'


async def get_price_by_position(campaign: Campaigns, pos: int):
    headers = common.get_headers()

    if campaign.type == 'search':
        result = get_adverts_strange_method(campaign.keywords)
        price = result[pos - 1]['cpm']


        # async with AsyncClient(headers=headers, timeout=common.TIMEOUT) as client:
        #     adverts, positions = await get_adverts_by_query_search(client, campaign.keywords)
        # pos1 = positions[0]['positions'][pos - 1]
        # price = adverts[pos1]["cpm"]
        return price + 1
    if campaign.type == 'carousel-auction':
        async with AsyncClient(headers=headers, timeout=common.TIMEOUT) as client:
            prices_with_position, scu = await get_adverts_by_scu_inline(client, campaign.sku)

        for price, position in prices_with_position.items():
            if len(position) > 1:
                if position[0] <= pos <= position[-1]:
                    return price
            else:
                if pos == position[0]:
                    return price
        return 50 # 3 places, need 4

    if campaign.type == 'catalog':
        pass


async def get_position_by_limit(campaign: Campaigns):
    headers = common.get_headers()

    if campaign.type == 'search':
        result = get_adverts_strange_method(campaign.keywords)
        pos = 0
        print(result)
        for i in result:
            pos += 1
            if campaign.limit >= i['cpm']:
                return pos
        return 0
        # async with AsyncClient(headers=headers, timeout=common.TIMEOUT) as client:
        #     adverts, positions = await get_adverts_by_query_search(client, campaign.keywords)
        # s = [adverts[i]['cpm'] for i in positions[0]['positions']]
        # print('adverts, positions', s, positions)
        # for i in positions[0]['positions']:
        #     if campaign.limit >= adverts[i - 1]['cpm']:
        #         return i
        # return 0
    if campaign.type == 'carousel-auction':
        async with AsyncClient(headers=headers, timeout=common.TIMEOUT) as client:
            prices_with_position, scu = await get_adverts_by_scu_inline(client, campaign.sku)

        print(prices_with_position)
        for price, position in prices_with_position.items():

            if price <= campaign.limit:
                return position[0]
        return 0


async def async_get_and_save_default_campaigns(session: AsyncSession, phone: int, wb_user_id: int, WBToken:str, supplier:str, important=True):
    """Получает все кампании и сохраняет в бд"""
    args = {'phone': phone, 'wb_user_id': wb_user_id, 'WBToken': WBToken, 'x-supplier-id': supplier}
    campaigns = get_all_campaigns(args, important)
    if campaigns:
        print(campaigns)
        await add_default_campaign(session, phone, campaigns)
