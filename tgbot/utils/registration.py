import asyncio
import threading
import time

from aiogram import Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.browser_work.login_acc import get_open_browser, start_registration, enter_code, check_code, resend_code, \
    save_cookies
from tgbot.services.db_queries import create_message, add_new_wbaccount


class Registration:
    def __init__(self, phone):
        self.phone = phone
        self.code = None
        self.driver = None

    # async def wait_commands(self):
    #     while True:
    #         await asyncio.sleep(10)

    def wait_commands(self):
        while True:
            time.sleep(10)

    def set_phone(self, phone):
        self.phone = phone

    def get_phone(self):
        return self.phone

    def set_code(self, code):
        self.code = code

    def get_code(self):
        return self.code

    def set_browser(self):
        self.driver = get_open_browser()
        # if self.driver == False:
        #     return False
        # else:
        #     return True

    def start_registration(self):
        self.driver, res = start_registration(self.driver, self.phone)
        return res

    def enter_code(self):
        self.driver = enter_code(self.driver, self.code)
        if self.driver == False:
            return False
        else:
            return True

    def check_code(self):
        return check_code(self.driver)

    def resend_code(self):
        resend_code(self.driver)

    def save_cookie(self):
        save_cookies(self.driver, self.phone)

    def close(self):
        self.driver.close()


class RegistrationThreading:

    def new_reg(self, phone):
        self.__dict__[phone] = Registration(phone)
        # print('set', self.__dict__)

    def get_reg(self, phone):
        # print('get', self.__dict__)
        return self.__dict__[phone]


reg = RegistrationThreading()


async def start_reg(reg_, cid: int):
    #loop = asyncio.get_event_loop()
    #asyncio.run(dp.bot.send_message(cid, 'Началась авторизация'))
    #loop.run_until_complete()
    reg_.set_browser()
    if not reg_.start_registration():
        #asyncio.run(dp.bot.send_message(cid, 'Браузер не смог начать авторизацию, попробуйте еще раз'))
        return 'Браузер не смог начать авторизацию, попробуйте еще раз'
    return 'Код отправлен'


def run_wait(reg_):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(reg_.wait_commands())
    reg_.wait_commands()


async def end_reg(reg_, code):
    reg_.set_code(code)
    reg_.enter_code()
    time.sleep(3)
    res = reg_.check_code()
    if res == 'True':
        reg_.driver.get('https://seller.wildberries.ru/cmp/campaigns/list/active?type=auction')
        time.sleep(5)
        reg_.driver.get('https://seller.wildberries.ru/cmp/campaigns/list/active?type=auction')
        time.sleep(5)
        reg_.save_cookie()
        #await add_new_wbaccount(session, cid, phone)
        #update_login_status(phone, 'True')
        #create_message(cid, 'Вход успешен')
        reg_.close()
        return True, 'Вход успешен'
    elif res == 'Code error':
        return False, 'code'
       # update_login_status(phone, 'Code error')
    else:
       # create_message(cid, 'Не удалось войти')
        reg_.close()
        return False, 'login'
