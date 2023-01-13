import logging
from datetime import date, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.future import select
from sqlalchemy.orm.session import sessionmaker

from tgbot.models.tables import User, Tracking, WBAccounts, Campaigns, Buffer, DefaultCampaigns


async def add_new_tracking(session: AsyncSession, user_id: int, query_text: str = None, scu: int = None):
    """Добавляет новое отслеживание"""
    await session.execute(sa.delete(Tracking).where(Tracking.user_id == user_id, Tracking.query_text == query_text,
                                                    Tracking.scu == scu))
    await session.commit()
    tracking = Tracking(user_id=user_id, query_text=query_text, scu=scu)
    session.add(tracking)
    try:
        await session.commit()
        return True
    except DBAPIError:
        await session.rollback()


async def add_user(session: AsyncSession, user_id: int, subscribe: int) -> bool:
    """
    Добавляет нового пользователя
    :param session:
    :param user_id:
    :param subscribe: Количество дней, на сколько активируется подписка у человека
    :return:
    """
    logging.info(f'Запустилась запись {user_id} {date.today() + timedelta(days=subscribe)}')

    user = User(id=user_id, subscribe=date.today() + timedelta(days=subscribe) if subscribe else None)
    logging.info(user)
    logging.info(session)
    session.add(user)
    try:
        await session.commit()
        return True
    except (IntegrityError, DBAPIError):
        logging.info('Ошибка')
        await session.rollback()
        return False


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    """Возвращает объект пользователя если он есть в базе, иначе None"""
    user = await session.execute(sa.select(User).where(User.id == user_id))
    return user.scalar()


async def delete_user(session: AsyncSession, user_id: int) -> tuple | None:
    """Удаляет пользователя по его id"""
    result = await session.execute(sa.delete(User).where(User.id == user_id).returning("*"))
    await session.commit()
    return result.first()


async def delete_tracking(session: AsyncSession, user_id: int, query_text: str = None, scu: int = None) -> tuple | None:
    """Удаляет отслеживание, которые выбрал пользователь"""
    result = await session.execute(
        sa.delete(Tracking).where(Tracking.user_id == user_id, Tracking.query_text == query_text, Tracking.scu == scu).returning("*")
    )
    await session.commit()
    return result.first()


async def get_users(session: AsyncSession) -> list[User]:
    """Возвращает всех пользователей"""
    users = await session.execute(sa.select(User).order_by(User.id))
    return users.scalars().all()

async def get_campaign_all(session: AsyncSession) -> list[User]:
    """Возвращает все компании"""
    users = await session.execute(sa.select(Campaigns))
    return users.scalars().all()

async def remove_users_without_subscribe(session_factory: sessionmaker):
    """Удаляет пользователей у которых срок подписки меньше сегодняшней даты"""
    async with session_factory() as session:
        result = await session.execute(sa.delete(User).where(User.subscribe.isnot(None), User.subscribe < date.today())\
                              .returning("*"))
        await session.commit()
        return result.scalars().all()


async def get_all_tracking(session: AsyncSession) -> list[Tracking]:
    """Возвращает все отслеживания в базе"""
    tracking = await session.execute(sa.select(Tracking).order_by(Tracking.user_id))
    return tracking.scalars().all()


async def get_tracking_by_user_id(session: AsyncSession, user_id: int) -> list[Tracking] | None:
    """Возвращает отслеживания пользователя"""
    tracking = await session.execute(sa.select(Tracking).where(Tracking.user_id == user_id))
    return tracking.scalars().all()


async def add_new_wbaccount(session: AsyncSession, user_id: int, phone: str, wb3token: str, name: str, supplier: str):
    """Добавляет новый аккаунт wb"""
    accs = await get_wbaccounts_by_user_id(session, user_id)
    if accs:
        for i in accs:
            if i.phone == phone:
                return False
        for i in accs:
            await session.execute(sa.update(WBAccounts).where(WBAccounts.phone == i.phone).values(choice=False))
        await session.commit()
    wbacc = WBAccounts(user_id=user_id, phone=phone, choice=True, wb3token=wb3token, name=name, supplier_id=supplier)
    session.add(wbacc)
    try:
        await session.commit()
        return True
    except DBAPIError:
        await session.rollback()
        return False


async def set_wbacc_is_work(session: AsyncSession, user_id: int, phone: str):
    accs = await get_wbaccounts_by_user_id(session, user_id)
    if accs:
        for i in accs:
            await session.execute(sa.update(WBAccounts).where(WBAccounts.phone == i.phone).values(choice=False))
        await session.commit()
    await session.execute(sa.update(WBAccounts).where(WBAccounts.phone == phone).values(choice=True))
    await session.commit()


async def get_wbaccount(session: AsyncSession, phone: str) -> WBAccounts:
    wbacc = await session.execute(sa.select(WBAccounts).where(WBAccounts.phone == phone))
    return wbacc.scalars().all()[0]

async def get_user_by_phone(session: AsyncSession, phone: str) -> WBAccounts:
    wbacc = await session.execute(sa.select(User).where(User.phone == phone))
    return wbacc.scalars().all()


async def get_wbaccount_by_token(session: AsyncSession, wb3token: str) -> WBAccounts:
    wbacc = await session.execute(sa.select(WBAccounts).where(WBAccounts.wb3token == wb3token))
    return wbacc.scalar()


async def get_all_wbaccounts(session: AsyncSession) -> list[WBAccounts]:
    wbacc = await session.execute(sa.select(WBAccounts))
    return wbacc.scalars().all()


async def update_wb_account(session: AsyncSession, phone: str, args: dict):
    """choice, wb3token, wbtoken, wb_user_id"""

    wbacc = await get_wbaccount(session, phone)
    await session.execute(sa.update(WBAccounts).where(WBAccounts.phone == wbacc.phone).values(
        choice=args.get('choice', wbacc.choice), wb3token=args.get('wb3token', wbacc.wb3token),
        wb_user_id=args.get('wb_user_id', wbacc.wb_user_id), wbtoken=args.get('WBToken', wbacc.wbtoken)))
    await session.commit()


async def delete_wbaccount(session: AsyncSession, phone: str, user_id: int):
    try:
        logging.info(phone)
        logging.info(session)
        res = await session.execute(sa.select(User).where(User.id == user_id))
        res = res.scalars().one()
        phone += ';'
        phone_all  = res.wbaccounts
        phone_all = phone_all.replace(phone, '')
        await session.execute(sa.delete(WBAccounts).where(WBAccounts.phone == phone))
        await session.execute(sa.delete(Campaigns).where(Campaigns.phone == phone))
        await session.execute(sa.delete(DefaultCampaigns).where(DefaultCampaigns.phone == phone))
        await session.execute(sa.update(User).where(User.id == user_id).values(wbaccounts=phone_all))
        await session.commit()
    except Exception as e:
        logging.info(e)
        print(e)


async def add_wbacc_to_user(session: AsyncSession, cid: int, phone: str):
    user = await get_user(session, cid)
    accounts = user.wbaccounts
    if accounts:
        accounts += f'{phone};'
    else:
        accounts = f'{phone};'
    await session.execute(sa.update(User).where(User.id == cid).values(wbaccounts=accounts))
    await session.commit()


async def remove_wb_account_from_user(session: AsyncSession, cid: int, phone: str):
    user = await get_user(session, cid)
    accounts = user.wbaccounts
    accounts = accounts.replace(f'{phone};', '')
    await session.execute(sa.update(User).where(User.id == cid).values(wbaccounts=accounts))
    await session.commit()


async def add_new_campaign(session: AsyncSession, args: dict):
    """Добавляет новую кампанию"""
    campaign_name = args['campaign_name']
    campaign_id = args['campaign_id']
    phone = args['phone']
    type = args['company_type']
    place = args['position']
    limit = args['limit']
    keywords = args.get('keywords')
    balance = args.get('balance')
    append_balance = args.get('append_balance', 0)
    is_active = args.get('is_active', False)
    phrases = args.get('phrases')
    auto_change_phrases = args.get('auto_change_phrases', False)
    sku = args.get('sku', 0)
    if phrases:
        phrases = phrases.lower()
    campaign = Campaigns(campaign_id=campaign_id, phone=phone, campaign_name=campaign_name, type=type, place=place,
                         limit=limit, keywords=keywords, phrases=phrases, auto_change_phrases=auto_change_phrases,
                         balance=balance, append_balance=append_balance, is_active=is_active, sku=sku)
    session.add(campaign)
    try:
        await session.commit()
        return True
    except Exception as e:
        print(e)
        await session.rollback()


async def update_campaign(session: AsyncSession, campaign_id: int, args: dict):
    """position, limit, keywords, sku, balance, append_balance, phrases, campaign_name"""
    campaign = await get_campaign_by_id(session, campaign_id)
    campaign_name = args.get('campaign_name', campaign.campaign_name)
    place = args.get('position', campaign.place)
    limit = args.get('limit', campaign.limit)
    keywords = args.get('keywords', campaign.keywords)
    balance = args.get('balance', campaign.balance)
    append_balance = args.get('append_balance', campaign.append_balance)
    is_active = args.get('is_active', campaign.is_active)
    phrases = args.get('phrases', campaign.phrases)
    auto_change_phrases = args.get('auto_change_phrases', campaign.auto_change_phrases)
    sku = args.get('sku', campaign.sku)
    if phrases:
        phrases = phrases.lower()
    await session.execute(sa.update(Campaigns).where(Campaigns.campaign_id == campaign_id).values(
        campaign_name=campaign_name, place=place, limit=limit, keywords=keywords, balance=balance,
        append_balance=append_balance, is_active=is_active, phrases=phrases, auto_change_phrases=auto_change_phrases, sku=sku))
    await session.commit()


async def delete_campaign(session: AsyncSession, campaign_id: int):
    try:
        await session.execute(sa.delete(Campaigns).where(Campaigns.campaign_id == campaign_id))
        await session.commit()
    except Exception as e:
        print(e)


async def get_wbaccounts_by_user_id(session: AsyncSession, user_id: int) -> list[WBAccounts] | None:
    """Возвращает wbaccounts пользователя"""

    user = await get_user(session, user_id)
    accounts = []
    if user.wbaccounts:
        for i in user.wbaccounts.split(';'):
            if i:
                try:
                    account = await session.execute(select(WBAccounts).where(WBAccounts.phone == i))
                    accounts.append(account.scalar())
                except Exception as e:
                    print('get_wbaccounts_by_user_id', e)
    return accounts


async def get_campaigns_by_user_id(session: AsyncSession, user_id: int) -> list[Campaigns] | None:
    """Возвращает кампании пользователя"""
    accounts = await get_wbaccounts_by_user_id(session, user_id)
    campaigns = []
    if accounts:
        for acc in accounts:
            if acc:
                campaign = await session.execute(sa.select(Campaigns).where(Campaigns.phone == acc.phone))
                if campaign:
                    campaigns += campaign.scalars().all()
    return campaigns


async def get_campaign_by_id(session: AsyncSession, campaign_id: int) -> Campaigns:
    """Возвращает кампанию"""
    res = await session.execute(sa.select(Campaigns).where(Campaigns.campaign_id == campaign_id))
    return res.scalars().one()

async def get_supplier_id(session: AsyncSession, supplier: str) -> WBAccounts:
    res = await session.execute(sa.select(WBAccounts).where(WBAccounts.supplier_id == supplier))
    return res.scalar()


async def create_message(session: AsyncSession, cid: int, text: str):
    messages = await get_all_messages(session)
    if messages:
        message_id = messages[-1].message_id + 1
    else:
        message_id = 1
    text = Buffer(message_id=message_id, cid=cid, text=text)
    session.add(text)
    await session.commit()


async def get_all_messages(session: AsyncSession) -> [Buffer]:
    res = await session.execute(sa.select(Buffer))
    return res.scalars().all()


async def delete_message(session: AsyncSession, message_id: int):
    await session.execute(sa.delete(Buffer).where(Buffer.message_id == message_id))
    await session.commit()


async def add_default_campaign(session: AsyncSession, phone: str, campaigns: list):
    print('add_default_campaign start delete campaigns')
    for campaign in campaigns:
        try:
            # campaignName = campaign['campaignName']
            # categoryName = campaign['categoryName']
            # campaignId = campaign['id']
            # company_type = 'default'
            #
            # if categoryName == 'Поиск':
            #     company_type = 'search'
            # if categoryName == 'Карусель':
            #     company_type = 'carousel-auction'
            # if categoryName == 'Каталог':
            #     company_type = 'catalog'
            # args = {'campaign_id': int(campaignId), 'phone': phone, 'name': campaignName, 'type': company_type}
            await session.execute(sa.delete(DefaultCampaigns).where(DefaultCampaigns.campaign_id == int(campaign['id']) and
                                                                    DefaultCampaigns.phone == phone))
            campaignName = campaign['campaignName']
            categoryName = campaign['categoryName']
            campaignId = campaign['id']
            company_type = 'default'
            if categoryName == 'Поиск':
                company_type = 'search'
            if categoryName == 'Карусель':
                company_type = 'carousel-auction'
            if categoryName == 'Каталог':
                company_type = 'catalog'
            args = {'campaign_id': int(campaignId), 'phone': phone, 'name': campaignName, 'type': company_type}
            company = DefaultCampaigns(campaign_id=args['campaign_id'], phone=args.get('phone'),
                                       name=args.get('name'), type=args.get('type'))
            session.add(company)
        except Exception as e:
            print(e)
    #await session.commit()
    # print('add_default_campaign start add campaigns')
    #
    # for campaign in campaigns:
    #     try:
    #         campaignName = campaign['campaignName']
    #         categoryName = campaign['categoryName']
    #         campaignId = campaign['id']
    #         company_type = 'default'
    #         if categoryName == 'Поиск':
    #             company_type = 'search'
    #         if categoryName == 'Карусель':
    #             company_type = 'carousel-auction'
    #         if categoryName == 'Каталог':
    #             company_type = 'catalog'
    #         args = {'campaign_id': int(campaignId), 'phone': phone, 'name': campaignName, 'type': company_type}
    #         company = DefaultCampaigns(campaign_id=args['campaign_id'], phone=args.get('phone'),
    #                                    name=args.get('name'), type=args.get('type'))
    #         session.add(company)
    #     except Exception as e:
    #         print(e)
    # print('add_default_campaign campaigns added')
    try:
        await session.commit()
        print('add_default_campaign completed')
    except Exception as e:
        print('session.commit()', e)


async def get_all_default_campaign_by_phone(session: AsyncSession, phone: str) -> list[DefaultCampaigns]:
    res = await session.execute(sa.select(DefaultCampaigns).where(DefaultCampaigns.phone == phone))
    return res.scalars().all()

async def update_wbtoken_all(session: AsyncSession, WBToken: str):
    await session.execute(sa.update(WBAccounts).values(wbtoken=WBToken))
    await session.commit()

