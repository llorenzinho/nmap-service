from datetime import datetime

from sqlmodel import Session, select

from nmap_service.cmd.models import NmapResult
from nmap_service.core.enums import TaskStatus
from .models import NmapJob
from .schemas import CreateJobSchema


class NmapJobRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_job(self, sch: CreateJobSchema) -> NmapJob:
        job = NmapJob(
            created_at=datetime.now(),
            target=sch.target,
            ports=",".join(sch.ports) if sch.ports and len(sch.ports) > 0 else None,
        )
        self.session.add(job)
        self.session.commit()
        return job

    def start_job(self, id: str) -> NmapJob | None:
        data = self.session.get(NmapJob, id)
        if not data:
            return None
        data.started_at = datetime.now()
        data.status = TaskStatus.RUNNING
        self.session.add(data)
        self.session.commit()
        return data

    def complete_job(self, id: str, result: NmapResult) -> NmapJob | None:
        data = self.session.get(NmapJob, id)
        if not data:
            return None
        data.status = TaskStatus.COMPLETED
        data.completed_at = datetime.now()
        data.result = result.model_dump()
        self.session.add(data)
        self.session.commit()
        return data

    def set_job_error(self, id: str, error: Exception) -> NmapJob | None:
        data = self.session.get(NmapJob, id)
        if not data:
            return None
        data.status = TaskStatus.FAILED
        data.error_message = str(error)
        self.session.add(data)
        self.session.commit()
        return data

    def get_by_id(self, id: str) -> NmapJob | None:
        return self.session.get(NmapJob, id)

    def list_jobs(self) -> list[NmapJob]:
        return list(self.session.exec(select(NmapJob)).all())
