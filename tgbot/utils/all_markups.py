from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.models.tables import Campaigns
from tgbot.utils.utils import campaign_is_active


def my_campaign_markup(campaign: Campaigns):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Пополнить бюджет', callback_data=f'campaign:add_balance:{campaign.campaign_id}'))
    markup.add(InlineKeyboardButton(f'Установить позицию', callback_data=f'campaign:set_position:{campaign.campaign_id}'))
    markup.add(InlineKeyboardButton(f'Установить макс ставку', callback_data=f'campaign:set_limit:{campaign.campaign_id}'))
    if campaign.append_balance > 0:
        markup.add(InlineKeyboardButton(f'Отключить автопополнение', callback_data=f'campaign:off_auto_add_balance:{campaign.campaign_id}'))
    else:
        markup.add(InlineKeyboardButton(f'Включить автопополнение', callback_data=f'campaign:on_auto_add_balance:{campaign.campaign_id}'))
    if campaign.type == 'search':
        markup.add(InlineKeyboardButton(f'Настроить автоудаление кл.фраз', callback_data=f'campaign:auto_change_keywords:{campaign.campaign_id}'))
        markup.add(InlineKeyboardButton(f'Мои ключевые фразы', callback_data=f'campaign:get_keywords:{campaign.campaign_id}'))

    if campaign_is_active.get_is_active_campaign(campaign.campaign_id):
        markup.add(InlineKeyboardButton(f'Остановить', callback_data=f'campaign:set_stop:{campaign.campaign_id}'))
    else:
        markup.add(InlineKeyboardButton(f'Запустить', callback_data=f'campaign:set_start:{campaign.campaign_id}'))
    markup.add(InlineKeyboardButton(f'Статистика', callback_data=f'campaign:stat:{campaign.campaign_id}'))
    markup.add(InlineKeyboardButton(f'Удалить', callback_data=f'campaign:delete:{campaign.campaign_id}'))
    markup.add(InlineKeyboardButton(f'Главное меню', callback_data=f'campaign:menu:{campaign.campaign_id}'))
    return markup


def btn_query_my_campaigns():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Мои кампании', callback_data=f'query_my_campaigns'))
    return markup


btn_skip = 'Пропустить'
