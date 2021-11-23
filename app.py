"""Main app"""
import components
import data
import options
import utils
import template
import sys

import streamlit as st

# ------------------------------------------------------------------------------
# Set page configuration
# ------------------------------------------------------------------------------
st.set_page_config(
	page_title="Stocks",
	page_icon='📊',
	layout='wide',
	initial_sidebar_state='expanded',
	menu_items={'About': 'All data comes from Yahoo! Finance.'}
)

# ------------------------------------------------------------------------------
# Initialize session state
# ------------------------------------------------------------------------------
STATE: st.session_state = st.session_state
if not hasattr(STATE, 'symbols'):
	STATE.symbols = []
if not hasattr(STATE, 'symbols_data'):
	STATE.symbols_data = {}
if not hasattr(STATE, 'sectors'):
	STATE.sectors = []
if not hasattr(STATE, 'industries'):
	STATE.industries = []
if not hasattr(STATE, 'asset_types'):
	STATE.asset_types = []

# ------------------------------------------------------------------------------
# Initialize pages
# ------------------------------------------------------------------------------
PAGES = {
	'Overview': template.Page,
	'Fundamental': template.Page,
	'Price Data': template.Page,
	'Analysts': template.Page,
	'Options': options.Options,
	'Portfolio Analysis': template.Page
}


def main() -> None:
	"""run app"""
	# --------------------------------------------------------------------------
	# Initialize sidebar
	# --------------------------------------------------------------------------
	sidebar = st.sidebar
	# --------------------------------------------------------------------------
	# Container setup
	# --------------------------------------------------------------------------
	info_container = sidebar.empty()
	input_container = sidebar.expander(
		'Symbols Input', expanded=False if STATE.symbols else True
	)
	filter_container = sidebar.expander(
		'Symbols Filter', expanded=True if STATE.symbols else False
	)
	filter_info_container = filter_container.empty()
	selected_symbols_container = sidebar.container()
	# --------------------------------------------------------------------------
	# Static text
	# --------------------------------------------------------------------------
	input_container.markdown('''
	There are 3 ways to load data.  
	##### 1) Upload a text file of symbols  
	##### 2) Manually type symbols  
	''')
	input_container.error('''###### 3) Yahoo! Finance crawler (not added yet)''')
	filter_container.error('''
	Filters are not currently linked. This means the filtered symbols will meet
	**any** of the filter criteria, not **all** criteria.
	''')
	input_container.markdown('''
	You can also come back here to add more symbols at any point.
	''')
	# --------------------------------------------------------------------------
	# Symbols input/get data
	# --------------------------------------------------------------------------
	if not STATE.symbols:
		info_container.info('Input some symbols to get started')
		filter_info_container.info('Input some symbols to get started')
	new_symbols = components.SymbolsInput(
		form_key='new_symbols_form',
		container=input_container,
		text_input_description='2) Enter ticker symbols below',
		uploader_description='1) Upload a text file',
		uploader_help_txt=''' 
			File must be .txt format (if you are using Windows, this means open 
			up Notepad...for Mac, TextEdit) and type only one symbol per line. 
			After uploading the file, click the "Add symbols" button and data 
			from Yahoo! Finance will be retrieved. This is not case sensitive. 
			Aapl, aapl, and AaPL will all be read as AAPL.''',
		submit_button_text='Add symbols to session',
		text_input_help_txt=''' 
			Type symbols into the box below, separating each with a space, 
			like this: AAPL AMZN GOOG. Click the button and data from Yahoo! 
			Finance will be retrieved. This is not case sensitive. Aapl, aapl, 
			and AaPL will all be read as AAPL.''',
	)
	if new_symbols.parsed_input:
		data.get_data(
			sorted(new_symbols.parsed_input),
			input_container,
			new_symbols.progressmsg_container,
			STATE
		)
		info_container.empty()
		filter_info_container.empty()
	# --------------------------------------------------------------------------
	# Symbols filter
	# --------------------------------------------------------------------------
	select_all = filter_container.checkbox('Select All Symbols') \
		if STATE.symbols else False
	default_symbols = []
	if select_all:
		default_symbols = STATE.symbols
	else:
		for filter_group in [
			{'asset_type': 'Asset Type'},
			{'home_exchange': 'Exchange'},
			{
				'sector': 'Sector',
				'industry': 'Industry'
			},
			{
				'country': 'Country',
				'state': 'State',
				'city': 'City'
			}
		]:
			default_symbols += components.SymbolsFilter(
				container=filter_container,
				input_objects=STATE.symbols_data,
				radio_description='Filter by:',
				radio_options=filter_group
			).output
	selected_symbols = selected_symbols_container.multiselect(
		'Select symbols to view',
		options=STATE.symbols,
		default=default_symbols
	)
	# ----------------------------------------------------------------------
	# Get page to run
	# ----------------------------------------------------------------------
	selected_page = sidebar.radio('Selected Page', options=PAGES.keys())
	# ----------------------------------------------------------------------
	# Tail info
	# ----------------------------------------------------------------------
	sidebar.markdown('''
	##### {} symbols in session using {} of RAM
	'''.format(
		len(STATE.symbols_data),
		utils.signify(sum([
			sys.getsizeof(x) for x in STATE.symbols_data.values()
	]))))
	# ----------------------------------------------------------------------
	# Run selected page
	# ----------------------------------------------------------------------
	PAGES[selected_page](selected_symbols, STATE).runpage(STATE)


if __name__ == '__main__':
	main()
