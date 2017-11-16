import unittest
from nut import *
from datetime import datetime, timedelta
import shutil, tempfile
from os import path


test_csv = "\n".join((
    "Person Name,Person ID,Date,Start,End",
    "AAA AAA,1,1.1.1,00:00,01:00",
    "AAA AAA,1,1.1.1,01:00,02:00",
    "AAA AAA,1,1.1.1,02:00,03:00",
    "AAA AAA,1,1.1.1,03:00,04:00",
    "AAA AAA,1,1.1.1,04:00,05:00",
    "AAA AAA,1,1.1.1,05:00,06:00",
    "AAA AAA,1,1.1.1,06:00,07:00",
    "AAA AAA,1,1.1.1,07:00,08:00",
    "AAA AAA,1,1.1.1,08:00,09:00",
    "AAA AAA,1,1.1.1,09:00,10:00",
    "AAA AAA,1,1.1.1,10:00,11:00",
    "AAA AAA,1,1.1.1,11:00,12:00",
    "BBB BBB,2,1.1.1,00:00,23:00",
    "BBB BBB,2,2.1.1,00:00,23:00",
    "BBB BBB,2,3.1.1,00:00,23:00",
    "BBB BBB,2,4.1.1,00:00,23:00",
    "BBB BBB,2,5.1.1,00:00,23:00"))


def make_interval(begin, end):
    b = datetime(1,1,1,*begin)
    e = datetime(1,1,1,*end)
    if (e < b):
        e += timedelta(days = 1)
    return TimeInterval(b, e)


class TestNut(unittest.TestCase):

    def setUp(self):
        LOGGER.setLevel('CRITICAL')
        self.tempdir = tempfile.mkdtemp()
        self.tempfile = path.join(self.tempdir, 'test.csv')
        with open(self.tempfile, 'w') as f:
            f.write(test_csv)

    def tearDown(self):
        shutil.rmtree(self.tempdir)


    def test_interval(self):
        interval = make_interval((1,30),(0,0))
        self.assertEqual(interval.hours(), 22.5)
        self.assertEqual(len(interval.days()), 2)

        interval = make_interval((1,30),(2,30))
        self.assertEqual(interval.hours(), 1.0)
        self.assertEqual(len(interval.days()), 1)

    def test_overtime(self):
        def assertRange(b,e,func):
            for h in range(b,e+1):
                self.assertEqual(overtime(h), func(h))
        assertRange( 0,  8, lambda x: 0)
        assertRange( 9, 10, lambda x: (x- 8) * 0.25)
        assertRange(11, 12, lambda x: (x-10) * 0.50 + 2*0.25)
        assertRange(13,100, lambda x: (x-12) * 1.00 + 2*0.50 + 2*0.25)

    def test_evening_hours(self):
        def assertHours(t0,t1,h):
            self.assertEqual(evening_hours(make_interval(t0,t1)), h)
        assertHours(( 0,0),( 6,0), 6)
        assertHours(( 6,0),(18,0), 0)
        assertHours((18,0),( 6,0),12)

        assertHours(( 0,0),(12,0), 6)
        assertHours((12,0),(23,0), 5)
        assertHours((23,0),(12,0), 7)

        assertHours(( 2,0),(22,0), 8)
        assertHours((14,0),(10,0),12)
        assertHours((23,0),(22,0),11)

    def test_read(self):
        persons = read_hourlist(self.tempfile)
        self.assertEqual(len(persons), 2)
        self.assertEqual(persons[1].name, "AAA AAA")
        self.assertEqual(persons[2].name, "BBB BBB")
        self.assertEqual(sum(i.hours() for i in persons[1].days[1]), 12)
        for day_idx in range(1,6):
            self.assertEqual(sum(i.hours() for i in persons[2].days[day_idx]), 23)

    def test_wage(self):
        persons = read_hourlist(self.tempfile)
        self.assertEqual(persons[1].total_wage(),    (12+overtime(12))*HOURLY_WAGE +  6*EVENING_BONUS)
        self.assertEqual(persons[2].total_wage(), 5*((23+overtime(23))*HOURLY_WAGE + 11*EVENING_BONUS))


if __name__ == '__main__':
    unittest.main()
