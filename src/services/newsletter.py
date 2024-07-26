from bson import ObjectId
from models import NewsletterUpdate, Newsletter
from repository import NewsletterRepository


newsletter_repository = NewsletterRepository()


def create_newsletter(text, photo_id=None):
    model = Newsletter(
        text=text,
        photo_id=photo_id,
        status='new'
    )
    model_dict = model.model_dump(exclude=model.get_excluded_fields())

    newsletter_repository.create_one(model_dict)


def update_newsletter_by_id(newsletter_id: str, model_update: NewsletterUpdate) -> dict:
    model_update_dict = model_update.model_dump(exclude_unset=True, exclude=model_update.get_excluded_fields())

    newsletter_repository.update_one(
        query={"_id": ObjectId(newsletter_id)},
        update={"$set": model_update_dict}
    )

    return model_update_dict
