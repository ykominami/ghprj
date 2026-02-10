from datetime import datetime, timedelta, timezone


class Timex:
    JST = timezone(timedelta(hours=9))

    @classmethod
    def get_now(cls) -> str:
        return datetime.now(cls.JST).isoformat()
