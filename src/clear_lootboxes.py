from models import LootBoxUpdate
from repository import LootboxRepository
from services.lootbox import update_lootbox_by_id

lootbox_repository = LootboxRepository()

lootboxes = lootbox_repository.get_many()

for lootbox in lootboxes:
    lootbox_id = lootbox['id']
    print(lootbox_id)
    update_lootbox_by_id(lootbox_id, LootBoxUpdate(
        activated=False,
        user=None
    ))
