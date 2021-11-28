"""Components built around streamlit widgets"""
import random

import datetime as dt
import plotly.graph_objs as go
import pandas as pd
import streamlit as st

from copy import deepcopy
from typing import Dict


class SymbolsInput:
	"""Form containing a text_input box and a button."""

	def __init__(
			self,
			form_key: str,
			container: st.container,
			title: str = None,
			title_importance: int = 1,
			text_input_description: str = None,
			text_input_help_txt: str = None,
			text_input_separator: str = ' ',  # can delete
			uploader_description: str = None,
			uploader_help_txt: str = None,
			submit_button_text: str = None,
			submit_button_clears: bool = True,
			parsed_case: str = 'upper'
	):
		self.form = container.form(
			key=form_key, clear_on_submit=submit_button_clears
		)
		self.title = None if not title else self.form.markdown(
			f'{"#"*title_importance} {title}'
		)
		self.uploader = self.form.file_uploader(
			label=uploader_description if uploader_description else '',
			help=uploader_help_txt if uploader_help_txt else ''
		)
		self.text_input = self.form.text_input(
			label=text_input_description if text_input_description else '',
			help=text_input_help_txt if text_input_help_txt else ''
		)
		self.button = self.form.form_submit_button(
			submit_button_text if submit_button_text else ''
		)
		self.progressbar_container = self.form.empty()
		self.progressmsg_container = self.form.empty()
		sep = text_input_separator
		case = {
			True: lambda x: x,
			False: lambda x: exec(f'''
			raise ValueError('case must be "upper" or "lower", not "{x}"')
			''')
		}[parsed_case in ['upper', 'lower']](parsed_case)
		self.parsed_input = [
			x for x in self.__parse_text_input(self.text_input, case, sep)
			if x != ''
		] or self.__parse_text_file()

	@staticmethod
	def __parse_text_input(text_input: st.text_input, c: str, s: str) -> list:
		return eval(f'sorted(list(set(text_input.{c}().split("{s}".{c}()))))')

	def __parse_text_file(self) -> list:
		uploader = self.uploader
		if uploader:
			return [
				x.strip(' ') for x in
				uploader.getvalue().decode('utf-8').upper().split()
			]


class SymbolsFilter:
	"""Component with radio buttons and a dropdown."""
	def __init__(
		self,
		container: st.container,
		input_objects: Dict[str, object] = None,
		title: str = None,
		title_importance: int = 4,
		radio_description: str = '',
		radio_options: dict = None,
		filter_type: bool = True
	):
		self.output = []
		if title:
			container.markdown(f'''{"#"*title_importance} {title}''')
		if radio_options:
			radio = container.radio(
				radio_description,
				options=[x for x in radio_options.keys()],
				format_func=lambda x: radio_options[x]
			)
			options = sorted(list({
					getattr(x, radio) for x in input_objects.values()
			}))
			filter_by = container.multiselect(
				f'{radio_options[radio]} selection:',
				options=options,
				default={
					'Any': [],
					'All': [] if len(options) > 1 else options,
					'Exclude': []
				}[filter_type]
			)
			self.output = {
				'Any': self._filter_any,
				'All': self._filter_all,
				'Exclude': self._filter_exclude
			}[filter_type](input_objects, radio, filter_by)

	@staticmethod
	def _filter_any(
		input_objects: Dict[str, object], attr: str, filter_by: list
	) -> list:
		out = []
		for k, v in input_objects.items():
			if getattr(v, attr) in filter_by:
				out.append(k)
		return out

	@staticmethod
	def _filter_all(
		input_objects: Dict[str, object], attr: str, filter_by: list
	) -> list:
		out = deepcopy(input_objects)
		for k, v in input_objects.items():
			if getattr(v, attr) not in filter_by:
				del out[k]
		return list(out.keys())

	@staticmethod
	def _filter_exclude(
		input_objects: Dict[str, object], attr: str, filter_by
	) -> list:
		out = deepcopy(input_objects)
		for k, v in input_objects.items():
			if getattr(v, attr) in filter_by:
				del out[k]
		return list(out.keys())


class TimeSeriesChart:
	"""Plotly chart(s) with some controls"""

	def __init__(
		self, container: st.container, symbols: list, data: pd.DataFrame
	):
		"""Note: data is a MultiIndex dataframe.
		There are two indices: symbol and dt.datetime.
		"""
		self.container = container
		columns = self.container.columns(4)
		start_date, end_date = self._filter_dates(
			data, columns[0].selectbox(
				'Select a time period',
				options=[
					'1Y',
					'6mo',
					'3mo',
					'1mo',
					'1wk',
					'5Y',
					'10Y',
					'all',
					'manual'
		]))
		self.symbols = symbols
		self.data = data.loc[[
			x for x in data.index
			if (x[1] >= start_date) and (x[1] <= end_date)
		]]
		self._plot_time_series(
			columns[1].selectbox('Select a plot type', ['line', 'OHLC']),
			columns[2].selectbox('Select a price type (for lines)', [
				'adjclose', 'open', 'high', 'low', 'close'
			]),
			columns[3].checkbox(
				'Normalize', value=True if len(symbols) > 1 else False
		))

	def _filter_dates(self, data: pd.DataFrame, time_period: str) -> tuple:
		dates = [x[1] for x in data.index]
		min_date = min(dates)
		max_date = max(dates)
		time_deltas = {
			'10Y': dt.timedelta(days=365*10),
			'5Y': dt.timedelta(days=365*5),
			'1Y': dt.timedelta(days=365*1),
			'6mo': dt.timedelta(days=int(365*0.5)),
			'3mo': dt.timedelta(days=int(365*0.25)),
			'1mo': dt.timedelta(days=int(365 / 12)),
			'1wk': dt.timedelta(days=7)
		}
		if time_period == 'manual':
			min_date, max_date = self.container.slider(
				'Select Date Range', value=(min_date, max_date)
			)
		else:
			if time_period in time_deltas:
				min_date = max_date - time_deltas[time_period]
		return min_date, max_date

	def _plot_time_series(self, plot_type: str, price_type: str, norm: bool):
		symbols = self.symbols
		fig = go.Figure()

		def _normalize(datum: float, data: pd.Series):
			return data / datum if norm else data

		colors_inc = [
			'aliceblue',
			'azure',
			'mediumslateblue',
			'mediumspringgreen',
			'olivedrab',
			'palegreen'
		]
		colors_dec = [
			'crimson',
			'lavenderblush',
			'magenta',
			'indianred',
			'coral',
			'orange'
		]

		for i, s in enumerate(symbols):
			data = self.data.loc[s]
			datum = data['open'].iloc[0]
			if plot_type == 'OHLC':
				if i == 0:
					color_inc = None
					color_dec = None
				else:
					color_inc = random.choice(colors_inc)
					color_dec = random.choice(colors_dec)
				fig.add_candlestick(
					name=s, x=data.index,
					open=_normalize(datum, data['open']),
					high=_normalize(datum, data['high']),
					low=_normalize(datum, data['low']),
					close=_normalize(datum, data['close']),
					increasing=go.candlestick.Increasing(
						fillcolor=color_inc, line={'color': color_inc}
					),
					decreasing=go.candlestick.Decreasing(
						fillcolor=color_dec, line={'color': color_dec}
					)
				)
			elif plot_type == 'line':
				fig.add_scatter(
					name=s, x=data.index,
					y={
						'open': _normalize(datum, data['open']),
						'high': _normalize(datum, data['high']),
						'low': _normalize(datum, data['low']),
						'close': _normalize(datum, data['close']),
						'adjclose': _normalize(datum, data['adjclose'])
					}[price_type]
				)

		fig.update_layout(
			height=600,
			xaxis_rangeslider_visible=False,
			hovermode='x', showlegend=True, template='seaborn'
		)
		self.container.plotly_chart(
			figure_or_data=fig, use_container_width=True
		)
