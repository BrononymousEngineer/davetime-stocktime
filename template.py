"""Page template

Usage
-----
import template
import streamlit as st


class ExamplePage(template.Page):

	def _single_symbol(self, symbol: str):
		# your code here

	def _multi_symbols(self, symbols: list):
		# your code here


"""
import utils

from abc import abstractmethod
import streamlit as st


class Page:
	"""Page template"""

	def __init__(self, symbols: list, STATE: st.session_state):
		self.symbols = symbols
		self.STATE = STATE
		self.data = utils.concat_obj_data(STATE.symbols_data)

	@abstractmethod
	def _single_symbol(self, symbol: str):
		"""Run a single or multi symbol page"""
		raise NotImplementedError(
			'need to implement ' +
			'_single_symbol(self, symbol: str) in class: {}'.format(
				self.__class__.__name__
			))

	@abstractmethod
	def _multi_symbols(self, symbols: list):
		"""Run a single or multi symbol page"""
		raise NotImplementedError(
			'need to implement ' +
			'_multi_symbols(self, symbols: list) in class: {}'.format(
				self.__class__.__name__
			))

	def runpage(self, STATE: st.session_state):
		"""Display the page"""
		try:
			if len(self.symbols) == 1:
				self._single_symbol(self.symbols[0])
			elif len(self.symbols) > 1:
				self._multi_symbols(self.symbols)
			else:
				st.markdown('''
					### Page not finished   
					TODO
					- make filters more general/modular
						- let the user add/create filter criteria
					- fix data errors for currencies & futures
					- "clear all" filter button
					- try to find a way to make data load FASTER (caching)
				''')
				if st.checkbox('Show session state'):
					st.markdown('''### Session State''')
					st.write(STATE)
		except Exception as e:
			st.markdown('''
				### Page not finished   
				TODO
				- make filters more general/modular
					- let the user add/create filter criteria
				- fix data errors for currencies & futures
				- "clear all" filter button
				- try to find a way to make data load FASTER (caching)
			''')
			if st.checkbox('Show session state'):
				st.markdown('''### Session State''')
				st.write(STATE)
			st.error(e)
