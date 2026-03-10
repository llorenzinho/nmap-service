from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Text
from sqlmodel import Column, Field, SQLModel

from nmap_service.cmd.models import HostResult
from nmap_service.core.enums import TaskStatus


class NmapJobBase(SQLModel):
    # Target della scansione
    target: str = Field(index=True, description="IP, range CIDR o hostname")

    # Stato
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)


class NmapJob(NmapJobBase, table=True):
    __tablename__ = "nmap_jobs"  # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)  # type: ignore
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)

    # Output
    result: list[dict[Any, Any]] | None = Field(default=None, sa_column=Column(JSON))

    # Errors
    error_message: str | None = Field(default=None, sa_column=Column(Text))
    exit_code: int | None = Field(default=None)

    @property
    def result_(self) -> list[HostResult]:
        return (
            [HostResult.model_validate(d) for d in self.result] if self.result else []
        )
