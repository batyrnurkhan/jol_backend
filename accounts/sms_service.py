import requests
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class SMSCService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.mobizon.kz/service/message/sendsmsmessage'

    def send_sms(self, phone_number, message):
        # Кодируем сообщение
        encoded_message = urlencode({'text': message})

        # Формируем URL для отправки SMS с URL-кодированным текстом
        url = f"{self.base_url}?recipient={phone_number}&{encoded_message}&apiKey=kz97942e67d631306b579416b07f19ce862d409385be6846ddeb8171f3f4f0c85d61e4"

        # Логирование отправляемого URL
        print(f"Sending request to URL: {url}")

        try:
            # Отправляем GET запрос
            response = requests.get(url)

            # Логируем статус ответа и данные
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response text: {response.text}")

            # Проверяем успешность запроса
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('code') == 0:
                    return True  # SMS успешно отправлено
                else:
                    error_message = response_data.get('message', 'Unknown error')
                    error_code = response_data.get('code', 'N/A')
                    raise Exception(f"Failed to send SMS: {error_message} (Error code: {error_code})")
            else:
                raise Exception(f"Failed to send SMS: HTTP {response.status_code}")

        except requests.exceptions.RequestException as e:
            # Логируем и пробрасываем ошибку в случае неудачи запроса
            logger.error(f"Request to Mobizon failed: {str(e)}")
            raise Exception("Failed to send SMS: Unknown error")
