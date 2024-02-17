from datetime import datetime, timezone

from pydantic import ConfigDict, BaseModel


class RWModel(BaseModel):
    class Config(ConfigDict):
        populate_by_name = True  # instructing Pydantic to populate fields based on their names rather than their positions.
        json_encoders = {
            datetime: lambda dt: dt.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        }

