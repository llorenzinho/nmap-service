from fastapi import APIRouter

from nmap_service.scan_manager.deps import ScanManagerDep
from nmap_service.scan_manager.schemas import SubmitJobSchema
from nmap_service.web.schemas import RunNmapJobRequest

router = APIRouter(prefix="/scans", tags=["v1"])


@router.post("")
def run_job(manager: ScanManagerDep, body: RunNmapJobRequest) -> str:
    return manager.submit(type=body.scan_type, sch=SubmitJobSchema(target=body.target))


@router.get("")
def list_jobs(manager: ScanManagerDep):
    data = manager.list_jobs()
    return data


@router.get("{scan_id:str}/results")
def get_job_detail(scan_id: str, manager: ScanManagerDep):
    data = manager.get_job_status(scan_id)
    return data
