import requests
import os

from datetime import datetime
from config import AGE_OF_ACCOUNT
from utils.env import WORK_DIR, UPLOADS_PATH


def download_image_by_url(url: str, filename: str, path: str) -> str:
    if not url or not filename or not path:
        return ''

    f_name, file_extension = os.path.splitext(url)

    path = WORK_DIR / UPLOADS_PATH / path
    path.mkdir(parents=True, exist_ok=True)

    file_path = str(path) + '/' + filename + file_extension

    with open(file_path, 'wb') as handle:
        response = requests.get(url, stream=True)

        if not response.ok:
            print(response)

            return ''

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

        return filename + file_extension


def get_age_of_account_by_user_id(user_id):
    account_registration_year = 2024

    for min_id, year in AGE_OF_ACCOUNT.items():
        if user_id > min_id:
            account_registration_year = year
            break

    return datetime.utcnow().year - (account_registration_year + 1)
