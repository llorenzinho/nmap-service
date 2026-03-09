from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, Text
from sqlmodel import Column, Field, SQLModel

from nmap_service.core.enums import TaskStatus


class NmapJobBase(SQLModel):
    # Target della scansione
    target: str = Field(index=True, description="IP, range CIDR o hostname")
    ports: str | None = Field(
        default=None, description="Es: '22,80,443' oppure '1-1024'"
    )

    # Stato
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)


class NmapJob(NmapJobBase, table=True):
    __tablename__ = "nmap_jobs"  # type: ignore

    id: str | None = Field(default_factory=uuid4, primary_key=True)

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)  # type: ignore
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)

    # Output
    result: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))

    # Errors
    error_message: str | None = Field(default=None, sa_column=Column(Text))
    exit_code: int | None = Field(default=None)
