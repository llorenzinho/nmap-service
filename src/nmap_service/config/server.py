from pydantic import BaseModel


class ServerCfg(BaseModel):
    host: str = "0.0.0.0"
    port: int = 3000
