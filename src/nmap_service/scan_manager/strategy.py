from abc import ABC, abstractmethod
from concurrent.futures import Future, ThreadPoolExecutor
from collections.abc import Callable

from nmap_service.cmd.models import NmapResult, NmapScanConfig
from nmap_service.cmd.nmap import NmapRunner

OnCompleteCallback = Callable[[str, NmapResult], None]
OnErrorCallback = Callable[[str, Exception], None]


class ScanStrategy(ABC):

    @abstractmethod
    def launch(
        self,
        job_id: str,
        config: NmapScanConfig,
        on_complete: OnCompleteCallback,
        on_error: OnErrorCallback,
    ) -> None: ...


class ThreadScanStrategy(ScanStrategy):

    def __init__(self, runner: NmapRunner, max_workers: int = 4):
        self.runner = runner
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="nmap-scan",
        )

    def launch(
        self,
        job_id: str,
        config: NmapScanConfig,
        on_complete: OnCompleteCallback,
        on_error: OnErrorCallback,
    ) -> None:
        """Sottomette lo scan al thread pool e aggancia i callback sul Future."""

        future: Future[NmapResult] = self._executor.submit(
            self.runner.scan, config.target, config.ports, config.extra_flags
        )

        future.add_done_callback(
            lambda f: self._handle_future(f, job_id, on_complete, on_error)
        )

        # logger.info("[ThreadStrategy] job=%s avviato su thread pool", job_id)

    def _handle_future(
        self,
        future: Future[NmapResult],
        job_id: str,
        on_complete: OnCompleteCallback,
        on_error: OnErrorCallback,
    ) -> None:
        """Invocato automaticamente dal ThreadPoolExecutor al termine del Future."""
        exc = future.exception()
        if exc is not None:
            # logger.error("[ThreadStrategy] job=%s fallito: %s", job_id, exc)
            on_error(job_id, exc) # type: ignore
        else:
            # logger.info("[ThreadStrategy] job=%s completato", job_id)
            on_complete(job_id, future.result())
