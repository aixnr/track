# Import modules
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime, date


def calendar_full(year=None, subset_month=None):
    """
    Creates a Pandas DataFrame with the following columns:
      Year             (int)          ; yr
      Month            (int)          ; mo_i
      Month            (str, English) ; mo_e
      Date             (int)          ; date
      Day of the year  (int)          ; doy
      Week of the year (int)          ; woy
      Day              (int, 0 = Mon) ; day_i
      Day              (str, English) ; day_e
      Status           (str)          ; status (default to 1 for empty)

    Args:
      year         : int, Year to make a calendar for
      subset_month : str, Only return the specified month

    Return:
      A Pandas DataFrame with columns specified above
    """
    # Constant; total days in a year without Feb
    _TOTAL_DAYS_MINUS_FEB = 337

    # Constant; check if leap year or not
    if year % 4 != 0:
        _feb = 28
        _total_days = 365
    else:
        _feb = 29
        _total_days = 366

    # Constant, total days in a year + Feb
    _TOTAL_DAYS = _TOTAL_DAYS_MINUS_FEB + _feb

    # Constant; dictionary of days in a month
    _month_dict = {
        "01": 31,
        "02": _feb,
        "03": 31,
        "04": 30,
        "05": 31,
        "06": 30,
        "07": 31,
        "08": 31,
        "09": 30,
        "10": 31,
        "11": 30,
        "12": 31
    }

    # Constant; dictionary of month name (English, 3 letter abbr)
    _month_name = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec"
    }

    # Constant; dictionary of day of the week
    _weekday = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}

    # Looper to initialize calendar
    _calendar = pd.DataFrame(columns=["date"])
    for _mo in _month_dict:
        _mo_i = _mo                  # Key (month number)
        _mo_days = _month_dict[_mo]  # Value (total days in that given month)

        _list_days = [x+1 for x in range(_mo_days)]           # Create list on number of days for a given month
        _mo_cal = pd.DataFrame(_list_days, columns=["date"])  # Insert it into a DataFrame
        _mo_cal["mo_i"] = _mo_i                               # Insert a column for month (integer)
        _mo_cal["mo_e"] = _month_name[_mo_i]                  # Insert a column for month (English, 3 letter)
        _calendar = _calendar.append(_mo_cal)                 # Append to _calendar DataFrame

    # Insert Year (yr) Day of Year (doy)
    _calendar["yr"] = year
    _days_list = [_d+1 for _d in range(_total_days)]
    _calendar["doy"] = _days_list

    # Insert day of the week, English
    _calendar["mo_i"] = _calendar["mo_i"].apply(lambda x: int(x))
    _calendar["day_e"] = _calendar.apply(lambda x: date(x["yr"], x["mo_i"], x["date"]).strftime("%a"), axis=1)

    # Insert day of the week, integer, Monday = 0
    _calendar["day_i"] = _calendar["day_e"].apply(lambda x: _weekday[x])

    # Insert week of the year
    _calendar["woy"] = _calendar.apply(lambda x: date(x["yr"], x["mo_i"], x["date"]).isocalendar()[1], axis=1)

    # Insert empty status
    _calendar["status"] = 1

    # Return DataFrame
    _sorted_cols = ["yr", "mo_i", "mo_e", "date", "doy", "woy", "day_i", "day_e", "status"]
    return _calendar.reset_index(drop=True)[_sorted_cols]


def calendar_wide(year=None):
    """
    Create a Pandas DataFrame in wide format, rows as day of the week (start at Monday), columns as WOY

    Args:
      year: int, Year to make the calendar for

    Return:
      A wide dataframe, to be used with calendar_viz()
    """
    # Return full calendar of the year, then get max week
    _calendar = calendar_full(year)
    _week_max = _calendar["woy"].max()

    # Create NumPy array, shape(row, col); and then use it to build a DataFrame
    _cal_wide = pd.DataFrame(np.ones(shape=(7, _week_max)))

    # Rename column, +1 (because it started with zero)
    _cal_wide.columns = [x+1 for x in range(_week_max)]

    # Return
    return _cal_wide


def calendar_merge(year=None, data=None, section=None, sheet_type="odf"):
    """
    Performs outer merge between calendar_full(year) and tracker data (as spreadsheet)

    Args:
      year       : int, The year of tracking collection
      data       : str, The spreadsheet file containing tracking information
      section    : str, Section to retrieve
      sheet_type : str, Use "odf" for Open Document Format (default), None for Excel spreadsheet

    Returns:
      A merged Pandas DataFrame
    """
    # Read data
    _tracker = pd.read_excel(data, sheet_name=section, engine=sheet_type)

    # Rename column to match _calendar DataFrame
    _tracker = _tracker.rename(columns={"month": "mo_i", "day": "day_e"})

    # Perform merge, for status column, df.fillna() to replace NaN with ones
    _calendar = calendar_full(year).drop(columns="status")
    _df = _calendar.merge(_tracker, on=["date", "mo_i", "day_e"], how="outer").fillna(1)

    # Return data
    return _df


def month_ticker(year=None):
    """
    Generate month_ticker, use inside calendar_viz() to show month on the x-axis

    """
    # Get full calendar
    _calendar = calendar_full(year=year)

    # Retrieve unique month names (3-letter), place into dictionary with corresponding first WOY of that month
    _mo_week = {}
    for _mo_e in _calendar["mo_e"].unique().tolist():
        _month_first_week_number = _calendar.query(" mo_e == @_mo_e ")["woy"].min()  # Get first WOY of that month
        _mo_week[_mo_e] = _month_first_week_number                                   # Place into dictionary

    # Generate a list of numbers to pass into ax.set_xticklabels()
    _ticker_list = ["" for x in range(1, _calendar["woy"].max() + 1)]
    for _key in _mo_week:
        _idx = _mo_week[_key]            # Get first WOY of each _key (month)
        _ticker_list[_idx - 1] = _key    # Insert that into the list, -1 to account for zeroth-based indexing

    return _ticker_list


def calendar_viz(year=None, data=None, section=None, sheet_type="odf", plot=False, ax=None, mo_tick=True):
    """
    When plot is set to True, this produces the visualization in the form of heatmap.

    Args:
      year         : int, Year
      data         : str, Path to the spreadsheet file
      section      : str, the name of the sheet
      sheet_type   : str, None for Excel, "odf" for ODF (LibreOffice)
      plot         : bool, if True, draws the plot, requires ax
      ax           : str, the Axes object to draw the plot on
      mo_tick      : bool, if true, show month (3-letter str) on the x-axis

    Returns:
      plot:
        true: Draws with matplotlib
        false: Pandas DataFrame
    """
    # Read sheet
    _cal_long = calendar_merge(year=year, data=data, section=section, sheet_type=sheet_type)

    # Generate wide calendar
    _cal_wide = calendar_wide(year=year)

    # Get max doy of the year, use for looping later
    _doy_max = _cal_long["doy"].max()

    # Looper to retrieve status data, then insert into specified day_i and woy from calendar_wide()
    _cols = ["woy", "day_i", "status"]
    for _d in [x+1 for x in range(_doy_max)]:
        _stat_info = _cal_long.query(" doy == @_d ")[_cols]

        # Get specific day_i, woy, and status as single number, subsetting [0] from .to_list() output
        _d_i = _stat_info["day_i"].to_list()[0]
        _w = _stat_info["woy"].to_list()[0]
        _s = _stat_info["status"].to_list()[0]

        # Assign into _cal_wide with .at[], row first (day_i) and then column (woy)
        _cal_wide.at[_d_i, _w] = _s

    # Change day_i index into English name for the days
    _cal_wide = _cal_wide.rename(index={0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"})

    if not plot:
        return _cal_wide

    if plot:
        sns.heatmap(_cal_wide, ax=ax, cmap="PuRd", cbar=False, vmin=0, vmax=15, linewidths=.1)
        ax.set_title(f"{section}, Year {year}")    # Set title
        ax.tick_params(axis="both", length=0)         # Remove ticks on y, but retain label

        # Conditional for activating month ticks on the x-axis
        if not mo_tick:
            ax.set_xticklabels("")                     # Remove labels on x
            ax.set_xticks([])                          # Remove ticks on x
        if mo_tick:
            ax.set_xticklabels(month_ticker(year=year))
