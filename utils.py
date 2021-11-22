"""Useful functions"""
import math
import streamlit as st
from typing import List


def signify(n, unit_type: str = 'bytes'):
	"""Human readable number to largest significance.
	Kinda stole this from stackoverflow.
	"""
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


def get_all_attributes(attrs: List[str], STATE: st.session_state) -> List[list]:
	"""Get all values of certain attributes of all symbols in session"""
	return [
		sorted(list({getattr(s, attr) for s in STATE.symbols_data.values()}))
		for attr in attrs
	]
