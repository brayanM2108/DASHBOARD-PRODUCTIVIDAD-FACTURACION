from __future__ import annotations

from pydantic import BaseModel, Field


class ProcessEntry(BaseModel):
    name: str = Field(..., min_length=1)
    seconds: int = Field(..., ge=1)


class ModuleTimes(BaseModel):
    rips: int = Field(default=45, ge=1)
    legalizations: int = Field(default=90, ge=1)
    billing: int = Field(default=45, ge=1)


class ProcessConfigResponse(BaseModel):
    processes: list[ProcessEntry] = []
    module_times: ModuleTimes = ModuleTimes()


class ProcessConfigUpdate(BaseModel):
    processes: list[ProcessEntry] = []
    module_times: ModuleTimes = ModuleTimes()
