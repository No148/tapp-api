from repository import UserRepository
from services.lootbox import generate_and_create_lootbox
user_repository = UserRepository()

users = user_repository.get_many()

for user in users:
    user_id = user['id']
    print(user_id)
    generate_and_create_lootbox(user_id)
