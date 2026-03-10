from fastapi import APIRouter, HTTPException, status

from nmap_service.scan_manager.deps import ScanManagerDep
from nmap_service.scan_manager.schemas import (
    JobStatusListResponse,
    JobStatusResponse,
    SubmitJobSchema,
)
from .schemas import NmapResultResponse, RunNmapJobRequest

router = APIRouter(prefix="/scans", tags=["v1"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def run_job(manager: ScanManagerDep, body: RunNmapJobRequest) -> str:
    return manager.submit(type=body.scan_type, sch=SubmitJobSchema(target=body.target))


@router.get("")
def list_jobs(manager: ScanManagerDep) -> list[JobStatusListResponse]:
    data = manager.list_jobs()
    return data


@router.get("/{scan_id:str}")
def get_job_detail(scan_id: str, manager: ScanManagerDep) -> JobStatusResponse | None:
    data = manager.get_job_detail(scan_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{scan_id} not found"
        )
    return data


@router.get("/{scan_id:str}/results")
def get_job_result(scan_id: str, manager: ScanManagerDep) -> NmapResultResponse | None:
    data = manager.get_job_result(scan_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{scan_id} not found"
        )
    return data
