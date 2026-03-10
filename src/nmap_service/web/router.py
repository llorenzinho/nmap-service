from fastapi import APIRouter

from nmap_service.core.log import get_logger
from nmap_service.scan_manager.deps import ScanManagerDep

router = APIRouter(prefix="/scans", tags=["v1"])


@router.post("")
def run_job(): ...


@router.get("")
def list_jobs(manager: ScanManagerDep):
    get_logger().info(manager)


@router.get("{scan_id:str}/results")
def get_job_detail(scan_id: str): ...
