from pydantic import BaseModel


class DatabaseCfg(BaseModel):
    user: str
    password: str
    host: str
    port: int = 5432
    db: str

    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    echo_sql: bool = False

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.db}"
        )
