from pydantic import BaseModel, Field


class RunnerCfg(BaseModel):
    timeout: int = Field(default=300, min=1)  # TODO: fix pylance no overload
    use_shell: bool = False


class NmapCfg(RunnerCfg): ...
