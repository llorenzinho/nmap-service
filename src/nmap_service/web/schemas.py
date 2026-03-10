from datetime import datetime

from pydantic import BaseModel

from nmap_service.cmd.models import HostResult
from nmap_service.core.enums import ScanType


class RunNmapJobRequest(BaseModel):
    target: str
    scan_type: ScanType


class NmapResultResponse(BaseModel):
    target: str
    start: datetime
    end: datetime | None = None
    command: str
    result: list[HostResult]  # TODO: externalize this by using another model
