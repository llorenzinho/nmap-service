from enum import Enum


class ScanType(Enum, str):
    QUICK = "QUICK"
    FULL = "FULL"
    SERVICE_DETECTION = "SERVICE_DETECTION"


class TaskStatus(Enum, str):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
