# Copyright © 2026 OldNestling
# License: GPLv3 (GNU General Public License Version 3)

from pathlib import Path 
from bs4 import BeautifulSoup, Tag

#from core.xml_data import Table, Cell

FILE = Path(r'output.html')

FILE_DATA = None

with open(FILE, 'r', encoding='utf-8') as f:
	FILE_DATA = f.read()

soup = BeautifulSoup(FILE_DATA, 'html.parser')

# Читает содержание из навигации
def get_content_list(data: BeautifulSoup):
	content_list = []
	navigation = data.find('nav')
	for le in navigation.find_all('li'):
		le = le.find('span').find('a')
		href = le.get('href')
		content_list.append(str(href))
	return content_list

def get_chapter_by_tag(data: BeautifulSoup, chapter_tag) -> list[Tag]:
	"""
	Получает срез дерева по разделу из данных HTML-файла на основе переданного тега,
	соответствующего свойствующего свойству `href` (включая сам заголовок),
	удаляет элементы из исходного массива
	### Args:
		- :data: данные HTML файла
		- :chapter_tag: тег раздела, принятый в системе для структуры ПЗ
	"""
	if not data:
		return
	# получаем заголовок с заранее не известным уровнем по переданному тегу href
	headers = ', '.join([f'h{i}#{chapter_tag}' for i in range(1, 7)])
	header = data.select_one(headers)
	if not header:
		return []

	# получаем все последующие элементы, пока не встретим заголовок того же уровня
	# 1) сначала собираем соседей (пока связи живы)
	siblings = list(header.find_next_siblings())
	# 2) извлекаем сам заголовок
	results = [header.extract()]
	# 3) проходим по заранее собранному списку
	try:
		level = int(header.name[1])
		for sib in siblings:
			if sib.name.startswith('h') and int(sib.name[1]) == level:
				break
			print(sib.name)
			results.append(sib.extract())
	except IndexError:
		results = []

	return results


def process_table_element(main_element: Tag) -> dict | None:
	""" Разворачивает дерево элемента `figure` у которого type='table' 
	и преобразует под шаблон xml-схемы для класса Table (tTable by ExplanatoryNote 1.07)
	### Args:
		- :main_element: элемент `<figure>`
 	"""
	figcaption = main_element.find('figcaption')
	table_name = figcaption.get_text(strip=True) if figcaption else None
	table = main_element.find('table')

	if not table:
		return 

	output = {
		'name': table_name,
		'thead': [],
		'tbody': []
	}

	def parse_rows(rows: list[Tag]) -> list[list[str]]:
		"""Преобразует список <tr> в матрицу с маркерами объединения."""
		if not rows:
			return []

		matrix = []

		for row_idx, row in enumerate(rows):
			# добавляем строки по мере необходимости
			while len(matrix) <= row_idx:
				matrix.append([])

			col = 0	# курсор по столбцам внутри текущей строки
			# recursive=False — чтобы не захватить ячейки из вложенных таблиц
			# Typst не генерирует таких ситуаций, но на всякий случай
			for cell in row.find_all(['th', 'td'], recursive=False):
				# пропускаем ячейки, занятые rowspan/colspan из предыдущих строк
				while col < len(matrix[row_idx]) and matrix[row_idx][col] is not None:
					col += 1
				# если курсор ушёл дальше текущей длины row — доращиваем 
				while len(matrix[row_idx]) <= col:
					matrix[row_idx].append(None)

				matrix[row_idx][col] = cell.get_text(strip=True)

				try:
					rowspan = int(cell.get('rowspan', 1))
				except (ValueError, TypeError):
					rowspan = 1
				try:
					colspan = int(cell.get('colspan', 1))
				except (ValueError, TypeError):
					colspan = 1

				# rowspan равный 0 объединяет все дальнейшие строки
				if rowspan == 0:
					rowspan = len(rows) - row_idx
				if colspan == 0:
					colspan = 1

				# Помечаем ВСЕ ячейки, которые покрыты объединением
				for r in range(rowspan):
					for c in range(colspan):
						# сама ячейка с данными, её пропускаем
						if r == 0 and c == 0:
							continue

						tr = row_idx + r
						tc = col + c

						# доращиваем матрицу 
						while len(matrix) <= tr:
							matrix.append([])
						while len(matrix[tr]) <= tc:
							matrix[tr].append(None)

						if matrix[tr][tc] is None:
							# '^' — вертикальное объединение, '<' — горизонтальное
							matrix[tr][tc] = '^' if r > 0 else '<'

				col += 1

		# None заменяем на пустую строку
		for row in matrix:
			for i, val in enumerate(row):
				if val is None:
					row[i] = ''

		return matrix

	thead = table.find('thead')
	if thead:
		output['thead'] = parse_rows(thead.find_all('tr', recursive=False))

	tbody_elements = table.find_all('tbody', recursive=False)
	if tbody_elements:
		body_rows = []
		for tb in tbody_elements:
			body_rows.extend(tb.find_all('tr', recursive=False))
		output['tbody'] = parse_rows(body_rows)
	else:
		# Если <tbody> нет, берём строки, лежащие прямо в <table>
		# реалезовано на всякий случай
		output['tbody'] = parse_rows(table.find_all('tr', recursive=False))

	return output