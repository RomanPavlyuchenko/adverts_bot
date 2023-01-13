from aiogram.dispatcher.filters.state import StatesGroup, State


class AdsSettingState(StatesGroup):
    set_account = State()
    account = State()
    campaign_name = State()
    campaign_choice_name = State()
    balance = State()
    balance_add = State()
    search_search_text = State()
    search_choice_place = State()
    search_choice_limit = State()
    search_auto_change_keywords = State()
    search_keywords = State()
    card_enter_sku = State()
    card_choice_place = State()
    card_choice_limit = State()
    confirm = State()



class AddAccountState(StatesGroup):
    phone = State()
    code = State()
    supplier = State()

class GenerateKeywordsState(StatesGroup):
    search = State()
    confirm = State()


class InsertKeywordsState(StatesGroup):
    insert = State()
    confirm = State()
