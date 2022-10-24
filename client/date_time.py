import datetime, calendar
from mixins import *

__author__ = "@prmpsmart"

DAYS_ABBRS, DAYS_NAMES, MONTHS_ABBRS, MONTHS_NAMES = (
    ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    calendar.month_abbr[:],
    calendar.month_name[:],
)
WEEKS = ["Week %d" % a for a in range(1, 6)]


_DAYS_IN_MONTH = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

_DAYS_BEFORE_MONTH = [-1]  # -1 is a placeholder for indexing purposes.
dbm = 0
for dim in _DAYS_IN_MONTH[1:]:
    _DAYS_BEFORE_MONTH.append(dbm)
    dbm += dim
del dbm, dim


def _is_leap(year):
    "year -> 1 if leap year, else 0."
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _days_before_year(year):
    "year -> number of days before January 1st of year."
    y = year - 1
    return y * 365 + y // 4 - y // 100 + y // 400


def _days_in_month(year, month):
    "year, month -> number of days in that month in that year."
    assert 1 <= month <= 12, month
    if month == 2 and _is_leap(year):
        return 29
    return _DAYS_IN_MONTH[month]


def _days_before_month(year, month):
    "year, month -> number of days in year preceding first day of month."
    assert 1 <= month <= 12, "month must be in 1..12"
    return _DAYS_BEFORE_MONTH[month] + (month > 2 and _is_leap(year))


def _ymd2ord(year, month, day):
    "year, month, day -> ordinal, considering 01-Jan-0001 as day 1."
    assert 1 <= month <= 12, "month must be in 1..12"
    dim = _days_in_month(year, month)
    assert 1 <= day <= dim, "day must be in 1..%d" % dim
    return _days_before_year(year) + _days_before_month(year, month) + day


_DI400Y = _days_before_year(401)  # number of days in 400 years
_DI100Y = _days_before_year(101)  #    "    "   "   " 100   "
_DI4Y = _days_before_year(5)  #    "    "   "   "   4   "

# A 4-year cycle has an extra leap day over what we'd get from pasting
# together 4 single years.
assert _DI4Y == 4 * 365 + 1

# Similarly, a 400-year cycle has an extra leap day over what we'd get from
# pasting together 4 100-year cycles.
assert _DI400Y == 4 * _DI100Y + 1

# OTOH, a 100-year cycle has one fewer leap day than we'd get from
# pasting together 25 4-year cycles.
assert _DI100Y == 25 * _DI4Y - 1


def _ord2ymd(n):
    "ordinal -> (year, month, day), considering 01-Jan-0001 as day 1."

    # n is a 1-based index, starting at 1-Jan-1.  The pattern of leap years
    # repeats exactly every 400 years.  The basic strategy is to find the
    # closest 400-year boundary at or before n, then work with the offset
    # from that boundary to n.  Life is much clearer if we subtract 1 from
    # n first -- then the values of n at 400-year boundaries are exactly
    # those divisible by _DI400Y:
    #
    #     D  M   Y            n              n-1
    #     -- --- ----        ----------     ----------------
    #     31 Dec -400        -_DI400Y       -_DI400Y -1
    #      1 Jan -399         -_DI400Y +1   -_DI400Y      400-year boundary
    #     ...
    #     30 Dec  000        -1             -2
    #     31 Dec  000         0             -1
    #      1 Jan  001         1              0            400-year boundary
    #      2 Jan  001         2              1
    #      3 Jan  001         3              2
    #     ...
    #     31 Dec  400         _DI400Y        _DI400Y -1
    #      1 Jan  401         _DI400Y +1     _DI400Y      400-year boundary
    n -= 1
    n400, n = divmod(n, _DI400Y)
    year = n400 * 400 + 1  # ..., -399, 1, 401, ...

    # Now n is the (non-negative) offset, in days, from January 1 of year, to
    # the desired date.  Now compute how many 100-year cycles precede n.
    # Note that it's possible for n100 to equal 4!  In that case 4 full
    # 100-year cycles precede the desired day, which implies the desired
    # day is December 31 at the end of a 400-year cycle.
    n100, n = divmod(n, _DI100Y)

    # Now compute how many 4-year cycles precede it.
    n4, n = divmod(n, _DI4Y)

    # And now how many single years.  Again n1 can be 4, and again meaning
    # that the desired day is December 31 at the end of the 4-year cycle.
    n1, n = divmod(n, 365)

    year += n100 * 100 + n4 * 4 + n1
    if n1 == 4 or n100 == 4:
        assert n == 0
        return year - 1, 12, 31

    # Now the year is correct, and n is the offset from January 1.  We find
    # the month via an estimate that's either exact or one too large.
    leapyear = n1 == 3 and (n4 != 24 or n100 == 3)
    assert leapyear == _is_leap(year)
    month = (n + 50) >> 5
    preceding = _DAYS_BEFORE_MONTH[month] + (month > 2 and leapyear)
    if preceding > n:  # estimate is too large
        month -= 1
        preceding -= _DAYS_IN_MONTH[month] + (month == 2 and leapyear)
    n -= preceding
    assert 0 <= n < _days_in_month(year, month)

    # Now the year and month are correct, and n is the offset from the
    # start of that month:  we're done!
    return year, month, n + 1


class OldCompareByDate:
    def __lt__(self, other):
        if other == None:
            return False
        return self.date < other.date

    def __le__(self, other):
        if other == None:
            return False
        return self.date <= other.date

    def __eq__(self, other):
        if other == None:
            return False
        return self.date is other.date

    def __ne__(self, other):
        if other == None:
            return True
        return self.date != other.date

    def __gt__(self, other):
        if other == None:
            return True
        return self.date > other.date

    def __ge__(self, other):
        if other == None:
            return True
        return self.date >= other.date


class CompareByDate:
    def __lt__(self, other):
        if other == None:
            return False
        return self.date.ymdToOrd < other.date.ymdToOrd

    def __le__(self, other):
        if other == None:
            return False
        return self.date.ymdToOrd <= other.date.ymdToOrd

    def __eq__(self, other):
        if other == None:
            return False
        return self.date.ymdToOrd is other.date.ymdToOrd

    def __ne__(self, other):
        if other == None:
            return True
        return self.date.ymdToOrd != other.date.ymdToOrd

    def __gt__(self, other):
        if other == None:
            return True
        return self.date.ymdToOrd > other.date.ymdToOrd

    def __ge__(self, other):
        if other == None:
            return True
        return self.date.ymdToOrd >= other.date.ymdToOrd


class CompareByWeek:
    def __lt__(self, other):
        if other == None:
            return False
        return self.date.week_month_year_tuple < other.date.week_month_year_tuple

    def __le__(self, other):
        if other == None:
            return False
        return self.date.week_month_year_tuple <= other.date.week_month_year_tuple

    def __eq__(self, other):
        if other == None:
            return False
        return self.date.week_month_year_tuple == other.date.week_month_year_tuple

    def __ne__(self, other):
        if other == None:
            return True
        return self.date.week_month_year_tuple != other.date.week_month_year_tuple

    def __gt__(self, other):
        if other == None:
            return True
        return self.date.week_month_year_tuple > other.date.week_month_year_tuple

    def __ge__(self, other):
        if other == None:
            return True
        return self.date.week_month_year_tuple >= other.date.week_month_year_tuple


class CompareByMonth:
    def __lt__(self, other):
        if other == None:
            return False
        return self.date.month_year_tuple < other.date.month_year_tuple

    def __le__(self, other):
        if other == None:
            return False
        return self.date.month_year_tuple <= other.date.month_year_tuple

    def __eq__(self, other):
        if other == None:
            return False
        return self.date.month_year_tuple == other.date.month_year_tuple

    def __ne__(self, other):
        if other == None:
            return True
        return self.date.month_year_tuple != other.date.month_year_tuple

    def __gt__(self, other):
        if other == None:
            return True
        return self.date.month_year_tuple > other.date.month_year_tuple

    def __ge__(self, other):
        if other == None:
            return True
        return self.date.month_year_tuple >= other.date.month_year_tuple


class CompareByYear:
    def __lt__(self, other):
        if other == None:
            return False
        return self.date.year < other.date.year

    def __le__(self, other):
        if other == None:
            return False
        return self.date.year <= other.date.year

    def __eq__(self, other):
        if other == None:
            return False
        return self.date.year == other.date.year

    def __ne__(self, other):
        if other == None:
            return True
        return self.date.year != other.date.year

    def __gt__(self, other):
        if other == None:
            return True
        return self.date.year > other.date.year

    def __ge__(self, other):
        if other == None:
            return True
        return self.date.year >= other.date.year


class DateTime(datetime.datetime, ClassMixins):
    date_fmt = "%d/%m/%Y"  # default date format, subclass DateTime and set date_fmt to your own format

    daysAbbr, days_names, months_abbrs, months_names = (
        DAYS_ABBRS,
        DAYS_NAMES,
        MONTHS_ABBRS,
        MONTHS_NAMES,
    )

    timedelta = datetime.timedelta

    # the __add__ and __sub__ are implementaions are purely by PRMPSmart@gmail.com

    def __lt__(self, other):
        if other == None:
            return False
        return super().__lt__(other) or self.date == other.date

    def __le__(self, other):
        if other == None:
            return False
        return super().__le__(other) or self.date == other.date

    def __eq__(self, other):
        if other == None:
            return False
        return super().__eq__(other) or self.date == other.date

    def __ne__(self, other):
        if other == None:
            return True
        return super().__ne__(other) or self.date == other.date

    def __gt__(self, other):
        if other == None:
            return True
        return super().__gt__(other) or self.date == other.date

    def __ge__(self, other):
        if other == None:
            return True
        return super().__ge__(other) or self.date == other.date

    def __getitem__(self, item):
        if item == slice(None, None, None):
            return self
        return ClassMixins.__getitem__(self, item)

    def __add__(self, add_month):
        if isinstance(add_month, self.timedelta):
            return self.create_date_time(obj=super().__add__(add_month))

        elif isinstance(add_month, int):
            months = self.month + add_month
            div, mod = divmod(months, 12)
            if (div == 0) or (months == 12):
                # it means that the months falls within the current self.year
                return self.create_date_time(self.year, months, self.day)
            elif div > 0:
                # it means that the new_month falls within the upcoming years
                if not mod:
                    # it means self.month = 12 and sub_month *12
                    mod = 12
                    # the resulting month is 12
                    div -= 1
                    # since self.month = 12 and sub_month *12 therefore div is having an additional self.month 12 in it
                return self.create_date_time(self.year + div, mod, self.day)

    def __sub__(self, sub_month):
        if isinstance(sub_month, self.timedelta):
            return self.create_date_time(obj=super().__sub__(sub_month))

        elif isinstance(sub_month, self.__class__):
            return self.diffInMonth(sub_month)
        elif isinstance(sub_month, int):

            if sub_month < self.month:
                # since sub_month is lower than self.month, the new month is within that same year
                return self.create_date_time(
                    self.year, self.month - sub_month, self.day
                )

            elif sub_month == self.month:
                # since sub_month is equal to self.month, the new month is automatically last month of last year
                return self.create_date_time(self.year - 1, 12, self.day)

            # since the above conditions are not met, it means that the sub_month is actually more than self.month which means that the new month is actually in the recent years if not the last one.
            else:
                # since 12 months == 1 year; recent years in the sub_month = sub_month // 12, and the remaining months is sub_month % 12.
                div, mod = divmod(sub_month, 12)

                if div == 0:
                    # the sub_month > self.month but < 12
                    rem = sub_month - self.month
                    #  first minus its exact month from itself, then minus the remaining months
                    first = self - self.month
                    second = first - rem
                    return second

                else:
                    # therefore, subtract the recent years from the current year, creating a new DateTime with everything else in place except the year
                    # the sub_month is more than 12
                    year = self.create_date_time(self.year - div, self.month, self.day)
                    # the remaining months will now fall into the categories of (sub_month < self.month) and ( sub_month == self.month).
                    # it will now look as if it's a loop, the remaining months will now be subtracted from the new year-DateTime, the process will now fall into the first two conditions in the new year-DateTime
                    return year - mod

    def __str__(self):
        return repr(self)

    # def __str__(self): return self.strftime(self.date_fmt)

    def get(self, name, default=""):
        return self.get_from_self(name, default)

    @property
    def date(self):
        return self.strftime(self.date_fmt)

    @property
    def strDate(self):
        return self.date

    @property
    def total_days(self):  # also equal to _days_in_month
        lis = [1, 3, 5, 7, 8, 10, 12]
        if self.month == 2:
            return 28 + self.is_leap
        elif self.month in lis:
            return 31
        else:
            return 30

    @classmethod
    def getDay_num(cls, day):
        error = Exception(
            "day must be among {} or {}".format(cls.days_abbrs, cls.days_names)
        )
        if isinstance(day, str):
            if day in cls.days_abbrs:
                day_num = cls.days_abbrs.index(day) + 1
            elif day in cls.days_names:
                day_num = cls.days_names.index(day) + 1
            else:
                raise error
            return day_num
        else:
            raise error

    @classmethod
    def getDay_name(cls, day, abbr=False):
        range_ = list(range(1, 31))
        error = Exception("day must be among {}".format(range_))
        if isinstance(day, int):
            if day in range_:
                if abbr:
                    day_name = cls.days_abbrs[day - 1]
                else:
                    day_name = cls.days_names[day - 1]
            else:
                raise error
            return day_name
        else:
            raise error

    @classmethod
    def check_date_time(cls, date, dontRaise=False):
        date = cls.getDMYFromString(date)
        if not isinstance(date, DateTime):
            if dontRaise:
                return False
            raise Exception("Date must be an instance of DateTime")
        return date

    @classmethod
    def now(cls):
        return cls.create_date_time(obj=super().now())

    @classmethod
    def getMonthNum(cls, month):
        error = Exception(
            "month must be among {} or {}".format(cls.months_abbrs), cls.months_names
        )
        if isinstance(month, str):
            if month in cls.months_abbrs:
                monthNum = cls.months_abbrs.index(month)
            elif month in cls.months_names:
                monthNum = cls.months_names.index(month)
            else:
                raise error
            return monthNum
        else:
            raise error

    @classmethod
    def getMonthName(cls, month, abbr=False):
        range_ = list(range(1, 12))
        error = Exception("month must be among {}".format(range_))
        if isinstance(month, int):
            if month in range_:
                if abbr:
                    month_name = cls.months_abbrs[month - 1]
                else:
                    month_name = cls.months_names[month - 1]
            else:
                raise error
            return month_name
        else:
            raise error

    @classmethod
    def create_date_time(
        cls,
        year=None,
        month=1,
        day=1,
        auto=False,
        obj=None,
        week=None,
        hour=0,
        minute=0,
        second=0,
        string="",
    ):
        if string:
            return cls.getDMYFromString(string)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            year = obj.year
            month = obj.month
            day = obj.day
            try:
                hour = obj.hour
                minute = obj.minute
                second = obj.second
            except:
                pass

        elif auto:
            return cls.now()

        elif week:
            assert month and year, "Month and Year are also required."
            weeks = cls.month_week_days(year, month)
            return weeks[week - 1][0]

        if isinstance(month, str):
            month = cls.getMonthNum(month)

        if isinstance(day, str):
            day = cls.getDay_num(month)

        dummy = cls(year, month, 1).total_days
        if dummy < day:
            day = dummy

        return cls(
            year=year, month=month, day=day, hour=hour, minute=minute, second=second
        )

    @property
    def day_num(self):
        return self.day

    @property
    def day_name(self):
        return self.strftime("%A")

    @property
    def day_nameAbbr(self):
        return self.strftime("%a")

    @property
    def month_name(self):
        return self.strftime("%B")

    @property
    def month_name_abbr(self):
        return self.strftime("%b")

    @property
    def month_year(self):
        return "{}-{}".format(self.month_name, self.year)

    @property
    def week_month_year(self):
        return "{}, {}-{}".format(self.week_name, self.month_name, self.year)

    @property
    def month_year_tuple(self):
        return (self.year, self.month)

    @property
    def week_month_year_tuple(self):
        return (self.year, self.month, self.week)

    @property
    def day_month_year(self):
        return "{}-{}".format(self.day, self.month_year)

    @property
    def iso_week_day(self):
        d = (int(self.isoweekday()) + 1) % 7
        if d == 0:
            return 7
        return d

    @property
    def week_day(self):
        return (int(self.weekday()) + 1) % 7

    @property
    def week_in_year(self):
        return int(self.isocalendar()[1])

    def is_same_date(self, date: "DateTime"):
        self.check_date_time(date)
        return self.date == date.date

    def is_same_day(self, date: "DateTime"):
        return self.day == date.day

    def is_same_day_name(self, date: "DateTime"):
        return self.day_name == date.day_name

    def is_same_year(self, date: "DateTime"):
        return self.year == date.year

    def is_same_month(self, date: "DateTime"):
        return self.month == date.month

    def is_same_week(self, date: "DateTime"):
        return self.week == date.week

    def is_same_month_year(self, date: "DateTime"):
        return self.month_year_tuple == date.month_year_tuple

    def is_same_week_month_year(self, date: "DateTime"):
        return self.week_month_year_tuple == date.week_month_year_tuple

    @classmethod
    def _month_week_days(cls, year=None, month=None, monday=False, dateObj=None):
        "getting all the weeks in a month"
        if dateObj:
            year, month = dateObj.year, dateObj.month

        year = int(year)
        if isinstance(month, str):
            month = MONTHS_NAMES[:].index(month)

        ca = calendar.Calendar(0 if monday else 6)

        month_wks = ca.monthdatescalendar(year, month)

        weeks = []

        for week in month_wks:
            weeks_days = []

            for day in week:
                Day = cls.create_date_time(obj=day)
                weeks_days.append(Day)

            weeks.append(weeks_days)

        return weeks

    def month_week_days(self, **kwargs):
        return self._month_week_days(dateObj=self, **kwargs)

    @classmethod
    def get_month_year_of_date_times(cls, dts):
        return [dt.month_year for dt in dts]

    @classmethod
    def month_year_of_month_week_days(cls, **kwargs):
        weeks = cls.month_week_days(**kwargs)
        weeks_month_year = [cls.get_month_year_of_date_times(week) for week in weeks]
        return weeks_month_year

    @property
    def weeks_dates(self):
        "returns all the days in a month in a list of weeks"
        return self.month_week_days()

    @property
    def week_dates(self) -> List["DateTime"]:
        "returns all the days in a month in a list of weeks"
        return self.weeks_dates[self.week - 1]

    @property
    def one_day_in_weeks_in_month(self) -> List["DateTime"]:
        "returns a list of containing a day from each weeks in the month"
        weeks_dates = self.weeks_dates
        one = weeks_dates[0]

        dates = []

        for week in weeks_dates:
            if week == one:
                dates.append(week[-1])
            else:
                dates.append(week[0])
        dates.sort
        return dates

    @property
    def month_dates(self) -> List["DateTime"]:
        "returns all the days that makes up the 4 or 5 weeks in a list"
        days = []
        for week in self.weeks_dates:
            for day in week:
                days.append(day)
        return days

    @property
    def month_only_dates(self) -> List["DateTime"]:
        "returns all the days in a month in a list"
        dates = self.month_dates
        days = [day for day in dates if self.is_same_month_year(day)]
        return days

    @property
    def all_same_days_dates(self) -> List[List["DateTime"]]:
        "returns a list of list each containing the days of the same name"
        all_dates = self.month_only_dates
        leng = range(len(self.days_names))

        sames = [[] for _ in leng]

        for date in all_dates:
            for day in leng:
                day_name = self.days_names[day]
                if date.day_name == day_name:
                    sames[day].append(date)

        return sames

    @property
    def same_days_dates(self) -> List["DateTime"]:
        "returns a list of each day from each list returned from all_same_days_dates"
        all_dates = self.all_same_days_dates
        sames = [a[0] for a in all_dates]
        sames.sort(key=lambda date: date.week_day)

        return sames

    @property
    def same_day_names_dates(self) -> List["DateTime"]:
        "returns a list of days having the same day_name as self"
        dates = self.all_same_days_dates[self.week_day]
        dates.sort()
        return dates

    @property
    def same_week_date_in_year(self):
        same_weeks = []
        weeks = self.weeks_in_year

        for index, week in enumerate(weeks):
            day = week[3]
            if not index:
                day = week[-1]
            elif index == len(weeks) - 1:
                day = week[0]
            if day.week == self.week:
                if day not in same_weeks:
                    same_weeks.append(day)

        return same_weeks

    @property
    def months_in_year(self) -> List["DateTime"]:
        "returns the months in the year of this current DateTime object"
        currentMonth = self.month
        months = range(1, 13)
        monthsDates = []

        for month in months:
            if month < currentMonth:
                monthsDates.append(self - month)
            elif month == currentMonth:
                monthsDates.append(self)
            elif month > currentMonth:
                diff = month - currentMonth
                monthsDates.append(self + diff)
        monthsDates.sort()
        return monthsDates

    @property
    def days_in_year(self) -> List["DateTime"]:
        months = self.months_in_year
        days = []
        for month in months:
            days.extend(month.month_only_dates)
        return days

    def _weeks_in_year(self, monday=False) -> List["DateTime"]:
        months = self.months_in_year
        weeks = []

        for month in months:
            weeks += month.month_week_days(monday=monday)

        return weeks

    @property
    def weeks_in_year(self):
        return self._weeks_in_year()

    @property
    def weeks_in_year1(self):
        return self._weeks_in_year(1)

    @property
    def one_day_in_weeks_in_year(self) -> List["DateTime"]:
        weeks = []
        _weeks = self.weeks_in_year
        last = len(_weeks)
        for index, week in enumerate(_weeks):
            _week = week[3]
            if not index:
                _week = week[-1]
            elif index == last - 1:
                _week = week[0]

            weeks.append(_week)

        return weeks

    @property
    def one_day_in_weeks_in_year(self) -> List["DateTime"]:
        weeks = {}
        _weeks = self.weeks_in_year
        last = len(_weeks)
        for index, week in enumerate(_weeks):
            _week = week[3]
            if not index:
                _week = week[-1]
            elif index == last - 1:
                _week = week[0]

            weeks[week.week_month_year_tuple] = _week

        weeks = list(weeks.values())
        weeks.sort()

        return weeks

    @property
    def week(self) -> int:
        "returns the week number that this date is in its month"
        weeks = self.weeks_dates
        for wk in weeks:
            _wk = [w.date for w in wk]
            if self.date in _wk:
                return weeks.index(wk) + 1
        return 0

    @property
    def week_name(self) -> str:
        return "Week {}".format(self.week)

    @classmethod
    def getDMYFromString(cls, date) -> "DateTime":
        if date:
            if isinstance(date, (str, bytes)):
                try:
                    day, month, year = cls.getNumsInStrAsList(None, date, [2], 1)
                except Exception as e:
                    return

                day, month, year = int(day), int(month), int(year)
                dt = cls(year, month, day)
                return dt
            elif isinstance(date, cls):
                return date

    def diffInMonth(self, date) -> int:
        "returns the different in the current month and the given month"
        self.check_date_time(date)
        if self.month_year_tuple == date.month_year_tuple:
            return 0
        elif self > date:
            max_date, min_date = self, date
        elif self < date:
            max_date, min_date = date, self

        year_diff = max_date.year - min_date.year
        month_from_year_diff = year_diff * 12
        month_diff = max_date.month - min_date.month
        months_diff = month_from_year_diff + month_diff

        return months_diff

    @classmethod
    def _is_leap(cls, year) -> bool:
        return _is_leap(year)

    @property
    def is_leap(self):
        return self._is_leap(self.year)

    @classmethod
    def _days_before_year(cls, year) -> int:
        return _days_before_year(year)

    @property
    def days_before_year(self):
        return self._days_before_year(self.year)

    @classmethod
    def _days_in_month(cls, year, month):
        return _days_in_month(year, month)

    @property
    def days_in_month(self):
        return self._days_in_month(self.year, self.month)

    @classmethod
    def _days_before_month(cls, year, month) -> int:
        return _days_before_month(year, month)

    @property
    def days_before_month(self):
        return self._days_before_month(self.year, self.month)

    @classmethod
    def _ymd2ord(cls, year, month, day) -> int:
        return _ymd2ord(year, month, day)

    @property
    def ymd_to_ord(self):
        return self._ymd2ord(self.year, self.month, self.day)

    @classmethod
    def ord2ymd(cls, ord_):
        return _ord2ymd(ord_)

    def add_times(self, **kwargs):
        return self + self.timedelta(**kwargs)

    def add_months(self, months):
        return self + months
