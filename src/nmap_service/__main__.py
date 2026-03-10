import uvicorn

from nmap_service.config import cfg
from nmap_service.core.enums import LogLevel

if __name__ == "__main__":
    configs = cfg()
    uvicorn.run(
        "nmap_service.web.asgi:app",
        host=configs.server.host,
        port=configs.server.port,
        reload=configs.log.level is LogLevel.DEBUG,
        forwarded_allow_ips="*",
        proxy_headers=True,
    )
