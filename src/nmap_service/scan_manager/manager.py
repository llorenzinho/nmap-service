from nmap_service.cmd.models import NmapResult, NmapScanConfig
from nmap_service.core.enums import ScanType, TaskStatus
from .repository import NmapJobRepository
from .schemas import (
    CreateJobSchema,
    JobStatusListResponse,
    JobStatusResponse,
    SubmitJobSchema,
    SummaryResponse,
)
from .strategy import ScanStrategy


class ScanManager:
    def __init__(self, strategy: ScanStrategy, repository: NmapJobRepository):
        self.strategy = strategy
        self.repo = repository

    def __build_flags(self, type: ScanType) -> str:
        if type == ScanType.QUICK:
            return "-T4 -F"
        if type == ScanType.FULL:
            return "-T4 -p-"
        if type == ScanType.SERVICE_DETECTION:
            return "-sV"
        raise ValueError("Unsupported")

    def submit(self, type: ScanType, sch: SubmitJobSchema) -> str:
        flags = self.__build_flags(type)
        job = self.repo.create_job(
            CreateJobSchema(
                target=sch.target,
                ports=sch.ports,
                extra_flags=flags,
            )
        )
        if not job.id:
            raise RuntimeError("Job Id Is null")

        self.strategy.launch(
            job_id=job.id,
            config=NmapScanConfig(
                target=sch.target,
                ports=",".join(sch.ports) if sch.ports else None,
                extra_flags=flags,
                timeout=30,  # TODO: use configs
            ),
            on_complete=self.__on_complete,
            on_error=self.__on_error,
        )
        return job.id

    def __on_complete(self, id: str, result: NmapResult):
        self.repo.complete_job(id, result)

    def __on_error(self, id: str, e: Exception):
        self.repo.set_job_error(id, e)

    def get_job_status(self, id: str) -> JobStatusResponse | None:
        data = self.repo.get_by_id(id)
        if not data:
            return None
        status = data.status
        if status != TaskStatus.COMPLETED:
            return JobStatusResponse(status=status)
        port_list = [d for d in data.ports.split(",") if len(d) > 0] if data.ports else []
        return JobStatusResponse(
            status=status,
            summary=SummaryResponse(
                elapsed_time=data.completed_at - data.created_at if data.completed_at is not None else None,
                ports=port_list,
                num_ports=len(port_list),
                target=data.target,
            ),
        )

    def list_jobs(self) -> list[JobStatusListResponse]:
        data = self.repo.list_jobs()
        return [
            JobStatusListResponse(
                id=d.id, # type: ignore
                status=d.status,
                timestamp=d.started_at,
            )
            for d in data
        ]
