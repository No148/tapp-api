from models import User, UserUpdate
from repository import UserRepository
from services.user import update_user_by_user_id

user_repository = UserRepository()

users = user_repository.get_many()

for user in users:
    user = User(**user)

    print(user.id)

    for index, user_task in enumerate(user.tasks):
        if user_task['_id'] == '6658219ff47a17441f9e6af9' and 'lang' not in user_task:
            user.tasks[index]['lang'] = 'en'
            update_user_by_user_id(user.id, UserUpdate(tasks=user.tasks))
            break
