from __future__ import annotations

import textwrap
import time
import typing as t


class SectionTimer:
    """
    SectionTimer is a utility for profiling developer-defined subsections of code.  It
    is morally equivalent to a manual process of adding timing events to a list.

    Example usage:

        >>> timer = SectionTimer()
        >>> timer.section_start("sectionA")
        >>> timer.section_start("sectionB")
        >>> timer.section_start("sectionC")
        >>> timer.section_end()
        >>> timer.times()
        (('sectionA", 1.374), ('sectionB', 1.181), ('sectionC', 2.192))

    Note: Timing events use `time.monotonic()`, so values are in seconds.
    """

    def __init__(self) -> None:
        self._timed_sections: list[tuple[str, float]] = []
        self._current_section_name = ""
        self._current_start_time = 0.0

    def section_start(self, section_title: str) -> None:
        """
        Begin timing a new section of code, named `section_title`.  If a previous
        section is currently active, that section is ended first.
        """
        self.section_end()
        self._current_section_name = section_title
        self._current_start_time = time.monotonic()

    @property
    def length(self) -> int:
        return len(self._timed_sections)

    @property
    def is_active(self) -> bool:
        return self._current_start_time > 0

    def section_end(self) -> None:
        """
        Stop timing a section of code, and append the section time value to the
        internal list.  If no section is active, then do nothing.
        """
        if self.is_active:
            duration = time.monotonic() - self._current_start_time
            self._timed_sections.append((self._current_section_name, duration))
            self._current_section_name = ""
            self._current_start_time = 0

    def times(self, ndigits: int = 3) -> tuple[tuple[str, float], ...]:
        """
        Return a tuple of (section_title, section_duration) timings.  The
        section_duration value will be rounded to `ndigits`.
        """
        return tuple((sec, round(dur, ndigits)) for sec, dur in self.times_raw)

    @property
    def times_raw(self) -> t.Iterable[tuple[str, float]]:
        """
        Return an iterable of (section_title, section_duration) tuples of the current
        section timings.  The timings are not rounded as with .times()
        """
        return ((sec, dur) for sec, dur in self._timed_sections)

    def __repr__(self) -> str:
        sec_names = "; ".join(n for n, _ in self._timed_sections)
        sec_names = textwrap.shorten(sec_names, width=30, placeholder="...")
        klassname = self.__class__.__name__
        is_active = self.is_active and ", *" or ""
        return f"<{klassname} ({self.length}{is_active}) [{sec_names}]>"
