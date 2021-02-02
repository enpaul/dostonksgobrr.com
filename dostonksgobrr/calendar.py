import datetime
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union


class Window(NamedTuple):
    start: datetime.time
    duration: datetime.timedelta


class Holiday(NamedTuple):
    date: datetime.date
    hours: Optional[Window] = None


class MarketCalendar:  # pylint: disable=too-many-instance-attributes

    WEEKEND_DAYS: Tuple[int, ...] = (5, 6)

    def __init__(  # pylint: disable=too-many-arguments
        self,
        holidays: Sequence[Holiday],
        weekday_window: Window,
        weekday_window_dst: Window,
        weekend_window_dst: Optional[Window] = None,
        weekend_window: Optional[Window] = None,
        dst_start: Optional[datetime.datetime] = None,
        dst_end: Optional[datetime.datetime] = None,
    ):
        self._holidays: Dict[datetime.date, Window] = {
            item.date: item.hours for item in holidays if item.hours is not None
        }
        self._exclude: List[datetime.date] = [
            item.date for item in holidays if item.hours is None
        ]
        self._weekday_window = weekday_window
        self._weekday_window_dst = weekday_window_dst
        self._weekend_window = weekend_window
        self._weekend_window_dst = weekend_window_dst

        if (dst_start and not dst_end) or (dst_end and not dst_start):
            raise ValueError(
                "Both a DST start and end time must be provided if DST is enabled"
            )

        self._dst_start = dst_start
        self._dst_end = dst_start

    def is_weekend(self, ref: Union[datetime.datetime, datetime.date]) -> bool:
        return ref.weekday() in self.WEEKEND_DAYS

    def is_dst(self, ref: Union[datetime.datetime, datetime.date]) -> bool:
        if self._dst_start and self._dst_end:
            return self._dst_start < ref < self._dst_end
        return False

    def is_market_open(self, ref: datetime.datetime) -> bool:
        window = self._get_window(ref)

        if window is None:
            return False

        start = datetime.datetime.combine(ref.date(), window.start)
        end = start + window.duration
        return start < ref < end

    def next_bell(self, ref: datetime.datetime) -> datetime.datetime:
        marker = ref
        window = self._get_window(marker)
        while window is None:
            marker += datetime.timedelta(days=1)
            window = self._get_window(marker)

        if marker.date() != ref.date():
            bell = datetime.datetime.combine(marker.date(), window.start)
        elif self.is_market_open(ref):
            bell = datetime.datetime.combine(ref.date(), window.start) + window.duration
        elif ref.time() < window.start:
            bell = datetime.datetime.combine(ref.date(), window.start)
        else:
            marker += datetime.timedelta(days=1)
            window = self._get_window(marker)
            while window is None:
                marker += datetime.timedelta(days=1)
                window = self._get_window(marker)
            bell = datetime.datetime.combine(marker.date(), window.start)

        return bell

    def _get_window(self, ref: datetime.datetime) -> Optional[Window]:
        if ref.date() in self._exclude:
            return None
        if ref.date() in self._holidays:
            return self._holidays[ref]
        if self.is_weekend(ref):
            return (
                self._weekend_window_dst if self.is_dst(ref) else self._weekend_window
            )
        return self._weekday_window if self.is_dst(ref) else self._weekday_window


CALENDARS: Dict[int, MarketCalendar] = {
    2021: MarketCalendar(
        weekday_window=Window(
            start=datetime.time(hour=14, minute=30),
            duration=datetime.timedelta(hours=6, minutes=30),
        ),
        weekday_window_dst=Window(
            start=datetime.time(hour=13, minute=30),
            duration=datetime.timedelta(hours=6, minutes=30),
        ),
        holidays=[
            Holiday(date=datetime.date(year=2021, month=1, day=1), hours=None),
            Holiday(date=datetime.date(year=2021, month=1, day=18), hours=None),
            Holiday(date=datetime.date(year=2021, month=2, day=15), hours=None),
            Holiday(date=datetime.date(year=2021, month=4, day=2), hours=None),
            Holiday(date=datetime.date(year=2021, month=5, day=31), hours=None),
            Holiday(date=datetime.date(year=2021, month=6, day=5), hours=None),
            Holiday(date=datetime.date(year=2021, month=9, day=6), hours=None),
            Holiday(date=datetime.date(year=2021, month=11, day=25), hours=None),
            Holiday(
                date=datetime.date(year=2021, month=11, day=26),
                hours=Window(
                    start=datetime.time(hour=14, minute=30),
                    duration=datetime.timedelta(hours=3, minutes=30),
                ),
            ),
            Holiday(date=datetime.date(year=2021, month=12, day=24), hours=None),
        ],
        dst_start=datetime.datetime(year=2021, month=3, day=14, hour=7, minute=0),
        dst_end=datetime.datetime(year=2021, month=11, day=7, hour=6, minute=0),
    )
}


def is_market_open() -> bool:
    now = datetime.datetime.utcnow()
    return CALENDARS[now.year].is_market_open(now)


def next_bell() -> datetime.datetime:
    now = datetime.datetime.utcnow()
    return CALENDARS[now.year].next_bell(now)
