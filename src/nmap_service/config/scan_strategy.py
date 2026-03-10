from pydantic import BaseModel, model_validator

from nmap_service.core.enums import ScanStrategyType


class StrategyCfg(BaseModel):
    strategy: ScanStrategyType
    n_executor: int | None = None

    @model_validator(mode="after")
    def validate_executor(self):
        if self.strategy in [ScanStrategyType.THREAD] and self.n_executor is None:
            raise ValueError(
                f"n_executor must be set for given scan strategy: {self.strategy}"
            )
        return self
