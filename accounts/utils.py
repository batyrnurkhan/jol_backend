import requests
from django.conf import settings


def send_sms(phone_number, message):
    api_key = settings.MOBIZON_API_KEY
    url = f'https://api.mobizon.kz/service/message/sendSmsMessage?recipient={phone_number}&text={message}&apiKey={api_key}'
    response = requests.get(url)
    return response.json()
