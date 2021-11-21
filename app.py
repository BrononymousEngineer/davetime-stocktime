"""Try to come up with a method of using streamlit components in the same way
as I did with dash.
"""
import components
import data
import utils
import template
import sys

import streamlit as st

st.set_page_config(
	page_title="Stock Research",
	page_icon='📊',
	layout='wide',
	initial_sidebar_state='expanded',
	menu_items={'About': 'All data comes from Yahoo! Finance.'}
)

# Initialize session state
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


PAGES = {
	'Overview': template.Page,
	'Fundamental': template.Page,
	'Price Data': template.Page,
	'Analysts': template.Page,
	'Options': template.Page,
	'Portfolio Analysis': template.Page
}


def main() -> None:
	"""run app"""
	sidebar = st.sidebar
	sidebar.markdown('''
	⬇️ Scroll down for more options, mouse over/tap the ❔ icons for help
	''')
	new_symbols = components.FormTextInput(
		form_key='new_symbols_form',
		container=sidebar,
		title='Symbols Input',
		text_input_description='Or enter ticker symbols below',
		uploader_description='Upload a text file',
		uploader_help_txt='File must be .txt format (if you are using ' +
				'Windows, this means open up Notepad...for Mac, TextEdit) ' +
				'and type only one symbol per line. After uploading the file, ' +
				'click the "Add symbols" button and data from Yahoo! Finance ' +
				'will be retrieved. This is not case sensitive. Aapl, aapl, ' +
				'and AaPL will all be read as AAPL.',
		submit_button_text='Add symbols to session',
		text_input_help_txt='Type symbols into the box below, ' +
				'separating each with a space, like this: AAPL AMZN GOOG. ' +
				'Click the button and data from Yahoo! Finance will be ' +
				'retrieved. This is not case sensitive. Aapl, aapl, and AaPL ' +
				'will all be read as AAPL.'
	)
	if new_symbols.parsed_input:
		data.get_data(
			sorted(new_symbols.parsed_input),
			new_symbols.progressbar_container,
			new_symbols.progressmsg_container,
			STATE
		)
		STATE.asset_types = utils.get_all_attributes('asset_type', STATE)
		STATE.sectors = utils.get_all_attributes('sector', STATE)
		STATE.industries = utils.get_all_attributes('industry', STATE)
	check_all = sidebar.checkbox('Select All Symbols')
	selected_symbols_container = sidebar.empty()
	default_symbols = []
	if check_all:
		default_symbols = STATE.symbols
	else:
		selected_asset_type = sidebar.multiselect(
			'Filter by asset type', options=STATE.asset_types
		)
		default_asset_type = []
		if selected_asset_type:
			for a in selected_asset_type:
				for s in STATE.symbols:
					if getattr(STATE.symbols_data[s], 'asset_type') == a:
						default_asset_type.append(s)
		selected_sector = sidebar.multiselect(
			'Filter by sector', options=STATE.sectors
		)
		default_sector = []
		if selected_sector:
			for a in selected_sector:
				for s in STATE.symbols:
					if getattr(STATE.symbols_data[s], 'sector') == a:
						default_sector.append(s)
		selected_industry = sidebar.multiselect(
			'Filter by industry', options=STATE.industries
		)
		default_industry = []
		if selected_industry:
			for a in selected_industry:
				for s in STATE.symbols:
					if getattr(STATE.symbols_data[s], 'industry') == a:
						default_industry.append(s)
		if default_asset_type:
			default_symbols = default_asset_type
		if default_sector:
			default_symbols = sorted(list(
				set(default_symbols).intersection(default_sector)
			))
		if default_industry:
			default_symbols = sorted(list(
				set(default_symbols).intersection(default_industry)
			))
	selected_symbols = selected_symbols_container.multiselect(
		'Select symbols to view', options=STATE.symbols, default=default_symbols
	)

	selected_page = sidebar.radio('Selected Page', options=PAGES.keys())
	sidebar.markdown('''
	##### {} symbols in session using {} of RAM
	'''.format(
		len(STATE.symbols_data),
		utils.signify(sum([
			sys.getsizeof(x) for x in STATE.symbols_data.values()
		])))
	)
	st.markdown('''
	# IN PROGRESS
		
		- the sidebar mostly works
		- the filtering system is currently being worked on
		- then pages will be created
		
	### Session State
	''')
	st.write(STATE)
	PAGES[selected_page](selected_symbols, STATE).runpage()


if __name__ == '__main__':
	main()
