import os
import requests
from dotenv import load_dotenv

load_dotenv()

telegram_token = os.getenv('telegram_token')
log_chat_id = os.getenv('log_chat_id')

with open('log.txt') as f:
    for line in f:
        pass
    last_line = line

log_msg = line
print(log_msg)
telegram_msg = requests.get(f'https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={log_chat_id}&text={log_msg}')
