import random
from unittest import mock

from funcx_common.utils.section_timer import SectionTimer


def test_happy_path(randomstring):
    section_titles = [randomstring() for _ in range(5)]
    timer = SectionTimer()
    assert not list(timer.times_raw), "no events; should be no data"
    timer.section_start(section_titles[0])
    assert not list(timer.times_raw), "no section ended; should be no data"

    timer = SectionTimer()
    for sec_title in section_titles:
        timer.section_start(sec_title)
    assert timer.is_active
    assert timer.length == len(section_titles) - 1

    timer.section_end()
    assert not timer.is_active
    assert timer.length == len(section_titles)

    for expected_title, (found_title, dur) in zip(section_titles, timer.times_raw):
        assert expected_title == found_title, "expecting to match input order"
        assert dur > 0


def test_data_rounding():
    time_vals = (i / 10 + random.random() / 10 for i in range(6))
    t_beg = next(time_vals)

    with mock.patch("funcx_common.utils.section_timer.time") as time_mock:
        time_mock.monotonic.return_value = t_beg

        timer = SectionTimer()
        expected = []
        for i, t_end in enumerate(time_vals, start=1):
            sec_title = f"Sec_{i}"
            timer.section_start(sec_title)
            time_mock.monotonic.return_value = t_end
            expected_val = t_end - t_beg
            t_beg = t_end
            expected.append((sec_title, round(expected_val, ndigits=3)))
        timer.section_end()
        assert tuple(expected) == timer.times()


def test_repr(randomstring):
    section_titles = [randomstring() for _ in range(5)]
    timer = SectionTimer()
    for sec_title in section_titles:
        timer.section_start(sec_title)

    exp = f"({len(section_titles) -1}, *)"
    assert timer.is_active and exp in repr(timer)
    assert timer.length == len(section_titles) - 1
    timer.section_end()

    exp = f"({len(section_titles)})"
    assert timer.is_active is False and exp in repr(timer)
    assert timer.__class__.__name__ in repr(timer)
    assert section_titles[0] in repr(timer)
    assert "..." in repr(timer), "expecting ellipsized section titles"
    assert section_titles[-1] not in repr(timer), "don't overwhelm repr()"
