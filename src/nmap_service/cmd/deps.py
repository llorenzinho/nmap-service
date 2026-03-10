from typing import Annotated

from fastapi import Depends

from nmap_service.config.app import cfg
from .nmap import NmapRunner


def __get_runner() -> NmapRunner:
    config = cfg().runner
    return NmapRunner(config)


NmapRunnerDep = Annotated[NmapRunner, Depends(__get_runner)]
