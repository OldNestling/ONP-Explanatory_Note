# Copyright © 2026 OldNestling
# License: GPLv3 (GNU General Public License Version 3)

import xml.etree.ElementTree as ET
import re

from ..support.utilities import get_report


#----------------------------------------------------------------------------------------
#======================================== Данные ======================================== 
#	Паттерн наименования атрибутов:
#	o_... — obligatory (обязательный параметр)
#	n_... — not obligatory (не обязательный параметр)

#	Дополнительные символы паттерна:
#	.a_... — атрибут
#	.m_... — many (множественный элемент)
#	.c_... — choice (выбор одного из нескольних элементов)
#----------------------------------------------------------------------------------------

#										Адреса
#----------------------------------------------------------------------------------------
class RussianAddress:
	""" Адрес на территории Российской Федерации """
	def __init__(self):
		self.o_RegionCode = '27'		# Код субъекта Российской Федерации
		self.n_PostIndex = None	 		# Почтовый индекс
		self.o_OKTMOCode = ''			# Код муниципального образования по ОКТМО
		self.o_OKTMOName = ''			# Наименование муниципального образования по ОКТМО
		self.oc_formal_address: dict = {
			'n_District': None,			# Район
			'n_City': 'Хабаровск',		# Город
			'n_Settlement': None,		# Населенный пункт
			'n_Street': 'Ленинградская',# Улица
			'n_Building': '28/5',		# Номер здания/сооружения
			'n_Room': 'офис 417',		# Номер помещения
			'n_Landmark': None			# Ориентир (неформализованное описание)
		}
		self.oc_Note = None

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент

		:parent: `RussianAddress` | `RussianPostAddress`
		"""	

		ET.SubElement(parent, 'RegionCode').text = self.o_RegionCode

		if self.n_PostIndex:
			ET.SubElement(parent, 'PostIndex').text = self.n_PostIndex

		ET.SubElement(parent, 'OKTMOCode').text = self.o_OKTMOCode
		ET.SubElement(parent, 'OKTMOName').text = self.o_OKTMOName
		
		if self.oc_Note:
			ET.SubElement(parent, 'Note').text = self.oc_Note
		else:
			n_District = self.oc_formal_address.get('n_District')
			n_City = self.oc_formal_address.get('n_City')
			n_Settlement = self.oc_formal_address.get('n_Settlement')
			n_Street = self.oc_formal_address.get('n_Street')
			n_Building = self.oc_formal_address.get('n_Building')
			n_Room = self.oc_formal_address.get('n_Room')
			n_Landmark = self.oc_formal_address.get('n_Landmark')
			if n_District:
				ET.SubElement(parent, 'District').text = n_District
			if n_City:
				ET.SubElement(parent, 'City').text = n_City
			if n_Settlement:
				ET.SubElement(parent, 'Settlement').text = n_Settlement
			if n_Street:
				ET.SubElement(parent, 'Street').text = n_Street
			if n_Building:
				ET.SubElement(parent, 'Building').text = n_Building
			if n_Room:
				ET.SubElement(parent, 'Room').text = n_Room
			if n_Landmark:
				ET.SubElement(parent, 'Landmark').text = n_Landmark

class ForeignAddress:
	""" Адрес за пределами территории Российской Федерации """
	def __init__(self):
		self.o_Country: str = ''	# Страна
		self.o_Note: str = ''		# Неформализованное описание адреса

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет элемент `ForeignAddress` внутри переданного контейнера

		:parent: `ForeignAddress` 
		"""
		ET.SubElement(parent, 'Country').text = self.o_Country
		ET.SubElement(parent, 'Note').text = self.o_Note


#			Организации, предприниматели и лица, учасвствующие в разработке ПД
#----------------------------------------------------------------------------------------
class Organization:
	""" Юридическое лицо, включение которого в реестр НОПРИЗ обязательное/ необязательно, но возможно """

	NOPRIZ_PATTERN = r'[ПИ]-\d{3}-\d{12}-\d{4}|\(Не требуется\)'

	def __init__(self, necessary_NOPRIZ = 'none'):
		""" :necessary_NOPRIZ: `required` | `option` | `none` Включение в реестр НОПРИЗ  """
		self.necessary_NOPRIZ = necessary_NOPRIZ # required | option | none

		# Полное наименование
		self.o_FullName: str ='ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ПРИМПРОЕКТ"'	
		self.n_AbbreviatedName: str = "ПримПроект"			# Сокращенное наименование
		self.o_number = {
			'OGRN': '1122721000302',	# Основной государственный регистрационный номер
			'RAFP': None	# Номер записи аккредитации Реестра аккредитованных филиалов, \
							# представительств иностранных юридических лиц
		}
		self.o_INN: str = '2721189934'						# Индивидуальный номер налогоплательщика
		self.o_KPP: str = '272101001'  						# Код причины постановки на учет
		self.o_Address: RussianAddress | ForeignAddress = RussianAddress()
		self.n_Email: str = 'adm@primproekt.ru'				# Адрес электронной почты
		self.a_NOPRIZNumber: str = ''						# Реестровый номер СРО
		self.is_developer = False							# Является застройщиком
		self.is_technical_customer = False					# Является техн. заказчиком
	
	def __str__(self):
		return self.n_AbbreviatedName if self.n_AbbreviatedName else self.o_FullName

	def write_xml(self,  parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `Organization`
		"""
		global reports

		match self.necessary_NOPRIZ:
			case 'required' | 'option':
				if re.fullmatch(self.NOPRIZ_PATTERN, self.a_NOPRIZNumber):
					parent.set('NOPRIZNumber', self.a_NOPRIZNumber)
				elif self.necessary_NOPRIZ == 'option' and not self.a_NOPRIZNumber:
					pass									# не был указан
				else:
					get_report(self, f'Номер НОПРИЗ {self.a_NOPRIZNumber} не соответствует паттерну')

		ET.SubElement(parent, 'FullName').text = self.o_FullName
		if self.n_AbbreviatedName:
			ET.SubElement(parent, 'AbbreviatedName').text = self.n_AbbreviatedName
		ET.SubElement(parent, 'OGRN').text = self.o_number['OGRN']
		ET.SubElement(parent, 'INN').text = self.o_INN
		ET.SubElement(parent, 'KPP').text = self.o_KPP
		addres = ET.SubElement(parent, 'Address')
		self.o_Address.write_xml(addres)
		if self.n_Email:
			ET.SubElement(parent, 'Email').text = self.n_Email


class AbstractPerson:
	""" Физическое лицо, должностное лицо, лицо, участвовавшее в разработке 
	проектной документации и/или отчетов о результатах инженерных изысканий """
	def __init__(self):
		self.o_Surname: str = '' 	# Фамилия
		self.o_Name: str = ''		# Имя
		self.t_Patronymic: str = ''	# Отчество
	
	def __str__(self):
		return f'{self.o_Surname} {self.o_Name} {self.t_Patronymic}'
	
	def write_xml(self,  parent: ET.Element):
		ET.SubElement(parent, 'Surname').text = self.o_Surname
		ET.SubElement(parent, 'Name').text = self.o_Name
		if self.t_Patronymic:
			ET.SubElement(parent, 'Patronymic').text = self.t_Patronymic


class IndividualEntrepreneur(AbstractPerson):
	""" Индивидуальный предприниматель, включение которого 
	в реестр НОПРИЗ обязательное / необязательное """

	NOPRIZ_PATTERN = r'[ПИ]-\d{3}-\d{12}-\d{4}|\(Не требуется\)'

	def __init__(self, necessary_NOPRIZ = 'none'):
		""" :necessary_NOPRIZ: `required` | `option` | `none` Включение в реестр НОПРИЗ  """
		super().__init__()
		self.necessary_NOPRIZ = necessary_NOPRIZ

		self.o_OGRNIP: str = ''	# Основной государственный регистрационный номер
		self.n_INN: str = ''	# Индивидуальный номер налогоплательщика

		# Почтовый адрес в пределах территории Российской Федерации /
		# Почтовый адрес за пределами территории Российской Федерации
		self.oc_PostAddress: RussianAddress | ForeignAddress = RussianAddress()

		self.n_Email: str = ''	# Адрес электронной почты
		self.a_NOPRIZNumber: str = ''
		self.is_developer = False							# Является застройщиком
		self.is_technical_customer = False					# Является техн. заказчиком
	
	def __str__(self):
		return self.o_Surname 
	
	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `IP`
		"""
		super().write_xml(parent)

		global reports
		match self.necessary_NOPRIZ:
			case 'required' | 'option':
				if re.fullmatch(self.NOPRIZ_PATTERN, self.a_NOPRIZNumber):
					parent.set('NOPRIZNumber', self.a_NOPRIZNumber)
				elif self.necessary_NOPRIZ == 'option' and not self.a_NOPRIZNumber:
					pass									# не был указан
				else:
					get_report(self, f'Номер НОПРИЗ {self.a_NOPRIZNumber} не соответствует паттерну')

		ET.SubElement(parent, 'OGRNIP').text = self.o_OGRNIP
		if self.n_INN:
			ET.SubElement(parent, 'INN').text = self.n_INN

		tPostAddress = ET.SubElement(parent, 'PostAddress')
		if isinstance(self.oc_PostAddress, RussianAddress):
			address = ET.SubElement(tPostAddress, 'RussianPostAddress')
		else:
			address = ET.SubElement(tPostAddress, 'ForeignAddress')
		self.oc_PostAddress.write_xml(address)

		if self.n_Email:
			ET.SubElement(parent, 'Email').text = self.n_Email
			

class EngineerPerson(AbstractPerson):
	"""
	Лицо, принимавшие участие в разработке проектной документации 
	и/или отчета о результатах инженерных изысканий 
	(обязательное включение в Национальный реестр специалистов НОПРИЗ)/
	(включение в Национальный реестр специалистов НОПРИЗ не требуется, но возможно)
	"""
	NOPRIZ_PATTERN = r'(П|ПИ|И)-\d{6}|(Не требуется)'
	SNILS_PATTERN = r'[0-9]{3}-[0-9]{3}-[0-9]{3} [0-9]{2}'

	def __init__(self, necessary_NOPRIZ = 'option'):
		""" :necessary_NOPRIZ: `required` | `option` | `none` Включение в реестр НОПРИЗ  """
		super().__init__()
		self.necessary_NOPRIZ = necessary_NOPRIZ
		self.o_SNILS: str =  ''			# Страховой номер индивидуального лицевого счёта
		self.o_n_NOPRIZNumber: str = ''	# Идентификационный номер в Национальном реестре специалистов НОПРИЗ
		self.n_Email: str = ''			# Адрес электронной почты
		self.oa_role: str = 'Разработка'	# 1. "Разработка"; 2. "Нормоконтроль"; 3. "Согласование"
	
	def __str__(self):
		return super().__str__()
	
	@property
	def check_NOPRIZ(self):
		return bool(re.fullmatch(self.NOPRIZ_PATTERN, self.o_n_NOPRIZNumber))
	
	@property
	def check_SNILS(self):
		return bool(re.fullmatch(self.SNILS_PATTERN, self.o_SNILS))
	
	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: 
		- tEngineerPersonNOPRIZ: `ChiefProjectEngineer` | `ChiefProjectArchitect` | `ChiefProjectEngineerSurvey`
		- tEngineerPersonNoNOPRIZ: `DocParticipant` | `Signer`
		"""	
		super().write_xml(parent)

		parent.set('role', self.oa_role)

		if self.check_SNILS:
			ET.SubElement(parent, 'SNILS').text = self.o_SNILS
		else:
			get_report(f'EngineerPerson {self}', f'Номер СНИЛС {self.o_SNILS} не соответствует паттерну')

		match self.necessary_NOPRIZ:
			case 'required' | 'option':
				if self.check_NOPRIZ:
					ET.SubElement(parent, 'NOPRIZNumber').text = self.o_n_NOPRIZNumber
				elif self.necessary_NOPRIZ == 'option' and not self.o_n_NOPRIZNumber:
					pass									# не был указан
				else:
					get_report(
						f'EngineerPerson {self}', 
						f'Номер НОПРИЗ {self.o_n_NOPRIZNumber} не соответствует паттерну'
					)
		
		if self.n_Email:
			ET.SubElement(parent, 'Email').text = self.n_Email
		

class PersonSNILS(AbstractPerson):
	""" Физическое лицо (обязательное указание СНИЛС) """
	SNILS_PATTERN = r'[0-9]{3}-[0-9]{3}-[0-9]{3} [0-9]{2}'

	def __init__(self):
		super().__init__()
		self.o_SNILS: str =  ''		# Страховой номер индивидуального лицевого счёта

		# Почтовый адрес
		self.oc_PostAddress: RussianAddress | ForeignAddress = RussianAddress()

		self.n_Email: str = ''				# Адрес электронной почты
		self.is_developer = True			# Является застройщиком

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `Developer`
		"""
		super().write_xml(parent)

		if re.fullmatch(self.SNILS_PATTERN, self.o_SNILS):
			ET.SubElement(parent, 'SNILS').text = self.o_SNILS
		else:
			get_report(f'EngineerPerson {self}', f'Номер СНИЛС {self.o_SNILS} не соответствует паттерну')

		tPostAddress = ET.SubElement(parent, 'PostAddress')
		if isinstance(self.oc_PostAddress, RussianAddress):
			tag = 'RussianPostAddress'
		else:
			tag = 'ForeignAddress'
		address = ET.SubElement(tPostAddress, tag)
		self.oc_PostAddress.write_xml(address)

		if self.n_Email:
			ET.SubElement(parent, 'Email').text = self.n_Email