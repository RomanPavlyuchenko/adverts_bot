import time

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from .service import send_update_price
from .db_queries import remove_users_without_subscribe, get_users, get_campaigns_by_user_id, get_wbaccount, update_wbtoken_all, \
    get_campaign_all, get_user_by_phone
from ..handlers.my_campaigns_set_start_stop_delete import my_campaign_stop_campaign, my_campaign_start_campaign
from ..utils.all_markups import btn_query_my_campaigns
from ..utils.bot_send_message import check_new_messages
from ..utils.utils import set_new_price_campaign, campaign_is_active, get_exist_phrases_and_excluded, auth
from ..utils.wb_api import api_get_budget, api_add_balance, set_excluded_words, api_stop_campaign

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


async def task_sending_notification(bot, session_factory):
    """Задача по отправке уведомления, если товара на складе меньше, чем указал пользователь"""
    await send_update_price(session_factory, bot)


async def task_remove_user_without_subscribe(bot, session_factory):
    """Задача на удаление пользователей без подписки"""
    users = await remove_users_without_subscribe(session_factory)
    for user in users:
        print(user)
        try:
            await bot.send_message(user, "Ваша подписка закончилась. Для дальнейшего использования нажмите /start")
        except Exception as er:
            logger.error(er)


async def task_set_new_price_on_ad(bot, session_factory):
    print('START set_new_price')
    async with session_factory() as session:
            users = await get_users(session)
            campaigns = await get_campaign_all(session)
            if campaigns:
                for campaign in campaigns:
                    if campaign.is_active:
                        t_start = time.time()
                        campaign_is_active.add_campaign(campaign.campaign_id, campaign.is_active, campaign.place)
                        # try:
                        wbacc = await get_wbaccount(session, campaign.phone)
                        complete, result = await set_new_price_campaign(campaign, wbacc)
                        args = {'company_type': campaign.type, 'campaign_id': campaign.campaign_id,
                                'wb_user_id': wbacc.wb_user_id, 'phone': campaign.phone, 'company_id': campaign.campaign_id, 'WBToken': wbacc.wbtoken, "supplier":wbacc.supplier_id}
                        print('complete, result', complete, result)
                        if complete:
                            real_old_pos = campaign_is_active.get_pos_campaign(campaign.campaign_id)
                            if real_old_pos == 0:
                                new_pos = int(result.split(':')[1])

                                if await my_campaign_start_campaign(session, args):
                                    campaign_is_active.set_pos_campaign(campaign.campaign_id, new_pos)
                                    print(users)
                                    for user in users:
                                        if user.wbaccounts is not None:
                                            if campaign.phone in user.wbaccounts:
                                                await bot.send_message(user.id, f'{campaign.campaign_name} Кампания вновь запущена, ставка в пределах нормы', reply_markup=btn_query_my_campaigns())

                        else:
                            real_old_pos = campaign_is_active.get_pos_campaign(campaign.campaign_id)
                            if real_old_pos != 0:
                                if result == 'out of limit':
                                    if campaign_is_active.get_pos_campaign(campaign.campaign_id) != 0:
                                        campaign_is_active.set_pos_campaign(campaign.campaign_id, 0)
                                        await api_stop_campaign(args)
                                        for user in users:
                                            if user.wbaccounts is not None:
                                                if campaign.phone in user.wbaccounts:
                                                    await bot.send_message(user.id, f'{campaign.campaign_name}\n Превышен лимит ставки и уже занято максимально низкое место, кампания приостановлена', reply_markup=btn_query_my_campaigns())
                                else:
                                    campaign_is_active.set_is_active_campaign(campaign.campaign_id, False)
                        with open('test.txt', 'a') as f:
                            f.write(f'{complete} {time.time() - t_start}')
                        # except Exception as e:
                        #     print('task_set_new_price_on_ad', e)
    print('END set_new_price')


async def task_auto_pay(bot: Bot, session_factory):
    print('START task_auto_pay')
    async with session_factory() as session:
            campaigns = await get_campaign_all(session)
            users = await get_users(session)
            for campaign in campaigns:
                campaign_is_active.add_campaign(campaign.campaign_id, campaign.is_active, campaign.place)
                # try:
                wbacc = await get_wbaccount(session, campaign.phone)
                args = {'phone': campaign.phone, 'wb_user_id': wbacc.wb_user_id,
                        'company_type': campaign.type, 'company_id': campaign.campaign_id,
                        'append_balance': 100, 'campaign_id': campaign.campaign_id, 'WBToken': wbacc.wbtoken, 'supplier':wbacc.supplier_id}
                balance = api_get_budget(args)['total']
                if balance == 0 and campaign_is_active.get_is_active_campaign(campaign.campaign_id):
                    if campaign_is_active.get_is_active_campaign(campaign.campaign_id):
                        for user in users:
                            if user.wbaccounts is not None:
                                if campaign.phone in user.wbaccounts:
                                    await bot.send_message(user.id, f'Бюджет кампании {campaign.campaign_name} закончился, кампания остановлена', reply_markup=btn_query_my_campaigns())
                        campaign_is_active.set_is_active_campaign(campaign.campaign_id, False)
                if balance <= 10 and campaign_is_active.get_is_active_campaign(campaign.campaign_id):
                    if campaign.append_balance > 0:
                        await api_add_balance(args)
                # except Exception as e:
                #     print('task_auto_pay', e)
    print('END task_auto_pay')


async def update_wb_token(session_factory):
    res, WBToken = await auth()
    async with session_factory() as session:
        await update_wbtoken_all(session, WBToken)
        logger.info('Success update token')
    # print(WBToken)


async def task_set_excluded(session_factory):
    print('START task_set_excluded')
    async with session_factory() as session:
        users = await get_users(session)
        for user in users:
            campaigns = await get_campaigns_by_user_id(session, user.id)
            if campaigns:
                for campaign in campaigns:
                    if campaign.is_active and campaign.type == 'search' and campaign.auto_change_phrases:
                        phrases = campaign.phrases
                        if phrases:
                            wbacc = await get_wbaccount(session, campaign.phone)
                            args = {'phone': campaign.phone, 'company_type': campaign.type,
                                    'company_id': campaign.campaign_id, 'wb_user_id': wbacc.wb_user_id, 'campaign_id': campaign.campaign_id, 'WBToken': wbacc.wbtoken, 'supplier':wbacc.supplier_id}
                            phrases_default, excluded = get_exist_phrases_and_excluded(args)
                            if phrases_default or excluded:
                                try:
                                    for i in phrases_default:
                                        excluded.append(phrases_default[i]['keyword'])
                                    result_excluded = []
                                    for i in excluded:
                                        if i not in phrases.split(';'):
                                            result_excluded.append(i)
                                    # print('phrases_default', phrases_default)
                                    # print('result_excluded', result_excluded)
                                    # print('excluded', excluded)
                                    # print('choice', phrases)
                                    set_excluded_words(args, result_excluded)
                                except Exception as e:
                                    print('scheduler excluded', e)
    print('END task_set_excluded')


def add_jobs(bot, session_factory):
    # scheduler.add_job(task_sending_notification, "cron", hour=9, args=[bot, session])
    # scheduler.add_job(task_sending_notification, "cron", hour=12, args=[bot, session])
    scheduler.add_job(task_sending_notification, "interval", minutes=15, args=[bot, session_factory])
    scheduler.add_job(task_remove_user_without_subscribe, "cron", hour=8, args=[bot, session_factory])
    scheduler.add_job(task_set_new_price_on_ad, "interval", minutes=5, args=[bot, session_factory])
    scheduler.add_job(task_auto_pay, "interval", minutes=2, args=[bot, session_factory])
    scheduler.add_job(update_wb_token, "interval", days=3, args=[session_factory])
    scheduler.add_job(task_set_excluded, "interval", minutes=15, args=[session_factory])
    #scheduler.add_job(check_new_messages, "interval", seconds=5, args=[bot, session_factory])

    return scheduler

