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
	sidebar.markdown('''
	##### Start here in the sidebar, from the top down.  
	##### Mouse over (tap on mobile) any ❔ icons for help
	''')
	# --------------------------------------------------------------------------
	# Symbols input/get data
	# --------------------------------------------------------------------------
	input_container = sidebar.expander('Symbols Input')
	input_container.markdown('''
	There are currently two ways to load data.  
	
	1) Upload a text file of symbols  
	2) Manually type symbols  
	
	A third option will be crawling through related symbols on Yahoo
	''')
	new_symbols = components.SymbolsInput(
		form_key='new_symbols_form',
		container=input_container,
		# title='Symbols Input',
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
			and AaPL will all be read as AAPL.'''
	)
	if new_symbols.parsed_input:
		data.get_data(
			sorted(new_symbols.parsed_input),
			# new_symbols.progressbar_container,
			input_container,
			new_symbols.progressmsg_container,
			STATE
		)
		# EXTRACT METADATA FOR FILTERING
		STATE.asset_types, STATE.sectors, STATE.industries, STATE.countries = \
		utils.get_all_attributes([
			'asset_type', 'sector', 'industry', 'country'
		], STATE)
	# --------------------------------------------------------------------------
	# Symbols filter
	# --------------------------------------------------------------------------
	filter_container = sidebar.expander('Symbols Filter')
	select_all = sidebar.checkbox('Select All Symbols')

	selected_symbols_container = sidebar.empty()

	default_symbols = []
	if select_all:
		default_symbols = STATE.symbols
	else:
		if STATE.sectors and STATE.industries:
			sector_industry_structure = {
				'radio': ['Sectors', 'Industries'],
				'Sectors': STATE.sectors,
				'Industries': STATE.industries
			}
			default_symbols = components.SymbolsFilter(
				filter_container,
				sector_industry_structure,
				description='Filter by sector/industry'
			).output

	selected_symbols = selected_symbols_container.multiselect(
		'Select symbols to view', options=STATE.symbols, default=default_symbols
	)
	# --------------------------------------------------------------------------
	# Run selected page
	# --------------------------------------------------------------------------
	selected_page = sidebar.radio('Selected Page', options=PAGES.keys())
	# --------------------------------------------------------------------------
	# Tail info
	# --------------------------------------------------------------------------
	sidebar.markdown('''
	##### {} symbols in session using {} of RAM
	'''.format(
		len(STATE.symbols_data),
		utils.signify(sum([
			sys.getsizeof(x) for x in STATE.symbols_data.values()
		])))
	)
	# --------------------------------------------------------------------------
	# Temporary dev info
	# --------------------------------------------------------------------------
	st.markdown('''
	# DEV INFO
	
	For now this page only displays useful information for development.
		
		- symbols input works, except for Yahoo crawler
		- filtering not yet implemented
		- pages not yet implemented
		
	### Session State
	''')
	st.write(STATE)
	if selected_page != 'Options':
		st.markdown('''
		### Ignore the error below
		''')
	PAGES[selected_page](selected_symbols, STATE).runpage()


if __name__ == '__main__':
	main()
