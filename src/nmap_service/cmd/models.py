# TODO: fix typing pylance

import xml.etree.ElementTree as ET
from typing import Any

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator


class CommandResult(BaseModel):
    """Risultato dell'esecuzione di un comando di sistema."""

    command: str = Field(..., description="Comando eseguito")
    stdout: str = Field(..., description="Output standard del processo")
    stderr: str = Field(..., description="Output di errore del processo")
    returncode: int = Field(..., description="Codice di uscita del processo")

    @computed_field
    @property
    def success(self) -> bool:
        return self.returncode == 0

    def __str__(self) -> str:
        return self.stdout


class NmapScanConfig(BaseModel):
    """Configurazione per una scansione nmap."""

    target: str = Field(
        ..., min_length=1, description="Host, IP o range CIDR da scansionare"
    )
    ports: str | None = Field(
        default=None,
        description="Port to scan (eq. '22,80,443' oppure '1-1024')",
        pattern=r"^[\d,\-]+$",
    )
    extra_flags: str = Field(
        default="", description="Flag nmap aggiuntivi (es. '-sV -O')"
    )

    @field_validator("target")
    @classmethod
    def target_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError(
                "Il target non può essere una stringa vuota o di soli spazi"
            )
        return v.strip()

    @field_validator("extra_flags")
    @classmethod
    def flags_must_not_contain_ox(cls, v: str) -> str:
        if "-oX" in v or "-oA" in v or "-oN" in v or "-oG" in v:
            raise ValueError(
                "Non specificare flag di output (-oX, -oA, -oN, -oG) in extra_flags: "
                "viene gestito automaticamente dalla classe."
            )
        return v.strip()


class PortInfo(BaseModel):
    """Informazioni su una singola porta aperta."""

    port: int = Field(..., ge=1, le=65535, description="Numero di porta")
    protocol: str = Field(..., description="Protocollo (tcp/udp)")
    service: str = Field(
        default="unknown", description="Nome del servizio rilevato da nmap"
    )

    @field_validator("protocol")
    @classmethod
    def protocol_must_be_valid(cls, v: str) -> str:
        if v.lower() not in {"tcp", "udp", "sctp"}:
            raise ValueError(f"Protocollo non riconosciuto: {v!r}")
        return v.lower()


class HostResult(BaseModel):
    ip: str = Field(..., description="Indirizzo IP dell'host")
    open_ports: list[PortInfo] = Field(
        default_factory=list, description="Elenco porte aperte"
    )


class NmapResult(BaseModel):
    """Risultato completo di una scansione nmap."""

    xml_output: str = Field(..., min_length=1, description="Output XML grezzo di nmap")
    hosts: list[HostResult] = Field(
        default_factory=list, description="Host rilevati con le loro porte"
    )

    @model_validator(mode="before")
    @classmethod
    def parse_xml_into_hosts(cls, data: dict[Any, Any]) -> dict[Any, Any]:
        """Parsa l'XML di nmap e popola automaticamente il campo hosts."""
        xml_string = data.get("xml_output", "")
        if not xml_string:
            return data

        try:
            root = ET.fromstring(xml_string)
        except ET.ParseError as exc:
            raise ValueError(f"L'output nmap non è XML valido: {exc}") from exc

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
