from abc import ABC, abstractmethod
from collections.abc import Callable
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor

from nmap_service.cmd.models import NmapResult, NmapScanConfig
from nmap_service.cmd.nmap import NmapRunner
from nmap_service.core.log import get_logger

OnCompleteCallback = Callable[[str, NmapResult], None]
OnErrorCallback = Callable[[str, Exception], None]
OnSubmitMethod = Callable[[str], None]


class ScanStrategy(ABC):

    @abstractmethod
    def launch(
        self,
        job_id: str,
        config: NmapScanConfig,
        on_submit: OnSubmitMethod,
        on_complete: OnCompleteCallback,
        on_error: OnErrorCallback,
    ) -> None: ...


class LocalScanStrategy(ScanStrategy):

    def __init__(
        self, runner: NmapRunner, executor: ThreadPoolExecutor | ProcessPoolExecutor
    ):
        self.runner = runner
        self._executor = executor
        self.logger = get_logger(LocalScanStrategy.__name__)

    def launch(
        self,
        job_id: str,
        config: NmapScanConfig,
        on_submit: OnSubmitMethod,
        on_complete: OnCompleteCallback,
        on_error: OnErrorCallback,
    ) -> None:
        future: Future[NmapResult] = self._executor.submit(
            self.runner.scan, config.target, config.ports, config.extra_flags
        )
        on_submit(job_id)

        future.add_done_callback(
            lambda f: self._handle_future(f, job_id, on_complete, on_error)
        )

        self.logger.debug(f"Submitted job {job_id}")

    def _handle_future(
        self,
        future: Future[NmapResult],
        job_id: str,
        on_complete: OnCompleteCallback,
        on_error: OnErrorCallback,
    ) -> None:
        exc = future.exception()
        if exc is not None:
            self.logger.error(f"Job {job_id} failed", "exc", str(exc))
            on_error(job_id, exc)  # type: ignore
        else:
            self.logger.info(f"Job {job_id} done")
            on_complete(job_id, future.result())
