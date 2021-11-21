"""Useful functions"""
import math
import streamlit as st


def signify(n, unit_type: str = 'bytes'):
	"""Human readable number to largest significance"""
	SIGNIFICANCE = {
		'money': ['', 'k', 'M', 'B', 'T'],
		'bytes': [' bytes', 'kB', 'MB', 'GB', 'TB']
	}[unit_type]
	try:
		n = float(n)
	except TypeError:
		return n
	significance = max(
		0,
		min(
			len(SIGNIFICANCE) - 1,
			int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
		)
	)
	return '{}{:.1f}{}'.format(
		'$' if unit_type == 'money' else '',
		n / 10 ** (3 * significance),
		SIGNIFICANCE[significance]
	)


def get_all_attributes(attr_type: str, STATE: st.session_state) -> list:
	"""Get all values of a certain attribute of the symbol objects in session"""
	types = ['sector', 'industry', 'asset_type']
	if attr_type not in types:
		raise ValueError(f'attr_type "{attr_type}" not in {types}')
	return sorted(list(set([
		getattr(STATE.symbols_data[s], attr_type) for s in STATE.symbols
	])))
