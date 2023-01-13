from aiogram.dispatcher.filters.state import StatesGroup, State


class MyCampaignState(StatesGroup):
    choice_campaign = State()

    add_balance = State()

    enter_search_or_sku = State()
    set_position = State()

    set_limit = State()

    keywords = State()
    generate_keywords = State()
    insert_keywords = State()
    keywords_confirm = State()
