"""Price page"""
import components
import template
import utils

import pandas as pd
import streamlit as st


class Price(template.Page):
	"""Price page"""

	def _create_ts_chart(self) -> components.TimeSeriesChart:
		return components.TimeSeriesChart(
			st.expander('Chart', expanded=True), self.symbols, self.data
		)

	def _single_symbol(self, symbol: str):
		chart = self._create_ts_chart()

	def _multi_symbols(self, symbols: list):
		chart = self._create_ts_chart()
