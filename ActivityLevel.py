from datetime import datetime, timedelta, timezone
from enum import Enum

class ActivityLevel(Enum):
    Active = datetime.now(timezone.utc) - timedelta(days=90) #three months
    someActivity = datetime.now(timezone.utc) - timedelta(days=180) #six months
    Inactive = datetime.now(timezone.utc) - timedelta(days=365) #one year