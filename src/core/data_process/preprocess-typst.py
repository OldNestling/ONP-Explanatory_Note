# Copyright © 2026 OldNestling
# License: GPLv3 (GNU General Public License Version 3)

import re, subprocess, time
from bs4 import BeautifulSoup
from pathlib import Path

# --------------------------------------- Очистка от Align ----------------------------------------

def find_matching(text, start, open_ch, close_ch):
	"""Возвращает индекс закрывающей скобки, соответствующей открывающей на позиции start."""
	count = 0
	i = start
	while i < len(text):
		ch = text[i]
		if ch == open_ch:
			count += 1
		elif ch == close_ch:
			count -= 1
			if count == 0:
				return i
		i += 1
	return -1

def remove_align_blocks(text):
	"""
	Удаляет все вызовы #?align(...)[...] и, при необходимости, внешние скобки.
	- align(...)[...] -> [...]
	- [ #align(...)[...] ] -> [...]   (внешние скобки убираются)
	- #align(...)[...] без внешних скобок -> [...]
	"""
	pattern = re.compile(r'(?<![A-Za-z])(#?)align\s*\(')
	
	while True:
		m = pattern.search(text)
		if not m:
			break
		
		has_hash = bool(m.group(1))   # есть ли решётка
		start_align = m.start()	   # начало слова align или #align
		open_paren = m.end() - 1	  # позиция '('
		close_paren = find_matching(text, open_paren, '(', ')')
		if close_paren == -1:
			break
		
		# Ищем открывающую '[' после закрывающей ')'
		i = close_paren + 1
		while i < len(text) and text[i] in ' \t\n\r':
			i += 1
		if i >= len(text) or text[i] != '[':
			break
		open_bracket = i
		close_bracket = find_matching(text, open_bracket, '[', ']')
		if close_bracket == -1:
			break
		
		# Содержимое аргумента align (включая сами квадратные скобки)
		inner_content = text[open_bracket:close_bracket + 1]   # например, '[*Месяцы*]'
		
		# Если есть решётка, пробуем найти внешние скобки
		if has_hash:
			# Ищем '[' перед start_align, пропуская пробелы и переносы
			j = start_align - 1
			while j >= 0 and text[j] in ' \t\n\r':
				j -= 1
			if j >= 0 and text[j] == '[':
				outer_open = j
				outer_close = find_matching(text, outer_open, '[', ']')
				if outer_close != -1 and outer_close > close_bracket:
					# Проверяем, что внутри внешних скобок только этот вызов align
					# (между outer_open и start_align, и между close_bracket и outer_close — только пробелы)
					prefix = text[outer_open + 1:start_align].strip()
					suffix = text[close_bracket + 1:outer_close].strip()
					if prefix == '' and suffix == '':
						# Заменяем всё от outer_open до outer_close на inner_content
						text = text[:outer_open] + inner_content + text[outer_close + 1:]
						continue   # начинаем сначала, так как структура изменилась
		
		# Если решётки нет или внешних скобок нет/они не подходят
		# Заменяем только сам вызов align (от start_align до close_bracket) на inner_content
		text = text[:start_align] + inner_content + text[close_bracket + 1:]
	
	return text

# ------------------------------------- Получение имени таблиц ------------------------------------

def get_table_name(text):
	""" Вычленяет имя таблицы из строки с параметром """
	
	text = text[:text.find('//')]
	text = text.replace('[','',1)
	text = text[::-1].replace(']','',1).replace(',','',1)
	text = text[::-1]
	_, name = text.split(':', 1)
	name = name.strip()
	return name.strip('"')

def get_all_table_names(document: str):
	""" Проходит по всем таблицам и собирает их имена """
	lines = document.split('\n')

	in_table = False
	level = 0
	tables_names = []

	for line in lines:
		if line.startswith('#таблица('):
			in_table = True
			level += 1
		if 'наименование:' in line and in_table:
			tables_names.append(get_table_name(line))
			in_table = False
	return tables_names


# =================================================================================================
   
if __name__ == "__main__":
	FILE = Path(r'/home/oldnestling/Документы/01_STORAGE/01_Работа/04_Материалы/02_Технологии_и_программы/08_Typst_и_ПЗ/Typst. Пояснительные записки/Том_1_ПЗ.typ')
	ROOT = FILE.parent
	OUTPUT = 'output.html'

	# Чтение файла
	with open(FILE, "r", encoding="utf-8") as f:
		original = f.read()
	
	processed: str = remove_align_blocks(original)
	
	# очистка от декаративного переноса строк
	processed = processed.replace(' \\ ', ' ')
	processed = processed.replace('\\ ', ' ')
	
	tables_names = get_all_table_names(processed)

	# Запускаем процесс typst compile, передавая текст через stdin
	proc = subprocess.Popen(
		[
			"typst", "compile",
			"--root", ROOT,
			"--features", "html", "--pretty", "-", OUTPUT
		],
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		encoding='utf-8'
	)

	stdout, stderr = proc.communicate(input=processed)

	if proc.returncode != 0:
		print("Ошибка компиляции:", stderr)
	else:
		print("HTML успешно создан")

	time.sleep(1)

	# Загружаем HTML
	with open(OUTPUT, 'r', encoding='utf-8') as f:
		clear_file = []
		for line in f:
			clear_file.append(line.replace('<strong>','').replace('</strong>',''))
		soup = BeautifulSoup(''.join(clear_file), 'html.parser')

	# Ищем все таблицы
	for idx, table in enumerate(soup.find_all('table')):
		# Создаём новый тег <figure>
		figure = soup.new_tag('figure')
		figure['type'] = 'table'

		# Обёртываем таблицу: метод .wrap() помещает figure вокруг table,
		table.wrap(figure)

		# Добавляем <figcaption>
		caption = soup.new_tag('figcaption')
		caption.string = f'Таблица {idx+1} — {tables_names[idx]}'
		figure.insert(0, caption)

	# Маркируем блоки с изображениями и переносим подписи внутрь
	for figure in soup.find_all('figure'):
		if figure.get('type') != 'table':
			figure['type'] = 'image'

			figcaption = soup.new_tag('figcaption')
			par = figure.find('p')
			div = figure.find('div')

			figcaption.string = par.text
			figure.append(figcaption)

			par.decompose()
			div.decompose()


	# Сохраняем результат
	with open(OUTPUT, 'w', encoding='utf-8') as f:
		f.write(str(soup))
		# f.write(soup.prettify())