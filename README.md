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
