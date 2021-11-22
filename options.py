"""Options page"""
import template
import streamlit as st


class Options(template.Page):
	"""Options page"""

	def _single_symbol(self, symbol: str):
		st.markdown('''
		Eventually 
		[Options3D](https://github.com/BrononymousEngineer/options3d) will be 
		migrated to this page.
		''')

	def _multi_symbols(self, symbols: list):
		self._single_symbol(symbols[0] if symbols else symbols)
