"""Price page"""
import components
import template

import datetime as dt
import pandas as pd
import plotly.graph_objs as go
import streamlit as st

from data import SymbolData


class Price(template.Page):
	"""Options page"""

	@staticmethod
	def _example_chart_slider(prices: pd.DataFrame):
		# ----------------------------------------------------------------------
		# Chart
		# ----------------------------------------------------------------------
		fig = go.Figure()
		fig.add_trace(go.Line(
			x=prices.index, y=prices.close
		))
		fig.update_layout(
			xaxis=dict(
				rangeselector=dict(
					buttons=list([
						dict(
							count=1,
							label="1m",
							step="month",
							stepmode="backward"
						),
						dict(
							count=6,
							label="6m",
							step="month",
							stepmode="backward"),
						dict(
							count=1,
							label="YTD",
							step="year",
							stepmode="todate"),
						dict(
							count=1,
							label="1y",
							step="year",
							stepmode="backward"
						),
						dict(step="all")
					])
				),
				rangeslider=dict(
					visible=True
				),
				type="date"
			)
		)
		'''
		[
			"plotly", 
			"plotly_white", 
			"plotly_dark", 
			"ggplot2", 
			"seaborn", 
			"simple_white", 
			"none"
		]
		'''
		fig.update_layout(
			template='plotly_dark'
		)
		st.plotly_chart(figure_or_data=fig, use_container_width=True)

	@staticmethod
	def _create_chart(container: st.container, prices: pd.DataFrame):
		fig = go.Figure()
		fig.add_trace(go.Line(
			x=prices.index, y=prices.close
		))
		container.plotly_chart(fig, use_container_width=True)

	def _example_chart_st_controls(self, symbol: str):
		# ----------------------------------------------------------------------
		# Extract data
		# ----------------------------------------------------------------------
		symbol_data: SymbolData = self.STATE.symbols_data[symbol]
		prices = symbol_data.historical_prices
		self._example_chart_slider(prices)
		min_date = min(prices.index)
		max_date = max(prices.index)
		container = st.expander('Chart', expanded=True)
		date_select_method = container.radio(
			'Date Range Selection',
			options=[
				'Select a time period',
				'Manually select a date range'
			]
		)
		if date_select_method == 'Manually select a date range':
			selected_dates = container.slider(
				label='Select a date range',
				min_value=min_date,
				max_value=max_date,
				value=(min_date, max_date)
			)
		else:
			selected_period = container.selectbox(
				'Or select a time period',
				options=[
					'all data',
					'last 10 years',
					'last 5 years',
					'last 1 year',
					'last 6 months',
					'last 3 months',
					'last 1 month',
					'last week'
			])
			timedeltas = {
				'last 10 years': dt.timedelta(days=365*10),
				'last 5 years': dt.timedelta(days=365*5),
				'last 1 year': dt.timedelta(days=365),
				'last 6 months': dt.timedelta(days=int(365*(1/12)*6)),
				'last 3 months': dt.timedelta(days=int(365*(1/12)*3)),
				'last 1 month': dt.timedelta(days=int(365*(1/12)*1)),
				'last week': dt.timedelta(days=7)
			}
			selected_dates = [
				min_date if selected_period == 'all data'
				else max_date - timedeltas[selected_period],
				max_date
			]
		filtered_dates = [
			x for x in prices.index
			if (x >= min(selected_dates)) and (x <= max(selected_dates))
		]
		filtered_prices = prices.loc[filtered_dates]
		self._create_chart(container, filtered_prices)

	def _create_ts_chart(self) -> components.TimeSeriesChart:
		return components.TimeSeriesChart(
			st.expander('Chart', expanded=True), self.symbols, pd.concat({
					x: self.STATE.symbols_data[x].historical_prices
					for x in self.symbols
				},
				keys=self.symbols
		))

	def _single_symbol(self, symbol: str):
		chart = self._create_ts_chart()

	def _multi_symbols(self, symbols: list):
		chart = self._create_ts_chart()
