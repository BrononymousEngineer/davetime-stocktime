"""Options page"""
import template
import streamlit as st

class Options(template.Page):

	def _multi_symbols(self, symbols: list):
		st.markdown('''
		Eventually [Options3D](https://options3d.herokuapp.com/) will be
		migrated to this page.
		
		The github is 
		[here](https://github.com/BrononymousEngineer/options3d).
		''')
