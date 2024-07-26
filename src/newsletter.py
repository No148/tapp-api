import asyncio
import telegram

from models import Newsletter, NewsletterUpdate, User, UserUpdate
from repository import UserRepository, NewsletterRepository
from services.newsletter import update_newsletter_by_id, create_newsletter
from services.user import update_user_by_user_id
from utils.env import BOT_TOKEN

user_repository = UserRepository()
newsletter_repository = NewsletterRepository()


async def newsletters_processing():
    newsletters = newsletter_repository.get_many({
        'status': 'new'
    })

    for newsletter in newsletters:
        try:
            newsletter = Newsletter(**newsletter)

            update_newsletter_by_id(newsletter.id, NewsletterUpdate(
                status='in_progress'
            ))

            print(f'Start newsletter {newsletter.id}')

            users = user_repository.get_many()
            j = 0

            for user in users:
                j += 1
                user = User(**user)

                if newsletter.id in user.newsletters:
                    continue

                try:
                    if newsletter.photo_id:
                        await telegram.Bot(token=BOT_TOKEN).send_photo(
                            chat_id=user.id,
                            photo=newsletter.photo_id,
                            caption=newsletter.text,
                            parse_mode='HTML',
                        )

                    else:
                        await telegram.Bot(token=BOT_TOKEN).send_message(
                            chat_id=user.id,
                            text=newsletter.text,
                            parse_mode='HTML',
                        )

                    update_user_by_user_id(user.id, UserUpdate(
                        newsletters=user.newsletters + [newsletter.id]
                    ))

                    print(f'[{j}] Newsletter {newsletter.id} SUCCESSFULLY sent to user {user.id}')

                except Exception as err:
                    print(f'[{j}] ERROR while trying send newsletter {newsletter.id} to user {user.id}. Error: \r\n {err}')

                # If you're sending bulk notifications to multiple users, the API will not allow more than 30 messages per second or so. Consider spreading out notifications over large intervals of 8—12 hours for best results.
                await asyncio.sleep(0.05)

            update_newsletter_by_id(newsletter.id, NewsletterUpdate(
                status='success'
            ))

        except Exception as err:
            update_newsletter_by_id(newsletter.id, NewsletterUpdate(
                status='error'
            ))


def save_excluded_user_ids(newsletter):
    update_newsletter_by_id(newsletter.id, NewsletterUpdate(
        success_user_ids=newsletter.success_user_ids,
        error_user_ids=newsletter.error_user_ids
    ))


# create_newsletter('test newsletter 1')
# create_newsletter('test newsletter 2')

asyncio.run(newsletters_processing())
