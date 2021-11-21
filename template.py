"""Page template"""
import data
from abc import abstractmethod
import streamlit as st


class Page:
	"""Page template"""

	def __init__(self, symbols: list, STATE: st.session_state):
		self.symbols = symbols

	@abstractmethod
	def _single_symbol(self, symbol: str):
		"""Run a single or multi symbol page"""
		raise NotImplementedError(
			'implement _single_symbol(self, symbol: str) in class: {}'.format(
				self.__class__.__name__
			)
		)

	@abstractmethod
	def _multi_symbols(self, symbols: list):
		"""Run a single or multi symbol page"""
		raise NotImplementedError(
			'implement _multi_symbols(self, symbols: list) in class: {}'.format(
				self.__class__.__name__
			)
		)

	def runpage(self):
		"""Display the page"""
		if len(self.symbols) == 1:
			self._single_symbol(self.symbols[0])
		else:
			self._multi_symbols(self.symbols)
