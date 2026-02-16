from pydantic import BaseModel, Field


class PlatformInfo(BaseModel):
    name: str = "حزم طويق – HAZM TUWAIQ"
    version: str = "1.0.0"
    status: str = "ok"


class SystemStatus(BaseModel):
    healthy: bool = True
    status: str = "ok"
    message: str = "Core API operational"


class GenericAction(BaseModel):
    payload: dict = Field(default_factory=dict)


class GenericResponse(BaseModel):
    ok: bool
    message: str
    data: dict = Field(default_factory=dict)
