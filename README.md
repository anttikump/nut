[![Build Status](https://travis-ci.org/warbaque/nut.svg?branch=master)](https://travis-ci.org/warbaque/nut)

Nut
===

- A hourlist.csv parser
- Nuts for squirrels

Tested with Python 3.6

(No ``pip`` install available at this time.)


Quick Start
-----------

Requires `dateutil`

    git clone https://github.com/warbaque/nut
    cd nut
    ./nut.py --help


Use Examples
------------

**Generate single report:**

    ❯ ./nut.py "recruitment-nut/HourList201403.csv" "recruitment-nut"
    ==================================================
    Read  'recruitment-nut/HourList201403.csv'
    Wrote 'recruitment-nut/Report201403.csv'
    ==================================================

**Generate multiple reports:**

    ❯ ./nut.py "recruitment-nut/HourList*.csv" "recruitment-nut"
    ==================================================
    Read  'recruitment-nut/HourList201403.csv'
    Wrote 'recruitment-nut/Report201403.csv'
    ==================================================
    ==================================================
    Read  'recruitment-nut/HourList201404.csv'
    Wrote 'recruitment-nut/Report201404.csv'
    ==================================================

**Print verbose output:**

    ❯ ./nut.py "recruitment-nut/HourList201403.csv" "recruitment-nut" -v
    ==================================================
    Read  'recruitment-nut/HourList201403.csv'
    >   ID  NAME            TOTAL
    >   1   Janet Java      $701.60
    >   2   Scott Scala     $657.34
    >   3   Larry Lolcode   $377.00
    Wrote 'recruitment-nut/Report201403.csv'
    ==================================================
