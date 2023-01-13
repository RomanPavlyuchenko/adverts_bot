import json
import time

from bs4 import BeautifulSoup
import requests
import re


# def auth(WB3, supplier):
#     headers = {'Cookie': f'WILDAUTHNEW_V3={WB3}','Content-Type':'application/json; charset=utf-8',
#                'Accept-Encoding':'gzip, deflate, br', 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
#                'Connection': 'keep-alive',}
#     url = 'https://seller.wildberries.ru/passport/api/v2/auth/wild_v3_upgrade'
#     data = {
#         "device": "Macintosh"
#     }
#     data = json.dumps(data)
#     # print(headers)
#     req = requests.post(url, headers=headers, data=data)
#
#     WBToken = req.cookies.get_dict()['WBToken']
#     print(WBToken)
#     headers = {'Cookie': f'WBToken={WBToken};x-supplier-id={supplier};x-supplier-id-external={supplier}',
#                'Content-Type': 'application/json; charset=utf-8', 'Accept-Encoding': 'gzip, deflate, br',
#                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
#                'Connection': 'keep-alive'}
#     url = 'https://seller.wildberries.ru/passport/api/v2/auth/introspect'
#     res = requests.get(url, headers=headers).text
#     print(res)
#     user_id = json.loads(res)
#     return WBToken, user_id['userID']



def get_default_companies(WBToken, supplier):
    headers = {'Cookie': f'WBToken={WBToken};x-supplier-id={supplier};x-supplier-id-external={supplier}','Content-Type':'application/json; charset=utf-8', 'Accept-Encoding':'gzip, deflate, br', 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
               'X-User-Id' : "7568872", 'Connection': 'keep-alive', 'Host':'cmp.wildberries.ru', 'Referer':'https://cmp.wildberries.ru/campaigns/list/active'}
    url = 'https://cmp.wildberries.ru/backend/api/v3/atrevds?pageNumber=1&pageSize=100&search&status=%5B1,15,2,4,9,3,14,16,6,17,5,10,13,12%5D&order=null&direction=null&type=%5B2,3,4,5,6,7%5D'
    url = 'https://cmp.wildberries.ru/backend/api/v3/atrevds?pageNumber=1&pageSize=100&search=&status=[0,11,1,15,2,4,9,3,14,16,6,17,5,10,13,12,7,8]&order=createDate&direction=desc&type=[2,3,4,5,6,7]'
    print(headers)
    req = requests.get(url, headers=headers).text
    data = json.loads(req)
    print(data)

    return data

def get_active_companies(WBToken, supplier):
    headers = {'Cookie': f'WBToken={WBToken};x-supplier-id={supplier};x-supplier-id-external={supplier}','Content-Type':'application/json; charset=utf-8', 'Accept-Encoding':'gzip, deflate, br', 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
               'X-User-Id' : "7568872", 'Connection': 'keep-alive', 'Host':'cmp.wildberries.ru', 'Referer':'https://cmp.wildberries.ru/campaigns/list/active'}
    url = 'https://cmp.wildberries.ru/backend/api/v3/atrevds?pageNumber=1&pageSize=100&search&status=%5B1,15,2,4,9,3,14,16,6,17,5,10,13,12%5D&order=null&direction=null&type=%5B2,3,4,5,6,7%5D'
    print(headers)
    req = requests.get(url, headers=headers).text
    data = json.loads(req)
    return data

def get_ad_info(args: dict):
    print('start get_ad_info')
    # phone = args['phone']
    wb_user_id = args['wb_user_id']
    url = f'https://cmp.wildberries.ru/backend/api/v2/carousel-auction/3792546/placement'
    print(url)
    headers_ = {'Host': 'cmp.wildberries.ru',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
'Accept': 'application/json',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
'Accept-Encoding': 'gzip, deflate, br',
'X-User-Id': args['wb_user_id'],
'Cache-control': 'no-store',
'Content-Type': 'application/json',
'Connection': 'keep-alive',
'Referer': 'https://cmp.wildberries.ru/campaigns/list/all/edit/carousel-auction/3792546',
'Cookie': f'WBToken={args["WBToken"]}; x-supplier-id-external={args["supplier"]}',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-origin'}
    print(headers_)
    # headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
    res = requests.get(url=url, headers=headers_)
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
    print(data)
    return data


def start_company(args):
    phone = args['phone']
    wb_user_id = args['wb_user_id']
    url = f'https://cmp.wildberries.ru/backend/api/v2/carousel-auction/3792546/3486774/placement'
    headers_ = f'''Accept: application/json
Accept-Encoding: gzip, deflate, br
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Cache-control: no-store
Connection: keep-alive
Content-Type: application/json
Host: cmp.wildberries.ru
Origin: https://cmp.wildberries.ru
Referer: https://cmp.wildberries.ru/campaigns/list/pause/edit/search/3792546
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
Cookie: WBToken={args['WBToken']};x-supplier-id={args['supplier']};x-supplier-id-external={args['supplier']}
X-User-Id: {wb_user_id}'''
    # ad_info = await get_ad_info(campaign, args)
    # subjectId = ad_info['subjectId']
    # price = ad_info['price']
    # balance = api_get_budget(args)['total']

    # if args["company_type"] == 'search':
    #     keyword = ad_info['keyWord']
    #     searchElements = [{'active': True, 'brand': i['brand'], 'name': i['name'], 'nm': i['nm']} for i in
    #                       ad_info['searchElements']]
    #     payload = {"budget": {"total": balance, "dailyMax": 0}, "minCPM": 50, "stepCPM": 1, 'name': 'трусы женские',
    #                'status': 11, 'place': [
    #             {'keyWord': keyword, 'subjectId': subjectId, 'price': price,
    #              'searchElements': searchElements}]}
    #
    # if args["company_type"] == 'carousel-auction':
    #     subject = ad_info['subject']
    #     carouselElements = [{'active': True, 'brand': i['brand'], 'name': i['name'], 'nm': i['nm']} for i in
    #                         ad_info['carouselElements']]
    #
    #     payload = {"budget": {"total": balance, "dailyMax": 0}, "minCPM": 50, "stepCPM": 1, "excludedBrands": [],
    #                "locale": [643], "place": [
    #             {"subjectId": subjectId, "subject": subject, "kindId": ad_info['kindId'],
    #              "kind": ad_info['kind'],
    #              "price": price, "carouselElements": carouselElements,
    #              "intervals": []}], "nmsCount": 1, "name": campaign.campaign_name, "status": 11}
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

# # supp = 'c9640da8-a840-5484-bb00-dee7d6df69dd'
# WBToken, user_id = auth('57752E08985F7901FF5ACE743E9AB52D754542EC46368B98735B2EF4B93A0229CD34116AEC1D4BD32A652021AA1ECE97B52F353269AF8856A7725BE0BF451E42348158385259AF7B28E2AF02A0FFCE46D93F53074C95DF3249AA07D11569D2DFEE3BFEF38B5336D247037E7CD6FF7FD961D60FBAF0598E790CF35F9E0567BFC7AA4DE889EBC8FC51216157ED0CAE824D78EE573C8EAD5BAD5FAC32A84E554506C8728344656716533BD5CE8A584344E65CAD356065402D51B61BC91374F50D64CD825D2BD762AD60F13BC26F45F96CC54268B578194A53B411BF9B0C4A3F9F2249B3A1ADCAE4F49802117A35D9A8EB665B430560682D48BD12C7E7A4DBA53B2B1BC08B63C899B18F4D5AFBFFD594E505B879DE9AC55674C772E69E44FF992073AD44502438DF6A783F030A085ED2CDBF77C0CB20B94C7B8E3A6C7EFAC861CA5067704280548F92FC7C80402A8D81C2C3668A0C9C', 'c9640da8-a840-5484-bb00-dee7d6df69dd')
# WBToken = 'Auj7zQP4gNu5DPjej7oMMvgVBXJZ-yZFNG2ZJGRKBY7DyKJxR61RrU-Upd_eOeqAsaqw3dxGXPDFdnIMC60uD2cJ'
#
# # WBToken = 'Auj7zQO8w9q5DLyhj7oMMsXaO3DO9vzfngJ2DTuo50R4Ce7bxkUvLL3TTKwU_C_23kFr_wNN0qozRumVRinTXois'
# # WBToken = 'Auj7zQOytKa5DLKS27kMMrZ3Q49WsNFjzHrB60YwuAIlDu6E0_b7SI8qF0rOSeOsgqidWOw7JQBm1Ezy8cEQVK5a

# # get_default_companies(WBToken, 'c9640da8-a840-5484-bb00-dee7d6df69dd')
#
# headers = {'Host': 'cmp.wildberries.ru',
# 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
# 'Accept': 'application/json',
# 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
# 'Accept-Encoding': 'gzip, deflate, br',
# 'X-User-Id': '7568872',
# 'Cache-control': 'no-store',
# 'Content-Type': 'application/json',
# 'Connection': 'keep-alive',
# 'Referer': 'https://cmp.wildberries.ru/campaigns/list/pause/edit/search/3486774',
# 'Cookie': f'WBToken={WBToken}; x-supplier-id-external=c9640da8-a840-5484-bb00-dee7d6df69dd',
# 'Sec-Fetch-Dest': 'empty',
# 'Sec-Fetch-Mode': 'cors',
# 'Sec-Fetch-Site': 'same-origin'}
# url = 'https://cmp.wildberries.ru/backend/api/v2/search/3486774/placement'
# resp = requests.get(url, headers=headers)
# print(resp)

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

def get_code_wb(WB3Token: str):
    wb3 = '0F43EA72888778809B12A67E5BA9D3AC99BF1FF5464E5D483A325BCAC3141C83005FC34473AC571CA87D72B9A97BBEB1272CD8E4B78278EBE54917BE8566A12529BB9D5886202F0BE8D30600A15223EBADDC913D227489EDC15034BC17B9DAC5F2E5DDCA50DB22EB11F7B670FB3135A78A4981CA895DD2682FE90D88462710AE26F1ABC31E1F3DD860FF8BBA2918246FC8451C83A44CC1FC7C8AD622119B00BB74CF9E49CC2B64281D693093C8482A714F6A6B54D356D0A675CC604C970521B8B9CA88628B1DFF5DE62AEBF015ECE1FC6F8262213645370DEC6569CBF3791462A0382657699BA40BACADFB975F4A3E652C8810464F653CF4600EDC04DE8A388A55153E29933C721A8F5EBE7C1EE72CAE8908C8F29B40FCF5763F0B06367277AB9F81B9B6984ECDC378CEBA395F002B7F0DF6E2E84CCF92CE5B2357D9E2247677F5D79E28C2B23502C95708EADC0574D10AE4124E'
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
"Cookie":  f"WILDAUTHNEW_V3={wb3}",
"Sec-Fetch-Mode": "cors",
"Sec-Fetch-Site": "same-origin",
"Content-Length": "0"}

    data = {}
    url = 'https://www.wildberries.ru/webapi/lk/newsfeed/events/data?'
    resp = requests.post(url=url, headers=headers, data=data).text
    resp = json.loads(resp)
    return resp


def parse_code(data):
    for i in data['value']['events']:
        soup = BeautifulSoup(i['message'], 'html.parser')
        code_all = soup.findAll('span')
        code = re.findall(r'\d+', code_all[1].get_text())
        return code[0]


def send_code_auth(code, token):
    url = 'https://cmp.wildberries.ru/passport/api/v2/auth/login'
    print(code)
    print(token)
    data = {"options":{"notify_code":f"{code}"}, "token": f"{token}","device":"Windows,Mozilla Firefox 109.0"}
    data = json.dumps(data)
    try:
        resp = requests.post(url, data=data)
        WBToken = resp.cookies.get_dict()['WBToken']
        return WBToken
    except:
        return False

def auth():
    wb3 = '7E9CFC7379820C6C3A7D11392DBA507009FCFBA4AD6D965FE4E241DF5E0E86BB20032F7990F38B3945634C6962B9F3228269E5C805F3F6E3AD1411238CF9662D86A1987AC74DB420D7E566D0F67FA0C4BAF39CAAC2F23CA00257426A3E07BB598EED9F2EE372C3E8547624033FA64D6B6F341B22666C78ADA916A7C7210B46CE0A494F135B51C5D3B0D7A9C21361D909827D772BB4FF6DF4E27E6784FBE348625219AAE9C92C61D569E972E006552EFE1F155C5C0B02D9D553A1697EE1B9EB6B1CB122CCC3CE0EFE7402FE5E632B171F83B5CB5DAA9DBA7893084B514B7C5A4A4C10CA6796BA9C4D097D41F748CB80841C9F9AB314E6E45064AA4A3D9EC460F372881FC265A0EEFB1316D913C6A305B681CF2A4309BA1EDAA4CC6B0C65E3DDEB6C165060CF4DC5C26ECAF5A0D9C476D487007B9A'
    phone = '+79246049032'
    token = send_code_phone(phone)
    print(token)
    code_data = get_code_wb(wb3)
    code = parse_code(code_data)
    WBToken = send_code_auth(code, token)
    return WBToken

WBToken = auth()
# WBToken = 'Auj7zQPeydu5DN6nkLoMMpnS3Y0Lj45IQtV740t2nf-v4_4rKvs3odp33kI96QHPKDV8TNdyxenAhkTf8gJxTSN4'
args = {'WBToken': WBToken, 'supplier':'c44a7ece-d7e9-56fd-b1d4-5b718ab59637', 'wb_user_id':'7568872'}
get_ad_info(args)
