"""
Time Series Labeller/Annotator

Product Feature Request (Amazon VPN):
https://aws-crm--c.na67.visual.force.com/a2v0z000002HTaa

Multivariate Time Series (MTS) is a very common problem in the real-world which usually
suffers from low signal-to-noise ratio, e.g. predictive maintenance, financial forecasting, etc.
Also MTS are difficult to clean, preprocess and transform in order to build ML models due to the
complex informations it contains from their sources.

It would be very crucial to have an effective labelling/annotation tool to
handle MTS labelling/preprocessing/segmentation/transforming.
This would laid an important foundation for the following steps of forecasting/classification/regression
with ML models.
"""


import json
from itertools import cycle

import numpy as np
import pandas as pd
from bqplot import Axis, DateScale, Figure, LinearScale, Lines
from bqplot.interacts import BrushIntervalSelector
from ipywidgets import HTML, Button, Dropdown, HBox, VBox, widgets

COLOUR_LIST = [
    "#008080",
    "#e6beff",
    "#9a6324",
    "#fffac8",
    "#800000",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#46f0f0",
    "#aaffc3",
    "#808000",
    "#ffd8b1",
    "#000075",
    "#808080",
    "#ffffff",
    "#000000",
    "#e6194b",
    "#3cb44b",
    "#ffe119",
    "#f032e6",
    "#bcf60c",
    "#fabebe",
]


class TimeSeriesAnnotator:
    """
    Prototype of Interactive Annotation of Multivariate Time Series Data

    >>> from mlmax.annotator import TimeSeriesAnnotator
    >>> import pandas as pd
    >>> import numpy as np
    >>> # use example open source data from NASA
    >>> nasa_telemetry_df = pd.read_pickle("../data/raw/CMAPSSData/train_FD001.pkl")
    >>> # randomly pick one machine
    >>> sample_nasa_telemetry = nasa_telemetry_df[
    >>>     nasa_telemetry_df["unit"] == np.random.choice(range(1, 101))
    >>> ]
    >>> # use timestamp "cycle" as index of dataframe
    >>> sample_nasa_telemetry.set_index('cycle', inplace=True)
    >>> # dimension of variant
    >>> sensor_id = sample_nasa_telemetry.columns[1:]
    >>> # self-define different events to annotate
    >>> events = ["Normal", "Planned_Shutting_Down", "Accident", "Recovery", "Miscellaneous"]
    >>> # define the output path
    >>> ANNOTATION_PATH = "../data/raw/CMAPSSData/anno_res.txt"
    >>> tsa = TimeSeriesAnnotator(
    >>>     df_timeseries=sample_nasa_telemetry,
    >>>     sensor_id=sensor_id,
    >>>     evts=events,
    >>>     output_path=ANNOTATION_PATH,
    >>>     timescale=False
    >>> )
    >>> # stand up the annotation dashboard
    >>> tsa.dashboard()
    """

    def __init__(
        self,
        df_timeseries: pd.DataFrame,
        sensor_id: list,
        evts: list,
        output_path: str,
        timescale: bool = True,
    ):
        """
        Parameters
        ----------
        df_timeseries: pd.DataFrame
            Time Series Dataset
        sensor_id: list
            multivariate sensor id
        evts: list
            different events to label
        output_path: list
            save path of annotation results
        timescale: bool = True
            display x axis as timescale in datetime
        """
        self._df_timeseries = df_timeseries
        self._sensor_id, self._evts = sensor_id, evts
        self._output_path = output_path
        self.sensor_colors, self.evt_colors = {}, {}
        self.annotation_res = []
        self.time_scale_ctr = timescale
        if self.time_scale_ctr:
            self.x_axis_scale = DateScale
        else:
            self.x_axis_scale = LinearScale

    def dashboard(self):
        """
        Standup the Annotation DashBoard

        Returns
        -------

        """
        self.__set_button()
        self.__set_evt_sensor_colour()
        self.vis = self.__set_view_layout()
        self.__wire_interaction()
        return self.vis

    def __highlight_annotation(self, x_scale):
        """
        Draw Rectangle Around annotating Period of Time
        Parameters
        ----------
        x_scale

        Returns
        -------

        """
        (
            self._evts,
            self.sensor,
            self.x_range,
            self.y_range,
        ) = self._parse_annotation_res()
        self._color_evt_sensor()
        return Lines(
            x=self.x_range,
            y=self.y_range,
            scales={"x": x_scale, "y": LinearScale()},
            stroke_width=5,
            close_path=True,
            fill="inside",
            fill_opacities=[0.4] * len(self.x_range),
            fill_colors=self.evt_colors,
            colors=self.sensor_colors,
        )

    def __set_button(self):
        """
        Create all buttons to click
        Returns
        -------

        """
        # create a dropdown menu for sensors
        self.dropdown_sensor = Dropdown(description="Sensor", options=self._sensor_id)
        self.current_sensor = self.dropdown_sensor.value
        # create a button to trigger annotate
        self.btn_record = Button(description="Record", button_style="success")
        # create a button to trigger saving image
        self.btn_save_image = Button(description="Save Image", button_style="warning")
        # create a button to trigger saving annotation
        self.btn_save_annotation = Button(
            description="Save Annotation", button_style="warning"
        )
        # create a button to trigger loading annotation
        self.btn_load_annotation = Button(
            description="Load Annotation", button_style="warning"
        )
        # create a button to undo last annotation
        self.btn_undo_annotation = Button(
            description="Undo Annotation", button_style="warning"
        )
        # create at button to empty all annotation
        self.btn_clear_annotation = Button(
            description="Clear Annotation", button_style="warning"
        )
        # create a dropdown menu for events
        self.dropdown_evt = Dropdown(description="Event", options=self._evts)
        self.current_event = self.dropdown_evt.value

    def __set_evt_sensor_colour(self):
        """
        Set sensor&event colours
        Returns
        -------

        """
        self.sensor_colors_dict = self._assign_colour(self._sensor_id)
        self.evt_colors_dict = self._assign_colour(self._evts)

    def __set_view_layout(self):
        """
        Set the Dashboard view layout
        Returns
        -------

        """
        self._set_plot_brush()
        # The following text widgets are used to display the `selected` attributes
        self.sensor_selector = HTML()
        self.event_selector = HTML()
        self.ctr_range_selector = HTML()
        self.annotator_selector = HTML()
        self.annotation_result = HTML()
        self.title = HTML()
        self.title.value = "<h2>Interactive Time Series Signal Annotator</h2><hr/>"

        return VBox(
            [
                self.title,
                HBox([self.dropdown_sensor, self.dropdown_evt, self.btn_record]),
                self.annotation_plt,
                self.control_plt,
                HBox(
                    [
                        self.btn_save_annotation,
                        self.btn_load_annotation,
                        self.btn_undo_annotation,
                        self.btn_clear_annotation,
                        self.btn_save_image,
                    ]
                ),
                self.annotation_result,
            ]
        )

    def __wire_interaction(self):
        """
        Combine interactive components with their corresponding callbacks
        Returns
        -------

        """
        # bind sensor dropdown callback
        self.dropdown_sensor.observe(self._update_sensor_callback, "value")
        # bind event dropdown callback
        self.dropdown_evt.observe(self._update_event_callback, "value")
        # bind control range selector callback
        self.ctr_br_intsel.observe(self._update_ctr_brush_text_callback, "selected")
        # bind annotator range selector callback
        self.annotator_br_intsel.observe(
            self._update_anno_brush_text_callback, "selected"
        )
        # zoom in
        self.ctr_br_intsel.observe(self._change_range_callback, names=["selected"])
        # annotation call back
        self.btn_record.on_click(self._record_annotator_callback)
        # save image call back
        self.btn_save_image.on_click(self._save_image_callback)
        # save annotation call back
        self.btn_save_annotation.on_click(self._save_annotation_callback)
        # load annotation call back
        self.btn_load_annotation.on_click(self._load_annotation_callback)
        # empty annotation call back
        self.btn_clear_annotation.on_click(self._empty_annotation_callback)
        # undo annotation call back
        self.btn_undo_annotation.on_click(self._undo_annotation_callback)

    @staticmethod
    def _ts_plot_line(idx, y, dt_x=DateScale(), label_axis=True):
        """
        Generate bqplot Line

        Parameters
        ----------
        idx
        y
        dt_x
        label_axis

        Returns
        -------

        """
        lin_y = LinearScale()

        if label_axis:
            x_ax = Axis(label="Timestamp", scale=dt_x)
            x_ay = Axis(label="Value", scale=lin_y, orientation="vertical")
        else:
            x_ax = Axis(scale=dt_x)
            x_ay = Axis(scale=lin_y, orientation="vertical")

        line_plt = Lines(x=idx, y=y, scales={"x": dt_x, "y": lin_y})

        return line_plt, x_ax, x_ay, dt_x, lin_y

    @staticmethod
    def _assign_colour(lists):
        """
        Assign colour to different variates and events about to label
        Parameters
        ----------
        lists

        Returns
        -------

        """
        cols = cycle(COLOUR_LIST)
        evt_colors_dict = {}
        for evt in lists:
            evt_colors_dict[evt] = next(cols)
        return evt_colors_dict

    def _parse_annotation_res(self):
        """
        Parse Annotation result which is in a format of list of dictionaries

        Returns
        -------

        """
        evts, sensor, x_range, y_range = [], [], [], []

        for item in self.annotation_res:
            evts.append(item["event"])
            sensor.append(item["sensor"])
            x_range.append(
                [
                    item["starting_time"],
                    item["starting_time"],
                    item["ending_time"],
                    item["ending_time"],
                ]
            )
            y_range.append([-100, 100, 100, -100])
        return evts, sensor, x_range, y_range

    def _color_evt_sensor(self):
        """
        Set colour to be used to draw
        Returns
        -------

        """
        self.evt_colors = [self.evt_colors_dict[x] for x in self._evts]
        self.sensor_colors = [self.sensor_colors_dict[x] for x in self.sensor]

    def _set_plot_brush(self):
        """
        Create plotting area and selecting brush
        Returns
        -------

        """
        # zoomed in plot line
        (
            self.disp_line,
            self.disp_x_ax,
            self.disp_x_ay,
            self.disp_x_scale,
            self.disp_y_scale,
        ) = self._ts_plot_line(
            self._df_timeseries.index.values,
            self._df_timeseries[self.current_sensor].values,
            self.x_axis_scale(),
            label_axis=False,
        )

        # control panel plot line
        (
            self.ctr_line,
            self.ctr_x_ax,
            self.ctr_x_ay,
            self.ctr_x_scale,
            self.ctr_y_scale,
        ) = self._ts_plot_line(
            self._df_timeseries.index.values,
            self._df_timeseries[self.current_sensor].values,
            self.x_axis_scale(),
        )

        # brush: annotator
        self.annotator_br_intsel = BrushIntervalSelector(
            scale=self.disp_x_scale, marks=[self.disp_line]
        )

        # zoom in/annotating plot
        self.annotation_plt = Figure(
            layout=widgets.Layout(width="100%", height="280pt"),
            marks=[self.disp_line, self.__highlight_annotation(self.disp_x_scale)],
            axes=[self.disp_x_ax, self.disp_x_ay],
            title=f"{self.current_sensor}",
            fig_margin=dict(top=30, bottom=20, left=40, right=40),
            interaction=self.annotator_br_intsel,
        )

        # brush: zoom in
        self.ctr_br_intsel = BrushIntervalSelector(
            scale=self.ctr_x_scale, marks=[self.ctr_line]
        )

        # control plot
        self.control_plt = Figure(
            layout=widgets.Layout(width="100%", height="120pt"),
            marks=[self.ctr_line, self.__highlight_annotation(self.ctr_x_scale)],
            axes=[self.ctr_x_ax, self.ctr_x_ay],
            fig_margin=dict(top=10, bottom=20, left=40, right=40),
            interaction=self.ctr_br_intsel,
            stroke_width=0.1,
        )

    def _update_sensor_callback(self, *_):
        """
        update the selected sensor
        """
        selected_ticker = self.dropdown_sensor.value
        self.ctr_line, self.ctr_x_ax, self.ctr_x_ay, *_ = self._ts_plot_line(
            self._df_timeseries.index.values,
            self._df_timeseries[selected_ticker].values,
            self.x_axis_scale(),
        )
        self.disp_line, self.disp_x_ax, self.disp_x_ay, *_ = self._ts_plot_line(
            self._df_timeseries.index.values,
            self._df_timeseries[selected_ticker].values,
            self.disp_x_scale,
            label_axis=False,
        )

        self.control_plt.marks, self.control_plt.axes = (
            [self.ctr_line, self.__highlight_annotation(self.ctr_x_scale)],
            [self.ctr_x_ax, self.ctr_x_ay],
        )
        (
            self.annotation_plt.marks,
            self.annotation_plt.axes,
            self.annotation_plt.title,
        ) = (
            [self.disp_line, self.__highlight_annotation(self.disp_x_scale)],
            [self.disp_x_ax, self.disp_x_ay],
            f"{selected_ticker}",
        )
        self.sensor_selector.value = "The sensor selected is: {}".format(
            self.dropdown_sensor.value
        )

    def _update_event_callback(self, *_):
        """
        update the selected event
        """
        self.event_selector.value = "The event to annotate is: {}".format(
            self.dropdown_evt.value
        )

    def _update_ctr_brush_text_callback(self, *_):
        self.ctr_range_selector.value = (
            f"The CONTROL Brush's selected attribute is {self.ctr_br_intsel.selected}"
        )

    def _update_anno_brush_text_callback(self, *_):
        self.annotator_selector.value = (
            f"The ANNOTATOR Brush's selected attribute is: "
            f" {self.annotator_br_intsel.selected}"
        )

    def _change_range_callback(self, change):
        if len(change["new"]) == 2:
            if self.time_scale_ctr:
                self.disp_x_scale.min = pd.to_datetime(change["new"][0])
                self.disp_x_scale.max = pd.to_datetime(change["new"][1])
            else:
                self.disp_x_scale.min = change["new"][0]
                self.disp_x_scale.max = change["new"][1]

    def _record_annotator_callback(self, *_):
        res = {
            "event": self.dropdown_evt.value,
            "sensor": self.dropdown_sensor.value,
            "starting_time": self.annotator_br_intsel.selected[0],
            "ending_time": self.annotator_br_intsel.selected[1],
        }
        self.annotation_res.append(res)
        self.annotation_result.value = (
            f"sensor: {res['sensor']} with event: \
            {res['event']}, starting from {res['starting_time']} "
            f"to {res['ending_time']}"
        )
        self._highlight_callback()

    def _highlight_callback(self):
        self.annotation_plt.marks = [
            self.annotation_plt.marks[0],
            self.__highlight_annotation(self.disp_x_scale),
        ]
        self.control_plt.marks = [
            self.control_plt.marks[0],
            self.__highlight_annotation(self.ctr_x_scale),
        ]

    def _save_image_callback(self, *_):
        self.annotation_plt.save_png(filename="annotation.png")

    def _save_annotation_callback(self, *_):
        with open(self._output_path, "w") as file:
            file.write(json.dumps(self.annotation_res, default=str))

    def _load_annotation_callback(self, *_):
        try:
            with open(self._output_path) as json_file:
                annotation_read = json.load(json_file)
                for dic in annotation_read:
                    if self.time_scale_ctr:
                        dic["starting_time"] = np.datetime64(dic["starting_time"])
                        dic["ending_time"] = np.datetime64(dic["ending_time"])
                    else:
                        dic["starting_time"] = dic["starting_time"]
                        dic["ending_time"] = dic["ending_time"]

            self.annotation_res.extend(annotation_read)
        except IOError as e:
            raise IOError("The annotation file does not exist") from e
        finally:
            self._highlight_callback()

    def _undo_annotation_callback(self, *_):
        try:
            self.annotation_res.pop()
        except IndexError:
            pass
        finally:
            self._highlight_callback()

    def _empty_annotation_callback(self, *_):
        self.annotation_res.clear()
        self._highlight_callback()
