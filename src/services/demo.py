from pprint import pprint
from typing import List
from bson import ObjectId
from fastapi import HTTPException
from pydantic import TypeAdapter
from models import DemoNew, Demo, DemoUpdate
from repository import DemoRepository

demo_repository = DemoRepository()


def create_demo_record(demo_record: DemoNew):
    return create_one_demo_record(demo_record)


def create_one_demo_record(demo_record: DemoNew) -> DemoNew:
    created_record = demo_record.model_dump(
        exclude_unset=False,
        exclude=demo_record.get_excluded_fields()
    )

    return DemoNew(**demo_repository.create_one(obj=created_record))


def get_all_demo_records() -> List[Demo]:
    records = demo_repository.get_many()

    return TypeAdapter(List[Demo]).validate_python(records)


def get_one_by_id(demo_id: str) -> Demo:
    return Demo(**demo_repository.get_one(query={'_id': ObjectId(demo_id)}))


def get_demo_or_fail(demo_id: str) -> Demo:
    demo_record = get_one_by_id(demo_id)

    if not demo_record:
        raise HTTPException(status_code=404, detail='User not found')

    return demo_record


def update_one_by_id(demo_id: str, demo: Demo) -> Demo:
    # stored_demo = get_demo_or_fail(demo_id)
    # pprint(stored_demo)
    # dump_model = demo.model_dump(exclude_unset=True)
    # pprint(dump_model)
    # updated_demo = stored_demo.model_copy(update=dump_model)
    # pprint(updated_demo)

    demo_repository.update_one(
        query={'_id': ObjectId(demo_id)},
        update={"$set": demo.model_dump(exclude_unset=True, exclude=demo.get_excluded_fields())}
    )

    return get_one_by_id(demo_id)

