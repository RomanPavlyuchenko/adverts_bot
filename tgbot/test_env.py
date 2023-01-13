import os
import os

SECRET_KEY = os.environ.get('token')
print(SECRET_KEY)
# load_dotenv будет искать файл .env, и, если он его найдет,
# из него будут загружены переменные среды
