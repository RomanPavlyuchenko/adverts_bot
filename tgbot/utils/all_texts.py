from tgbot.models.tables import Campaigns
from tgbot.utils.utils import campaign_is_active

enter_campaign_name = 'Введите название кампании'
search_enter_keyword = 'Введите ключевую фразу'


carousel_enter_sku = 'Введите SKU конкурента'


balance_enter_append_sum = 'Введите сумму кратную 50 (мин. сумма 100р)'

enter_limit = 'Введите максимальную ставку'
limit_set_complete = 'Лимит установлен'
auto_add_balance_on = 'Автопополнение включено'
auto_add_balance_off = 'Автопополнение выключено'

campaign_has_no = 'У вас нет добавленных кампаний'
campaign_start = 'Кампания запущена'
campaign_stop = 'Кампания остановлена'
campaign_delete = 'Кампания удалена'
campaign_start_error = 'При запуске кампании вознилка ошибка. Проверьте бюджет и повторите попытку'
campaign_stop_error = 'При остановке кампании вознилка ошибка, повторите попытку'
campaign_keywords_saved = 'Ключевые фразы сохранены'
get_keywords_have_no = 'У вас нет сохраненных ключевых фраз'


choice_menu = 'Выберите пункт меню'


def my_campaign_text(campaign: Campaigns):
    try:
        status = '🟢Активна' if campaign_is_active.get_is_active_campaign(campaign.campaign_id) else '🔴Приостановлена'
    except Exception as e:
        print('my_campaign_text', e)
        status = ''
    type_ad = 'Поиск' if campaign.type == 'search' else 'КТ'
    limit = campaign.limit if campaign.limit != 99999 else 'Неограничен'
    s = f'''Название - {campaign.campaign_name}
Вид - {type_ad}
Статус - {status}
Баланс - {campaign.balance}руб.
Строка отслеживания - {campaign.place}
Ставка - {campaign_is_active.get_price_campaign(campaign.campaign_id)}
Макс. ставка - {limit}'''
    return s
