"""Handle data"""
import datetime as dt
import pandas as pd
import streamlit as st
import yahooquery as yq

from numpy import nan

PLACEHOLDERS = {
	str: '<no data>',
	int: nan,
	float: nan,
	list: [],
	dict: {}
}


class SymbolData:
	"""Stores data about a ticker symbol."""
	asof_raw: dt.datetime
	asof: str
	symbol: str
	sector: str
	industry: str
	asset_type: str
	country: str
	short_name: str
	long_name: str
	option_chain: pd.DataFrame
	historical_prices: pd.DataFrame

	def __init__(self, symbol: str):
		now = dt.datetime.now()
		date = dt.datetime.strftime(now, '%Y-%m-%d')
		time = dt.datetime.strftime(now, '%I:%m %p').strip('0')
		self.asof_raw = now
		self.asof = f'{date} {time}'
		self.symbol = symbol
		self.ticker_obj = yq.Ticker(symbol)

	def __repr__(self):
		return f'SymbolData({self.symbol})'

	def get_metadata(self) -> None:
		"""Overview"""
		# YQ ENDPOINTS
		asset_profile = self.ticker_obj.asset_profile[self.symbol]
		quote_type = self.ticker_obj.quote_type[self.symbol]
		# EXTRACT DATA FROM ENDPOINTS
		self.sector = asset_profile.get(
			'sector', PLACEHOLDERS[str]
		)
		self.industry = asset_profile.get(
			'industry', PLACEHOLDERS[str]
		)
		self.country = asset_profile.get(
			'country', PLACEHOLDERS[str]
		)
		self.asset_type = quote_type.get('quoteType', PLACEHOLDERS[str])
		self.short_name = quote_type.get('shortName', PLACEHOLDERS[str])
		self.long_name = quote_type.get('longName', PLACEHOLDERS[str])

	def get_fundamental_data(self) -> None:
		"""Fundamental data"""
		pass

	def get_historical_prices(self) -> None:
		"""Historical price data"""
		self.historical_prices = self.ticker_obj.history(
			period='max'
		).loc[self.symbol]

	def get_analyst_data(self) -> None:
		"""Analyst info"""
		pass

	def get_option_chain(self) -> None:
		"""Option chain"""
		self.option_chain = self.ticker_obj.option_chain.loc[self.symbol]


def get_data(
	symbols: list,
	p_cont: st.container,
	m_cont: st.container,
	STATE: st.session_state
) -> list:
	"""Create all Symbol objects and add to the session"""
	symbols = sorted([
		x for x in yq.Ticker(symbols, validate=True).symbols
		if x not in STATE.symbols_data.keys()
	])

	if not symbols:
		return symbols

	def _update_progress(n: int):
		for x in range(1, n + 1):
			yield x / n

	def update_progress(msg: str):
		"""Update the progress bar"""
		info_container.text(msg)
		progress.progress(next(progress_vals))

	successful = []
	info_container = m_cont.empty()
	progress_cont = p_cont.empty()
	progress_vals = _update_progress(5*len(symbols))
	progress = progress_cont.progress(0)
	for s in symbols:
		symbol_obj = SymbolData(s)
		failed = False
		try:
			update_progress(f'Getting {s} metadata')
			symbol_obj.get_metadata()
			update_progress(f'Getting {s} fundamentals')
			symbol_obj.get_fundamental_data()
			update_progress(f'Getting {s} price history')
			symbol_obj.get_historical_prices()
			update_progress(f'Getting {s} analyst info')
			symbol_obj.get_analyst_data()
			update_progress(f'Getting {s} option chain')
			symbol_obj.get_option_chain()
			# successful.append(s)
		except Exception as e:
			failed = True
			print(f'getdata err {s}: {e}')

		if not failed:
			STATE.symbols.append(s)
			STATE.symbols_data[s] = symbol_obj

	info_container.empty()
	progress_cont.empty()

	STATE.symbols = sorted(STATE.symbols)
	STATE.symbols_data = {
		k: STATE.symbols_data[k]
		for k in sorted(list(STATE.symbols_data.keys()))
	}

	# return successful
