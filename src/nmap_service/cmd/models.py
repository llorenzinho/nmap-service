# TODO: fix typing pylance

import xml.etree.ElementTree as ET
from typing import Any

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator


class CommandResult(BaseModel):
    """System command execution result"""

    command: str = Field(..., description="Executed command")
    stdout: str = Field(..., description="Proc STDOut")
    stderr: str = Field(..., description="Proc STDErr")
    returncode: int = Field(..., description="Proc exit code")

    @computed_field
    @property
    def success(self) -> bool:
        return self.returncode == 0

    def __str__(self) -> str:
        return self.stdout


class NmapScanConfig(BaseModel):

    target: str = Field(..., min_length=1, description="Host, IP or CIDR")
    ports: str | None = Field(
        default=None,
        description="Port to scan (eq. '22,80,443' oppure '1-1024')",
        pattern=r"^[\d,\-]+$",
    )
    extra_flags: str = Field(default="", description="Flag nmap (es. '-sV -O')")

    @field_validator("target")
    @classmethod
    def target_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Target must be not empty")
        return v.strip()

    @field_validator("extra_flags")
    @classmethod
    def flags_must_not_contain_ox(cls, v: str) -> str:
        if "-oX" in v or "-oA" in v or "-oN" in v or "-oG" in v:
            raise ValueError(
                "Do not manually specify (-oX, -oA, -oN, -oG) in extra_flags"
            )
        return v.strip()


class PortInfo(BaseModel):

    port: int = Field(..., ge=1, le=65535, description="Port Number")
    protocol: str = Field(..., description="Protocol (tcp/udp)")
    service: str = Field(default="unknown", description="Service name")

    @field_validator("protocol")
    @classmethod
    def protocol_must_be_valid(cls, v: str) -> str:
        if v.lower() not in {"tcp", "udp", "sctp"}:
            raise ValueError(f"Unrecognized protocol: {v!r}")
        return v.lower()


class HostResult(BaseModel):
    ip: str = Field(..., description="Host's IP address")
    open_ports: list[PortInfo] = Field(default_factory=list, description="Open ports")


class NmapResult(BaseModel):
    """Full NMAP scan result"""

    xml_output: str = Field(..., min_length=1, description="RAW XML Output")
    hosts: list[HostResult] = Field(default_factory=list, description="Hosts")

    @model_validator(mode="before")
    @classmethod
    def parse_xml_into_hosts(cls, data: dict[Any, Any]) -> dict[Any, Any]:
        xml_string = data.get("xml_output", "")
        if not xml_string:
            return data

        try:
            root = ET.fromstring(xml_string)
        except ET.ParseError as exc:
            raise ValueError(f"nmap xml output invalid: {exc}") from exc

        hosts: list[dict] = []
        for host in root.findall("host"):
            addr_el = host.find("address[@addrtype='ipv4']")
            if addr_el is None:
                addr_el = host.find("address")
            if addr_el is None:
                continue
            ip = addr_el.get("addr", "unknown")

            open_ports: list[dict] = []
            for port_el in host.findall(".//port"):
                state_el = port_el.find("state")
                if state_el is None or state_el.get("state") != "open":
                    continue
                service_el = port_el.find("service")
                open_ports.append(
                    {
                        "port": int(port_el.get("portid", 0)),
                        "protocol": port_el.get("protocol", "tcp"),
                        "service": (
                            service_el.get("name", "unknown")
                            if service_el is not None
                            else "unknown"
                        ),
                    }
                )

            hosts.append({"ip": ip, "open_ports": open_ports})

        data["hosts"] = hosts
        return data
