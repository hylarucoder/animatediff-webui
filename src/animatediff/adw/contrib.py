import pydantic as pt
from pydantic.alias_generators import to_camel


class PtBaseModel(pt.BaseModel):
    model_config = pt.ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )
