"""Components built around streamlit widgets"""
import streamlit as st
from copy import deepcopy
from typing import Dict


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
		input_objects: Dict[str, object] = None,
		title: str = None,
		title_importance: int = 4,
		radio_description: str = '',
		radio_options: dict = None,
		filter_type: bool = True
	):
		self.output = []
		if title:
			container.markdown(f'''{"#"*title_importance} {title}''')
		if radio_options:
			radio = container.radio(
				radio_description,
				options=[x for x in radio_options.keys()],
				format_func=lambda x: radio_options[x]
			)
			options = sorted(list({
					getattr(x, radio) for x in input_objects.values()
			}))
			filter_by = container.multiselect(
				f'{radio_options[radio]} selection:',
				options=options,
				default={
					'Any': [],
					'All': [] if len(options) > 1 else options,
					'Exclude': []
				}[filter_type]
			)
			self.output = {
				'Any': self._filter_any,
				'All': self._filter_all,
				'Exclude': self._filter_exclude
			}[filter_type](input_objects, radio, filter_by)

	@staticmethod
	def _filter_any(
		input_objects: Dict[str, object], attr: str, filter_by: list
	) -> list:
		out = []
		for k, v in input_objects.items():
			if getattr(v, attr) in filter_by:
				out.append(k)
		return out

	@staticmethod
	def _filter_all(
		input_objects: Dict[str, object], attr: str, filter_by: list
	) -> list:
		out = deepcopy(input_objects)
		for k, v in input_objects.items():
			if getattr(v, attr) not in filter_by:
				del out[k]
		return list(out.keys())

	@staticmethod
	def _filter_exclude(
		input_objects: Dict[str, object], attr: str, filter_by
	) -> list:
		out = deepcopy(input_objects)
		for k, v in input_objects.items():
			if getattr(v, attr) in filter_by:
				del out[k]
		return list(out.keys())
