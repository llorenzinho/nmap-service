import re
from datetime import datetime
from ipaddress import ip_address

from pydantic import BaseModel, field_validator

from nmap_service.cmd.models import HostResult
from nmap_service.core.enums import ScanType


def is_valid_fqdn(v: str) -> bool:
    if v == 'localhost':
        return True
    pattern = r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))*\.[A-Za-z]{2,63}$"
    return bool(re.match(pattern, v))


def is_valid_ip(v: str) -> bool:
    try:
        ip_address(v)
        return True
    except ValueError:
        return False


class RunNmapJobRequest(BaseModel):
    target: str
    scan_type: ScanType

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        if is_valid_ip(v) or is_valid_fqdn(v):
            return v
        raise ValueError(f"'{v}' non è un indirizzo IP o FQDN valido")


class NmapResultResponse(BaseModel):
    target: str
    start: datetime
    end: datetime | None = None
    command: str
    result: list[HostResult]  # TODO: externalize this by using another model
