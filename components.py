"""Components built around streamlit widgets"""
import streamlit as st


class SymbolsInput:
	"""Form containing a text_input box and a button."""

	def __init__(
			self,
			form_key: str,
			container: st.container,
			title: str = None,
			title_importance: int = 1,
			text_input_description: str = None,
			text_input_help_txt: str = None,
			text_input_separator: str = ' ',  # can delete
			uploader_description: str = None,
			uploader_help_txt: str = None,
			uploader_separator: str = '\\n',  # can delete
			submit_button_text: str = None,
			submit_button_clears: bool = True,
			parsed_case: str = 'upper'
	):
		self.form = container.form(
			key=form_key, clear_on_submit=submit_button_clears
		)
		self.title = None if not title else self.form.markdown(
			f'{"#"*title_importance} {title}'
		)
		self.uploader = self.form.file_uploader(
			label=uploader_description if uploader_description else '',
			help=uploader_help_txt if uploader_help_txt else ''
		)
		self.text_input = self.form.text_input(
			label=text_input_description if text_input_description else '',
			help=text_input_help_txt if text_input_help_txt else ''
		)
		self.button = self.form.form_submit_button(
			submit_button_text if submit_button_text else ''
		)
		self.progressbar_container = self.form.empty()
		self.progressmsg_container = self.form.empty()
		sep = text_input_separator
		case = {
			True: lambda x: x,
			False: lambda x: exec(f'''
			raise ValueError('case must be "upper" or "lower", not "{x}"')
			''')
		}[parsed_case in ['upper', 'lower']](parsed_case)
		self.parsed_input = [
			x for x in self.__parse_text_input(self.text_input, case, sep)
			if x != ''
		] or self.__parse_text_file()

	@staticmethod
	def __parse_text_input(text_input: st.text_input, c: str, s: str) -> list:
		return eval(f'sorted(list(set(text_input.{c}().split("{s}".{c}()))))')

	def __parse_text_file(self) -> list:
		uploader = self.uploader
		if uploader:
			return [
				x.strip(' ') for x in
				uploader.getvalue().decode('utf-8').upper().split()
			]


class SymbolsFilter:
	"""Component with radio buttons and a dropdown."""
	def __init__(
		self,
		container: st.container,
		struct: dict,
		description: str = ''
	):
		self.radio = container.radio(description, struct['radio'])
		st.write(struct)
		self.dropdown = container.multiselect(
			f'Select {self.radio}', options=struct[self.radio]
		)
		self.output = []
