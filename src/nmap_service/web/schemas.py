from pydantic import BaseModel

from nmap_service.core.enums import ScanType


class RunNmapJobRequest(BaseModel):
    target: str
    scan_type: ScanType
