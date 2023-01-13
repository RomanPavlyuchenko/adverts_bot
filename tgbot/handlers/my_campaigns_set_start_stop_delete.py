from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.keyboards import kb_user
from tgbot.models.tables import Campaigns
from tgbot.services import logger
from tgbot.services.db_queries import update_campaign, get_campaign_by_id, delete_campaign
from tgbot.services.wb import wb, common
from tgbot.states.my_campaign_state import MyCampaignState
from tgbot.states.user_state import AdsSettingState
from tgbot.utils.all_markups import my_campaign_markup
from tgbot.utils.all_texts import my_campaign_text
from tgbot.utils.wb_api import api_start_campaign, api_stop_campaign


async def my_campaign_start_campaign(session: AsyncSession, args: dict):
    print('start my_campaign_start_campaign')
    args['is_active'] = True

    await update_campaign(session, args['campaign_id'], args)
    campaign = await get_campaign_by_id(session, args['campaign_id'])
    return await api_start_campaign(campaign, args)


async def my_campaign_stop_campaign(session: AsyncSession, args: dict):
    args['is_active'] = False
    await update_campaign(session, args['campaign_id'], args)
    return await api_stop_campaign(args)


async def my_campaign_delete_campaign(session: AsyncSession, args: dict):
    await delete_campaign(session, args['campaign_id'])


