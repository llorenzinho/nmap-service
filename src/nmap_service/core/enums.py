from enum import Enum


class ScanType(str, Enum):
    QUICK = "QUICK"
    FULL = "FULL"
    SERVICE_DETECTION = "SERVICE_DETECTION"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ScanStrategyType(str, Enum):
    THREAD = "THREAD"
    PROCESS = "PROCESS"
