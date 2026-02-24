import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

FILE = Path("dev_time.json") 

def dev_get_extra_seconds():
    if not FILE.exists():
        return 0
    return json.loads(FILE.read_text()).get("seconds", 0)

def dev_add_seconds(seconds: int):
    current = dev_get_extra_seconds()
    FILE.write_text(json.dumps({"seconds": current + seconds}))

def dev_reset_extra_seconds():
    if not FILE.exists():
        with open(FILE, "w") as f:
            f.write("")
    FILE.write_text(json.dumps({"seconds": 0}))

def utcnow() -> datetime:
    dev_extra_time_seconds = dev_get_extra_seconds()
    return datetime.now(timezone.utc) + timedelta(seconds=dev_extra_time_seconds)
