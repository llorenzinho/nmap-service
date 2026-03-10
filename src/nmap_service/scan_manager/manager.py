from datetime import datetime
from itertools import chain

from nmap_service.cmd.models import NmapResult, NmapScanConfig
from nmap_service.cmd.nmap import NmapRunner
from nmap_service.core.enums import ScanType, TaskStatus
from nmap_service.core.log import get_logger
from nmap_service.web.schemas import NmapResultResponse
from .repository import NmapJobRepository
from .schemas import (
    CreateJobSchema,
    ErrorSummaryResponse,
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
        self.logger = get_logger(ScanManager.__name__)

    def __build_flags(self, type: ScanType) -> str:
        if type == ScanType.QUICK:
            return "-T4 -F"
        if type == ScanType.FULL:
            return "-T4 -p-"
        if type == ScanType.SERVICE_DETECTION:
            return "-sV"
        raise ValueError("Unsupported")

    def submit(self, type: ScanType, sch: SubmitJobSchema) -> str:
        self.logger.info(
            f"Running scan with parameters type: {type.value}, data: {sch.model_dump()}"
        )
        flags = self.__build_flags(type)
        config = NmapScanConfig(
            target=sch.target,
            ports=",".join(sch.ports) if sch.ports else None,
            extra_flags=flags,
        )
        job = self.repo.create_job(
            CreateJobSchema(
                target=sch.target,
                ports=sch.ports,
                extra_flags=flags,
                command=NmapRunner.build_command(config),
            )
        )
        if not job.id:
            self.logger.error("Failed job creation")
            raise RuntimeError("Job Id Is null")

        self.logger.debug(f"Job Record Created Succesfully: {job.id}")

        self.strategy.launch(
            job_id=str(job.id),
            config=config,
            on_submit=self.__on_submit,
            on_complete=self.__on_complete,
            on_error=self.__on_error,
        )
        return str(job.id)

    def __on_submit(self, id: str):
        self.repo.start_job(id)

    def __on_complete(self, id: str, result: NmapResult):
        self.repo.complete_job(id, result)

    def __on_error(self, id: str, e: Exception):
        self.repo.set_job_error(id, e)

    def get_job_detail(self, id: str) -> JobStatusResponse | None:
        data = self.repo.get_by_id(id)
        if not data:
            return None
        status = data.status
        if status == TaskStatus.FAILED:
            return JobStatusResponse(
                status=status,
                summary=ErrorSummaryResponse(
                    message=data.error_message,  # type: ignore (this must be populated)
                ),
            )
        if status != TaskStatus.COMPLETED:
            return JobStatusResponse(status=status)

        result = data.result_
        if not result:
            raise ValueError(f"job with id {data.id} is completed with no results")

        ips: list[str] = []
        ports: list[list[int]] = []
        for d in result:
            ips.append(d.ip)
            ports.append([op.port for op in d.open_ports])

        ports_flat = list(chain.from_iterable(ports))

        elapsed = (
            data.completed_at - data.created_at
            if data.completed_at is not None
            else datetime.now() - data.created_at
        )
        t = elapsed.total_seconds() if elapsed else None
        return JobStatusResponse(
            status=status,
            summary=SummaryResponse(
                elapsed_seconds=t,
                num_ports=len(ports_flat),
                target=data.target,
            ),
        )

    def list_jobs(self) -> list[JobStatusListResponse]:
        data = self.repo.list_jobs()
        return [
            JobStatusListResponse(
                id=str(d.id),
                status=d.status,
                timestamp=d.started_at,
            )
            for d in data
        ]

    def get_job_result(self, id: str) -> NmapResultResponse | None:
        data = self.repo.get_by_id(id)
        if not data:
            return None

        return NmapResultResponse(
            target=data.target,
            command=data.command,
            start=data.created_at,
            end=data.completed_at,
            result=data.result_,
        )
