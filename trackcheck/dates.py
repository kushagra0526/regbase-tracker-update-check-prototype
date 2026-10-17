"""Dates and number words as they appear in tracker prose."""
import datetime as dt
import re

MONTHS = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8,
          "september": 9, "october": 10, "november": 11, "december": 12,
          "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10,
          "nov": 11, "dec": 12}
_M = "|".join(sorted(MONTHS, key=len, reverse=True))
DATE_RE = re.compile(rf"\b({_M})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?\b(?:,?\s+(\d{{4}}))?", re.I)
ISO_RE = re.compile(r"\b(20\d\d)-(\d\d)-(\d\d)\b")

WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
         "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100}
NUM = r"(\d+|(?:(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)[- ])?(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)|a hundred(?: and twenty)?)"


def number(s):
    s = s.lower().strip()
    if s.isdigit():
        return int(s)
    if s.startswith("a hundred"):
        return 100 + (20 if "twenty" in s else 0)
    total = 0
    for w in re.split(r"[- ]", s):
        total += WORDS.get(w, 0)
    return total


def find_dates(text, year):
    """[(start, end, date)]; a date with no year takes `year` (the page's or the sentence's)."""
    out = []
    for m in DATE_RE.finditer(text):
        mon = MONTHS[m.group(1).lower()]
        y = int(m.group(3)) if m.group(3) else year
        try:
            out.append((m.start(), m.end(), dt.date(y, mon, int(m.group(2)))))
        except ValueError:
            pass
    for m in ISO_RE.finditer(text):
        try:
            out.append((m.start(), m.end(), dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))))
        except ValueError:
            pass
    return sorted(out)


def add(d, n, unit):
    unit = unit.lower().rstrip("s")
    if unit == "day":
        return d + dt.timedelta(days=n)
    if unit == "week":
        return d + dt.timedelta(weeks=n)
    if unit == "month":
        m = d.month - 1 + n
        y, m = d.year + m // 12, m % 12 + 1
        for day in (d.day, 30, 29, 28):
            try:
                return dt.date(y, m, day)
            except ValueError:
                continue
    raise ValueError(unit)


def fmt(d):
    return f"{d:%B} {d.day}, {d.year}"


def short(d):
    return f"{d:%b} {d.day}"
