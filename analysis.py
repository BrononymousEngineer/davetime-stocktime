"""Analysis page"""
import pandas as pd

import components
import template

import streamlit as st


class Analysis(template.Page):
	"""Analysis page"""

	def _weight_grid(self, max_cols: int = 8) -> dict:
		num_symbols = len(self.symbols)
		max_cols = max_cols if num_symbols >= max_cols else num_symbols
		weights = {}
		i = 0
		cols = None
		for s in self.symbols:
			cols = st.columns(max_cols) if i == 0 else cols
			weights[s] = cols[i].number_input(s, step=0.1)
			i += 1 if i < max_cols - 1 else -(max_cols - 1)
		return {s: w for s, w in weights.items() if w != 0}

	@staticmethod
	def _build_portfolio(weights: dict, data: pd.DataFrame):
		data = data.loc[weights.keys()]
		data_dict = {}
		returns = None
		for s in weights.keys():
			df = data.loc[s]
			wret = (
					df['adjclose'] / df['adjclose'].shift(1) - 1
			).fillna(0)*weights[s]
			if returns is None:
				returns = wret
			else:
				returns = returns.add(wret, fill_value=0)
			# df['wret'] = wret
			# data_dict[s] = df

		# data = pd.concat(
		# 	{k: v for k, v in data_dict.items()}, keys=data_dict.keys()
		# )[['adjclose', 'wret']]
		# st.write(data)
		# st.write((1 + returns).cumprod())
		return (1 + returns).cumprod()

	def _single_symbol(self, symbol: str):
		pass

	def _multi_symbols(self, symbols: list):
		st.markdown('''### Weights''')
		weights = self._weight_grid(max_cols=6)
		chart = components.TimeSeriesChart(
			st,
			self.symbols,
			self.data,
			plot_type_controls=False,
			price_type_controls=False
		)
		chart.add_line(self._build_portfolio(weights, chart.data))
