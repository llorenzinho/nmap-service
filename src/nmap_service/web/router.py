from fastapi import APIRouter

router = APIRouter(prefix="api/v1/scans", tags=["v1"])


@router.post("")
def run_job(): ...


@router.get("")
def list_jobs(): ...


@router.get("{scan_id:str}/results")
def get_job_detail(scan_id: str): ...
