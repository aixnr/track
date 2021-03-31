# track

A small utility script for producing Github-style activity heatmap. This script requires the following libraries: `pandas`, `numpy`, and `seaborn`.

## Why

Because I wanted to track my productivity-related metrics, and wanted to do so to get a general overview of a specific year, [in line with the PACT](https://nesslabs.com/smart-goals-pact) goal-tracking scheme.

## The spreadsheet

The recommended design of the spreadsheet is as follows:

| month | date | day | status
| ----- | ---- | --- | ------
| 3     | 8    | Mon | 10
| 3     | 9    | Tue | 5
| --    | --   | --  | --

Because this script is case-sensitive, all column headers must be in lowercase.

As for my personal convention, 10 means "positive" or "yes", 5 means "negative" or "no", depending on the activity being tracked.

## How to use

```python
# Import modules
import matplotlib.pyplot as plt
from track import track

# Instantiate the Figure and Axes objects
fig, ax = plt.subplots()

# Draw the plot; section refers to the specific sheet name
track.calendar_viz(year=2021, data="path/to/data.ods", section="Experiment", plot=True, ax=ax)
```

Default values are assigned as `1` for dates that do not have entries in the spreadsheet.

## How it works

Because I was bored (or actually trying to productively procrastinate), and quite impressed by the level of details in this [readme (Overv/outrun)](https://github.com/Overv/outrun), I decided to explain how I wrote the main logic for this small module.

The main function that is responsible for drawing the chart is `track.calendar_viz()`, which is shown above, and it has several parameters. The first thing that happens is that it calls the function `track.calendar_merge()`, which performs the following:

1. Read the sheet containing the data, using Pandas `read_excel()` function.
2. Calls `track.calendar_full()` to return the full calendar for the specified year.
3. Performs `outer` join to merge full calendar (from `track.calendar_full()`) with the `dataframe` from the sheet imported from the first step.
4. Finally, returns the merge `dataframe` object.

The function `track.calendar_full()` takes care a lot of things. It creates a long dataframe containing all the necessary information, which also includes day of the year (1-365 or 366) and week number. Once ready to be merged, the `track.calendar_merge()` drops the `status` column, joins the data, then fill N/A in the `status` column with bunch of `ones`.

Next, this main function calls `track.calendar_wide()`, which basically returns a `dataframe` with 7 x `_week_max` (i.e. maximum number of weeks in a year, e.g. 53). This `dataframe` is the one that Seaborn will use to generate a heatmap. And then, it would loop to copy the `status` data from `track.calendar_merge()` output by using day of the week (integer, Monday = 0) and week of the year as the row and column reference. Then, Seaborn takes over to draw a heatmap on the specified `Axes` object from `matplotlib.pyplot.subplots()` function call.

For aesthetic when `mo_tick` (month ticker) is set to `True` (default), a list with a length of the maximum number of week in a year (e.g. 53) with default value of an empty `""` string except where new month starts (denoted with 3-letter string, e.g. "May"), this list will be used by `ax.set_xticklabels()` to put mark the month on the final heatmap.
