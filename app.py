"""Main app"""
import analysis
import components
import data
import options
import price
import template

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

# ------------------------------------------------------------------------------
# Initialize pages
# ------------------------------------------------------------------------------
PAGES = {
	# 'Overview': template.Page,
	# 'Fundamental': template.Page,
	'Price Data': price.Price,
	# 'Analysts': template.Page,
	'Options': options.Options,
	'Portfolio Analysis': analysis.Analysis
}


def main() -> None:
	"""run app -- FYI this function is mainly sidebar setup"""
	# --------------------------------------------------------------------------
	# Initialize sidebar
	# --------------------------------------------------------------------------
	sidebar = st.sidebar
	# --------------------------------------------------------------------------
	# Container setup
	# --------------------------------------------------------------------------
	info_container = sidebar.empty()
	input_container = sidebar.expander('Symbols Input', expanded=False)
	filter_container = sidebar.expander('Symbols Filter', expanded=False)
	filter_info_container = filter_container.empty()
	selected_symbols_container = sidebar.container()
	# --------------------------------------------------------------------------
	# Static text
	# --------------------------------------------------------------------------

	# --------------------------------------------------------------------------
	# Symbols input/get data
	# --------------------------------------------------------------------------
	if not STATE.symbols_data:
		info_container.info('Input some symbols to get started')
		filter_info_container.info('Input some symbols to get started')
	new_symbols = components.SymbolsInput(
		form_key='new_symbols_form',
		container=input_container,
		text_input_description='Enter ticker symbols below',
		uploader_description='Upload a text file',
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
		if STATE.symbols_data else False

	if select_all:
		default_symbols = STATE.symbols_data.keys()
	else:
		filter_type = filter_container.radio(
			'Filter Type', options=['Any', 'All', 'Exclude'], help='''
			"Any" means that symbols will be selected which meet ***any*** of 
			the "Filter by:" criteria. 

			"All" means that symbols will be selected only if they meet 
			***all*** of the "Filter by:" criteria.

			"Exclude" means that all symbols will be selected that ***do not***
			meet the "Filter by:" criteria.   
		''')
		default_symbols = [] \
			if filter_type == 'Any' else list(STATE.symbols_data.keys())
		for filter_group in [
			{'asset_type': 'Asset Type'},
			{'home_exchange': 'Exchange'},
			{'sector': 'Sector', 'industry': 'Industry'},
			{'country': 'Country', 'state': 'State', 'city': 'City'}
		]:

			input_objects = STATE.symbols_data if filter_type == 'Any' else \
				{
					k: v for k, v in STATE.symbols_data.items()
					if k in default_symbols
				}

			symbol_group = components.SymbolsFilter(
				container=filter_container,
				input_objects=input_objects,
				radio_description='Filter by:',
				radio_options=filter_group,
				filter_type=filter_type
			).output

			if filter_type == 'Any':
				default_symbols += symbol_group
			else:
				default_symbols = symbol_group

	if default_symbols:
		selected_symbols_container.info('''
		Filters that have been set will not be updated if you manually 
		select/delete symbols from the current selection. This is being worked 
		on.
		''')
	selected_symbols = selected_symbols_container.multiselect(
		'Select symbols to view',
		options=STATE.symbols_data.keys(),
		default=default_symbols
	)
	sidebar.markdown(f'''
	##### {len(selected_symbols)} / {len(STATE.symbols_data)} symbols selected
	''')
	# --------------------------------------------------------------------------
	# Get page to run
	# --------------------------------------------------------------------------
	selected_page = sidebar.radio('Selected Page', options=PAGES.keys())
	# --------------------------------------------------------------------------
	# Run selected page
	# --------------------------------------------------------------------------
	PAGES[selected_page](selected_symbols, STATE).runpage(STATE)


if __name__ == '__main__':
	main()
