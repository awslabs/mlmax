# -*- coding: utf-8 -*-

"""Templates for common tasks in ML Interpretation."""

import numpy as np
from functools import partial
from .core import plot, hist

prob_hist = partial(
    hist,
    ylab="Observation Count (Valid)",
    xlab="Probability Bucket",
    bins=np.arange(0, 1.1, 0.1),
)
prob_hist.__doc__ = """Histogram for charting probabilities."""

pr_curve = partial(
    plot,
    labels=["Recall", "Precision"],
    xlab="Threshold Cutoff for Positive Class",
    ylab="Precision or Recall",
    title="Choosing a Threshold",
    markers=["g--", "b--", "r--", "k--", "c--"],
    grid=True,
)
pr_curve.__doc__ = """Dashed line chart for charting precision and recall curve."""
