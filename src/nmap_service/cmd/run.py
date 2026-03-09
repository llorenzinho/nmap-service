import shlex
import subprocess

from nmap_service.config.runner import RunnerCfg
from .models import CommandResult


class CommandRunner:
    def __init__(self, cfg: RunnerCfg) -> None:
        self.timeout = cfg.timeout
        self.shell = cfg.use_shell

    def run(self, command: str, input_data: str | None = None) -> CommandResult:
        args = command if self.shell else shlex.split(command)

        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            shell=self.shell,
            input=input_data,
        )

        return CommandResult(
            command=command,
            stdout=proc.stdout,
            stderr=proc.stderr,
            returncode=proc.returncode,
        )
