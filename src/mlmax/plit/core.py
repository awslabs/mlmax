# -*- coding: utf-8 -*-


"""Base functionality for three different types of charts.

Includes plot (for line chart and scatter), hist, and bar.

    Todo:
        * test out plotting arrays of arrays
        * make sure time series works with line chart
"""

import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import numpy as np
import os

COLORS = ["g", "b", "r", "k", "c"]
VISUAL_DIR = "../../../reports/figures"
STYLESHEET = "../../../config/default.mplstyle"
plt.style.use(STYLESHEET)


def hist(
    x_li,
    xlab,
    labels,
    ax=None,
    grid=False,
    alpha=0.7,
    edgecolor="0.1",
    ylab="Count",
    colors=None,
    title=None,
    subtitle=None,
    figsize=(10, 7),
    figname=None,
    **kwargs
):
    """Create a simple histogram.

    Args:
        x_li (list:arrays): list of data arrays to create bins and counts for.
        xlab (str): Descriptive x label.
        labels (list:str): labels for each series to be displayed on legend.
        ax (Axes, optional): A matplotlib Axes object.
        grid (bool, optional): whether you would like a bacground grid.
        title (str): Descriptive title for the chart.
        subtitle (string, optional): chart subtitle
        alpha (float, optional): transparency.
        edgecolor (string, optional): color for edges.
        ylab (str, optional): Y axis value.
        colors (list:str, optional): Colors for the bars if desired to overwrite
            defaults.
        bins (int or list:float, optional): the number or actual bins to count data in.
            Default to 10.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Axes object: for more detail see matplotlib docs:
            https://matplotlib.org/3.1.1/api/index.html#the-object-oriented-api
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    if colors is None:
        colors = COLORS
    for i in range(len(x_li)):
        ax.hist(
            x_li[i],
            label=labels[i],
            color=colors[i],
            edgecolor=edgecolor,
            alpha=alpha,
            **kwargs
        )
    ax.grid(grid)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.legend()
    if title:
        ax.set_title(title, loc="left", color="k")
    if subtitle is not None:
        ax.set_title(subtitle, loc="right", fontsize=13, color="grey")
    if figname is not None:
        plt.savefig(os.path.join(VISUAL_DIR, figname), bbox_inches="tight")
    return ax


def bar(
    x,
    y_li,
    labels,
    xlab,
    ylab,
    ax=None,
    ylim=None,
    grid=False,
    href=None,
    title=None,
    subtitle=None,
    overlap=False,
    colors=None,
    horizontal=False,
    figsize=(10, 7),
    pct_ticks=False,
    figname=None,
    **kwargs
):
    """Create a bar plot for up to 5 series/groups.

    Args:
        x (list:string): list of group labels for x axis.
        y_li (list[:list]:float): list or list of lists of data points y-coordinates.
        labels (list:str): labels for each series to be displayed on legend.
        xlab (string): label for x-axis
        ylab (string): label for y-axis
        ax (Axes, optional): A matplotlib Axes object.
        ylim (list:float, optional): optional limiter for y-axis.
        grid (bool, optional): whether you would like a bacground grid.
            Defaults to false.
        href (float, optional): whether you would like a horizontal ref. line.
        title (string, optional): chart title
        subtitle (string, optional): chart subtitle.
        overlap (bool, optional): Come back.
        colors (list:str, optional): Colors for the bars if desired to overwrite
            defaults.
        horizontal (bool, optional): Select horizontal bars.
        figsize (tuple:int, optional): figure size. Ignored if Axes object provided.
        pct_ticks (bool, optional): Whether you want percent ticks.
        figname (string, optional): figure name if you would like a saved image.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Axes object: for more detail see matplotlib docs:
            https://matplotlib.org/3.1.1/api/index.html#the-object-oriented-api
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    assert len(y_li) <= 5, "Please select <= 5 series"
    assert len(y_li) == len(labels), "len(y_li) != len(labels)"
    assert len(y_li[0]) == len(x), "len(y_li[i]) != len(x)"
    x_int = np.arange(len(x))
    w = 0.8 / len(y_li)
    adj = np.array([-2 * w, -3 / 2 * w, -w, -w / 2, 0, w / 2, w, 3 * w / 2, 2 * w])
    x_adj = adj[5 - len(y_li) : len(adj) - (5 - len(y_li)) : 2]

    if overlap:
        x_adj = np.zeros_like(x_adj)
    w *= len(y_li)
    if colors is None:
        colors = COLORS
    for i in range(len(y_li)):
        if horizontal:
            ax.barh(
                x_int + x_adj[i], y_li[i], w, label=labels[i], color=colors[i], **kwargs
            )
            ax.set_ylabel(xlab)
            ax.set_xlabel(ylab)
            ax.set_yticks(x_int)
            ax.set_yticklabels(x)
        else:
            ax.bar(
                x_int + x_adj[i], y_li[i], w, label=labels[i], color=colors[i], **kwargs
            )
            ax.set_xlabel(xlab)
            ax.set_ylabel(ylab)
            ax.set_xticks(x_int)
            ax.set_xticklabels(x)
    if ylim:
        ax.set_ylim(ylim)
    ax.grid(grid)
    if href:
        ax.axhline(href, linestyle="--", color="k")
    if title:
        ax.set_title(title, loc="left", color="k")
    if subtitle is not None:
        ax.set_title(subtitle, loc="right", fontsize=13, color="grey")
    ax.legend()
    if pct_ticks:
        if horizontal:
            ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
        else:
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    if figname is not None:
        plt.savefig(os.path.join(VISUAL_DIR, figname), bbox_inches="tight")
    return ax


def plot(
    x_li,
    y_li,
    labels,
    xlab,
    ylab,
    ax=None,
    xlim=None,
    ylim=None,
    href=None,
    vref=None,
    title=None,
    subtitle=None,
    xticks=None,
    set_xticks=False,
    pct_ticks=(False, False),
    marker_type="-",
    markers=None,
    figname=None,
    grid=False,
    figsize=(10, 7),
    **kwargs
):
    """Create a line chart or scatter forseries/groups.

    Args:
        x_li (list[:list]:string): list or list of lists of data points x-coordinates.
        y_li (list[:list]:float): list or list of lists of data points y-coordinates.
        labels (list:str): labels for each series to be displayed on legend.
        xlab (string): label for x-axis
        ylab (string): label for y-axis
        ax (Axes, optional): A matplotlib Axes object.
        xlim (list:float, optional): optional limiter for x-axis
        ylim (list:float, optional): optional limiter for y-axis
        href (float, optional): horizontal ref. line.
        vref (float, optional): vertical ref. line.
        title (string, optional): chart title
        subtitle (string, optional): chart subtitle
        xticks (list:float, optional): xticks to be used if not `x`.
        set_xticks (bool, optional): Whether xticks should be set based
            off of the x data. Only useful when there are few unique data
            points (e.g., 10).
        pct_ticks (tuple:bool, optional): Whether you want percent ticks for (x,y)
        marker_type (string, optional): Common options: '-' (line),
            '--' (dashed line), 'o' (scatter), and 'o-' (line with dots).
            See matplotlib docs for complete list.
            https://matplotlib.org/3.1.1/api/markers_api.html
            Will be ignored if series-specific markers are provided.
        markers (list:string, optional): Marker types using the standard shorthand.
            Useful when compariing multiple types of objects.
            For example, compariing  models and hypers in the same chart.
            Colors and shapes can be combined (e.g. 'k-' for black lines)
        figname (string, optional): figure name if you would like a saved image
        grid (bool, optional): whether you would like a bacground grid.
        figsize (tuple:int, optional): figure size. Ignored if Axes object provided.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Axes object: for more detail see matplotlib docs:
            https://matplotlib.org/3.1.1/api/index.html#the-object-oriented-api
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    assert len(y_li) == len(labels), "len(y_li) != len(labels)"
    if markers is None:
        markers = [m + marker_type for m in COLORS]
    assert len(markers) >= len(y_li), "len(markers) < len(y_li)"
    for i in range(len(y_li)):
        if len(x_li) == 1:
            x = x_li[0]
        else:
            x = x_li[i]
        ax.plot(x, y_li[i], markers[i], label=labels[i], **kwargs)
        ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.grid(grid)
    if ylim:
        ax.set_ylim(ylim)
    if xlim:
        ax.set_xlim(xlim)
    if vref:
        ax.axvline(vref, linestyle="--", color="gray")
    if href:
        ax.axhline(href, linestyle="--", color="gray")
    if title:
        ax.set_title(title, loc="left", color="k")
    if subtitle is not None:
        ax.set_title(subtitle, loc="right", fontsize=13, color="grey")
    if xticks is not None:
        ax.set_xticks(xticks)
    elif set_xticks:
        ax.set_xticks(x)
    if pct_ticks[0]:
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    if pct_ticks[1]:
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.legend()
    if figname is not None:
        plt.savefig(os.path.join(VISUAL_DIR, figname), bbox_inches="tight")
    return ax


def subplots(ncols=1, nrows=1, figsize=(8, 8), **kwargs):
    """For creating subplots.

    Args:
        ncols (int, optional): Number of columns.
        nrows (int, optional): Number of rows.
        figsize (tuple:int, optional): size for entire chart.
            Counterintuitively, but in keeping with matplotlib
            convention, specified as (width, height).

    Returns:
        A tuple consisting of a matplotlib figure and a
        matplotlib Axes array.
    """
    return plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, **kwargs)
