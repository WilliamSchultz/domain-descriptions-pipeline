from datetime import datetime
import pytz
import requests

def telegram_bot_sendtext(bot_message):
    tz = pytz.timezone('Europe/Berlin')
    berlin_time = datetime.now(tz)
    bot_message = f'{berlin_time.strftime("%d/%m/%Y %H:%M")} - {bot_message}'
    bot_token = ''
    bot_chatID = '@domains_description_updates'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()
