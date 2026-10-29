# Copyright © 2026 OldNestling
# License: GPLv3 (GNU General Public License Version 3)

import re, zlib
from pathlib import Path

#								Вспомогательные функции
#----------------------------------------------------------------------------------------

reports = []
""" Список ошибок в процессе формирования XML """

def check_date(text):
	pattern = r'\d\d\d\d\-\d\d\-\d\d'
	if not isinstance(text, str):
		return False
	matched = re.fullmatch(pattern, text)
	return bool(matched)

def get_report(block: str, text: str):
	""" Создаёт отчёт о ошибке 
	### Args:
		:block: Наименования процесса в коде
		:text: Сообщение о проблеме
	"""
	global reports
	warning = f'[WARNING: {block}] {text}'
	print(warning)
	reports.append(warning)

def get_CRC32_checksum(filepath: Path):
	""" Получает контрольную сумму файла по алгоритму CRC32-IEEE длиной 8 символов"""
	if not isinstance(filepath, Path):
		return 'None'
	if not filepath.exists():
		return 'Нет файла'
	crc = 0
	with open(filepath, 'rb') as f:
		# Читаем блоками по 8 КБ, чтобы не нагружать память
		while chunk := f.read(8192):
			crc = zlib.crc32(chunk, crc)
	# Маскируем старшие биты (на случай отрицательного значения) и форматируем в 8 заглавных шестнадцатеричных цифр
	return f"{(crc & 0xFFFFFFFF):08X}"