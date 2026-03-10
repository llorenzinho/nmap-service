from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from nmap_service.cmd.deps import NmapRunnerDep
from nmap_service.config.app import ConfigDep
from nmap_service.core.enums import ScanStrategyType
from nmap_service.database.engine import get_session
from nmap_service.scan_manager.manager import ScanManager
from nmap_service.scan_manager.repository import NmapJobRepository
from .strategy import LocalScanStrategy, ScanStrategy


@lru_cache
def __get_threadpool(num_worker: int) -> ThreadPoolExecutor:
    return ThreadPoolExecutor(max_workers=num_worker, thread_name_prefix="thread-pool")


@lru_cache
def __get_process_pool(num_worker: int) -> ProcessPoolExecutor:
    return ProcessPoolExecutor(max_workers=num_worker)


def __get_strategy(runner: NmapRunnerDep, config: ConfigDep) -> ScanStrategy:
    match config.scan_strategy.strategy:
        case ScanStrategyType.THREAD:
            pool = __get_threadpool(config.scan_strategy.n_executor)  # singleton
            return LocalScanStrategy(executor=pool, runner=runner)
        case ScanStrategyType.PROCESS:
            pool = __get_process_pool(config.scan_strategy.n_executor)  # singleton
            return LocalScanStrategy(executor=pool, runner=runner)
        case _:
            raise ValueError(
                f"Scan strategy {config.scan_strategy.strategy} not supported"
            )


ScanStrategyDep = Annotated[ScanStrategy, Depends(__get_strategy)]


def __get_repository(session: Session = Depends(get_session)) -> NmapJobRepository:
    return NmapJobRepository(session=session)


def __get_manager(
    strategy: ScanStrategyDep, repo: NmapJobRepository = Depends(__get_repository)
) -> ScanManager:
    return ScanManager(repository=repo, strategy=strategy)


ScanManagerDep = Annotated[ScanManager, Depends(__get_manager)]
