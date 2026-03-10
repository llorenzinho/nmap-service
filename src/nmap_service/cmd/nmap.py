from nmap_service.config.runner import NmapCfg, RunnerCfg
from nmap_service.core.log import get_logger
from .models import NmapResult, NmapScanConfig
from .run import CommandRunner


class NmapRunner(CommandRunner):
    NMAP_BIN = "nmap"

    def __init__(self, cfg: NmapCfg):
        super().__init__(cfg=RunnerCfg.model_validate(cfg.model_dump()))
        self.logger = get_logger(NmapRunner.__name__)

    def scan(
        self,
        target: str,
        ports: str | None = None,
        extra_flags: str = "",
    ) -> NmapResult:

        config = NmapScanConfig(
            target=target,
            ports=ports,
            extra_flags=extra_flags,
        )
        cmd = self.build_command(config)
        self.logger.info(f"Executing command: {cmd}")
        return self._execute_and_return_result(cmd)

    @staticmethod
    def build_command(config: NmapScanConfig) -> str:
        cmd = [NmapRunner.NMAP_BIN]

        if config.extra_flags:
            cmd.append(config.extra_flags)

        if config.ports:
            cmd += ["-p", config.ports]

        cmd += ["-oX", "-"]
        cmd.append(config.target)

        return " ".join(cmd)

    def _execute_and_return_result(self, command: str) -> NmapResult:
        result = self.run(command)

        if not result.success:
            raise RuntimeError(
                f"nmap returned {result.returncode}.\n"
                f"cmd: {result.command}\n"
                f"stderr: {result.stderr}"
            )

        return NmapResult(xml_output=result.stdout)
