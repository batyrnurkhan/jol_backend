import requests
import logging

logger = logging.getLogger(__name__)

class SMSCService:
    def __init__(self, login, password, sender_name='SMSC'):
        self.login = login
        self.password = password
        self.sender_name = sender_name
        self.base_url = 'https://smsc.kz/sys/send.php'

    def send_sms(self, phone_number, message, sender=None):
        payload = {
            'login': self.login,
            'psw': self.password,
            'phones': phone_number,
            'mes': message,
            'fmt': 3,  # Ответ в формате JSON
            'charset': 'utf-8'
        }

        # Добавляем параметр `sender`, если он был передан
        if sender:
            payload['sender'] = sender

        try:
            response = requests.get(self.base_url, params=payload)
            response_data = response.json()

            # Логирование ответа
            logger.error(f"Response status code: {response.status_code}")
            logger.error(f"Response data: {response_data}")

            if response.status_code == 200 and 'error_code' not in response_data:
                return True
            else:
                error_message = response_data.get('error', 'Unknown error')
                error_code = response_data.get('error_code', 'N/A')
                raise Exception(f"Failed to send SMS: {error_message} (Error code: {error_code})")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request to SMSC failed: {str(e)}")
            raise Exception("Failed to send SMS: Unknown error")
