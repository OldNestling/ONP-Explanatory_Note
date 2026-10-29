# Copyright © 2026 OldNestling
# License: GPLv3 (GNU General Public License Version 3)

import xml.etree.ElementTree as ET
import re, zlib
from datetime import datetime, timezone
from pathlib import Path
from lib.tDocumentType import tDocumentType 
from lib.tEngineeringSurveyDocumentType import tEngineeringSurveyDocumentType
from lib.tOKEI import tOKEI

from ..support.utilities import get_report, check_date
from .People_and_Orgs import Organization
from .Data import TextBlock, Modification
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


class BudgetSource:
	tBudgetLevel = (
		'Федеральный бюджет', 'Бюджет субъекта Российской Федерации', 'Местный бюджет',
		'Бюджет государственного внебюджетного фонда Российской Федерации',
		'Бюджет территориального государственного внебюджетного фонда'
	)
	def __init__(self):
		self.oc_BudgetLevel: str = 'Федеральный бюджет'	# Уровень бюджета по tBudgetLevel
		self.n_SourceRatio: float | None = None			# Размер финансирования (доля в процентах)

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `BudgetSource`
		"""
		if self.oc_BudgetLevel in self.tBudgetLevel:
			ET.SubElement(parent, 'BudgetLevel').text = self.oc_BudgetLevel
			if self.n_SourceRatio:
				ET.SubElement(parent, 'SourceRatio').text = str(self.n_SourceRatio)
		else:
			get_report('tFinanceSources [tBudgetSource]', 'невалидный уровень бюджета')
		
class StateCustomerSource(Organization):
	""" Сведения об источнике финансирования 
	(Средства ЮЛ, перечисленных в части 2 статьи 8.3 ГК РФ) """
	def __init__(self, necessary_NOPRIZ='none'):
		super().__init__(necessary_NOPRIZ)				# Юридическое лицо, владелец средств
		self.n_SourceRatio: float | None = None			# Размер финансирования (доля в процентах)

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `StateCustomerSource`
		"""
		tOrganization = ET.SubElement(parent, 'Owner')
		super().write_xml(tOrganization)
		if self.n_SourceRatio:
			ET.SubElement(parent, 'SourceRatio').text = str(self.n_SourceRatio)


class FinanceSources:
	""" Сведения об источниках финансирования объекта капитального строительства """
	def __init__(self):
		# Сведения об источнике финансирования (Бюджетные средства)
		self.om_sources: list[BudgetSource, StateCustomerSource, str] = []

		# Комментарий к сведениям об источниках финансирования
		self.n_FinanceComment: str | None = None	
	
	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `FinanceSources`
		"""
		for source in self.om_sources:
			tag = None
			match source:
				case BudgetSource():
					tag = 'BudgetSource'
				case StateCustomerSource():
					tag = 'StateCustomerSource'
				case str():
					tag = 'PrivateSource'
				case _:
					get_report('tFinanceSources', 'невалидный тип данных')
					continue
			element = ET.SubElement(parent, tag)
			source.write_xml(element)
		
		if self.n_FinanceComment:
			ET.SubElement(parent, 'FinanceComment').text = self.n_FinanceComment


class NationalProject:
	"""
	Сведения о включении ОКС в Национальный проект
	Сведения о включении ОКС в Региональный проект в составе Федерального проекта
	"""
	def __init__(self):
		self.o_Title_NP: str = ''			# Наименование Национального проекта
		self.o_Title_FP: str = ''			# Наименование Федерального проекта
		self.n_Title_RP: str | None = ''	# Наименование Регионального проекта

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `NationalProject`
		"""
		ET.SubElement(parent, 'Title').text = self.o_Title_NP
		tFederalProject = ET.SubElement(parent, 'FederalProject')
		ET.SubElement(tFederalProject, 'Title').text = self.o_Title_FP
		if self.n_Title_RP:
			tRegionalProject = ET.SubElement(tFederalProject, 'RegionalProject')
			ET.SubElement(tRegionalProject, 'Title').text = self.n_Title_RP


class Functions:
	""" Функциональное назначение объекта капитального строительства и сведения о составе, 
	характеристиках и номенклатуре выпускаемой продукции """
	def __init__(self):
		self.n_FunctionsNote: str = ''	# Функциональное назначение ОКС
		self.o_FunctionsClass: str = ''	# Функциональное назначение ОКС по классификатору

		# Общие сведения о составе и характеристике производства, номенклатуре продукции
		self.n_ProductsNote: TextBlock | None = None

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `Functions`
		"""
		if self.n_FunctionsNote:
			ET.SubElement(parent, 'FunctionsNote').text = self.n_FunctionsNote

		ET.SubElement(parent, 'FunctionsClass').text = self.o_FunctionsClass
		
		if self.n_ProductsNote:
			tTextBlock = ET.SubElement(parent, 'ProductsNote')
			self.n_ProductsNote.write_xml(tTextBlock)

class TEI:
	""" Технико-экономический показатель (показатель мощности) и его значение """
	def __init__(self):
		self.o_Name: str = ''		# Наименование показателя
		self.oc_Measure: str = '-' 	# Единица измерения показателя (код по ОКЕИ)
		self.o_Value: str = '0'		# Значение показателя

		# Предыдущее значение показателя (при реконструкции)
		self.n_OldValue: str | None = None

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `PowerIndicator` | `TEI`
		"""
		ET.SubElement(parent, 'Name').text = self.o_Name

		if self.oc_Measure in tOKEI:
			ET.SubElement(parent, 'Measure').text = self.oc_Measure
		else:
			get_report(f'tTEI -> {parent.tag}', 'Код не валиден')

		if self.n_OldValue:
			ET.SubElement(parent, 'OldValue').text = self.n_OldValue

class ClimateConditions:
	""" Сведения о климатической, географической и инженерно-геологической характеристике района, 
	на территории которого предполагается осуществлять строительство, реконструкцию или 
	капитальный ремонт объекта капитального строительства """

	CLIMATE_DISTRICTS = (
		'I', 'IА', 'IБ', 'IВ', 'IГ', 'IД', 'II', 'IIА', 'IIБ', 'IIВ', 'IIГ', 
		'III', 'IIIА', 'IIIБ', 'IIIВ', 'IV', 'IVА', 'IVБ', 'IVВ', 'IVГ'
	)

	GEO_CONDITIONS = ('I', 'II', 'III')

	def __init__(self):
		self.o_ClimateNote: TextBlock = TextBlock()	# Общие сведения
		
		# Возможность опасных природных процессов и явлений и техногенных воздействий на территории
		self.o_DangerousNatureProcesses: TextBlock = TextBlock()

		self.nm_ClimateDistrict: list[str] | str | None = None # Климатический район, подрайон

		# Категория сложности инженерно-геологических условий
		self.nm_GeologicalConditions: list[str] | str | None = None

		# Категория сложности инженерно-геокриологических условий
		self.nm_GeocryologicalConditions: list[str] | str | None = None

		self.nm_WindDistrict: list[str] | str | None = None	# Ветровой район
		
		self.nm_SnowDistrict: list[str] | str | None = None	# Снеговой район

		# Интенсивность сейсмических воздействий
		self.nm_SeismicActivity: list[int] | int | None = None
	
	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `ClimateConditions`
		"""
		# ---------- Общие сведения ----------
		if isinstance(self.o_ClimateNote, TextBlock()):
			element_CN = ET.SubElement(parent, 'ClimateNote')
			self.o_ClimateNote.write_xml(element_CN)
		else:
			get_report('ClimateNote', 'Не соответствует классу TextBlock')

		# ---------- Возможность опасных  процессов и явлений ----------
		if isinstance(self.o_DangerousNatureProcesses, TextBlock()):
			element_DNP = ET.SubElement(parent, 'DangerousNatureProcesses')
			self.o_DangerousNatureProcesses.write_xml(element_DNP)
		else:
			get_report('DangerousNatureProcesses', 'Не соответствует классу TextBlock')

		# ---------- Климатический район ----------
		def __process_element(value, name, collection: list | tuple):
			if value in collection:
				ET.SubElement(parent, name).text = value
			else:
				get_report(name, 'Не валидный номер')

		if isinstance(self.nm_ClimateDistrict, str):
			self.nm_ClimateDistrict = list(self.nm_ClimateDistrict)
		
		if self.nm_ClimateDistrict:
			for cd in self.nm_ClimateDistrict:
				__process_element(cd, 'ClimateDistrict', self.CLIMATE_DISTRICTS)

		# ---------- Категория сложности инженерно-геологических условий ----------
		if isinstance(self.nm_GeologicalConditions, str):
			self.nm_GeologicalConditions = list(self.nm_GeologicalConditions)

		if self.nm_GeologicalConditions:
			for gc in self.nm_GeologicalConditions:
				__process_element(gc, 'GeologicalConditions', self.GEO_CONDITIONS)

		# ---------- Категория сложности инженерно-геокриологических условий ----------
		if isinstance(self.nm_GeocryologicalConditions, str):
			self.nm_GeocryologicalConditions = list(self.nm_GeocryologicalConditions)

		if self.nm_GeocryologicalConditions:
			for gc in self.nm_GeocryologicalConditions:
				__process_element(gc, 'GeocryologicalConditions', self.GEO_CONDITIONS)
		
		# ---------- Ветровой район ----------
		if isinstance(self.nm_WindDistrict, str):
			self.nm_WindDistrict = list(self.nm_WindDistrict)
		
		if self.nm_WindDistrict:
			COLLECTION = ('Iа', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII')
			for wd in self.nm_WindDistrict:
				__process_element(wd, 'WindDistrict', COLLECTION)

		# ---------- Снеговой район ----------
		if isinstance(self.nm_SnowDistrict, str):
			self.nm_SnowDistrict = list(self.nm_SnowDistrict)
		
		if self.nm_SnowDistrict:
			COLLECTION = ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII')
			for sd in self.nm_SnowDistrict:
				__process_element(sd, 'SnowDistrict', COLLECTION)

		# ---------- Интенсивность сейсмических воздействий ----------
		match self.nm_SeismicActivity:
			case int():
				self.nm_SeismicActivity = list(self.nm_SeismicActivity)
			case None:
				self.nm_SeismicActivity = []
			
			case str():
				try:
					self.nm_SeismicActivity = list(int(self.nm_SeismicActivity))
				except Exception:
					get_report('SeismicActivity', 'значение должно быть целочисленным')

		if self.nm_SeismicActivity:
			COLLECTION = (5, 6, 7, 8, 9, 10)
			for sa in self.nm_SeismicActivity:
				__process_element(sa, 'SeismicActivity', COLLECTION)

class Route:
	""" Описание варианта маршрута прохождения линейного объекта по территории района строительства """
	def __init__(self):
		self.o_Name: str = ''	# Наименование или идентификатор варианта маршрута
		self.n_Note: TextBlock | None = None # Описание варианта маршрута 

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		:parent: `Route`
		"""
		ET.SubElement(parent, 'Name').text = self.o_Name

		if self.n_Note is not None:
			note = ET.SubElement(parent, 'NOte')
			self.n_Note.write_xml(note)

class Routes:
	""" 
	Описание вариантов маршрутов прохождения линейного объекта по территории района строительства
	(реконструкции), обоснование выбранного варианта трассы
	"""
	def __init__(self):
		self.o_RoutesNote: TextBlock = TextBlock()
		self.nm_Route: list[Route] = []

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		:parent: `Routes`
		"""
		routes_note = ET.SubElement(parent, 'RoutesNote')
		self.o_RoutesNote.write_xml(routes_note)

		for route in self.nm_Route:
			route_el = ET.SubElement(parent, 'Route')
			route.write_xml(route_el)



class Resources:
	""" Сведения о необходимых ресурсах, сырьевой базе """
	def __init__(self):
		# Общие сведения о необходимых ресурсах, сырьевой базе
		self.n_Note: TextBlock | None =  None

		# Сведения о необходимом ресурсе (сырье)	{Name: str, Measure: str, Value: str}
		self.nm_Resource: list[dict] = []


	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		:parent: `Resources`
		"""
		if self.n_Note:
			self.n_Note.write_xml(parent)

		for res in self.nm_Resource:
			if not isinstance(res, dict):
				continue
			resource = ET.SubElement(parent, 'Resource')

			# Наименование необходимого ресурса
			name = res.get('Name', '')
			if not name:
				get_report('Resources', f'не валидное значение параметра {name=}' )
			else:
				ET.SubElement(resource, 'Name').text = name

			# Единица измерения
			measure = res.get('Measure', '')
			if measure not in tOKEI:
				get_report('Resources', f'не валидное значение параметра {measure=}' )
			else:
				ET.SubElement(resource, 'Measure').text = measure

			# Необходимый объем ресурса
			value = res.get('Value', '')
			if not value:
				get_report('Resources', f'не валидное значение параметра {value=}' )
			else:
				ET.SubElement(resource, 'Value').text = value


class LandInfo:
	"""
	Сведения о земельных участках, изымаемых для государственных или муниципальных нужд, 
	о земельных участках, в отношении которых устанавливается сервитут, публичный сервитут, 
	обоснование их размеров, если такие размеры не установлены нормами отвода земель для 
	конкретных видов деятельности, или правилами землепользования и застройки, или проектами 
	планировки, проектами межевания территории, - при необходимости изъятия земельного участка 
	для государственных или муниципальных нужд, установления сервитута, публичного сервитута
	"""
	def __init__(self):
		self.o_CommonLandInfo: TextBlock = TextBlock()	# Общие сведения о земельных участках

		# Описание земельного участка
		# {CadastralNumber: str, LandCategory: int, UsingNote: str}
		self.nm_LandAreaInfo: list[dict] | None = None	

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		:parent: `LandInfo`
		"""
		tTextBlock = ET.SubElement(parent, 'CommonLandInfo')
		self.o_CommonLandInfo.write_xml(tTextBlock)

		value_range = tuple(range(1, 8))
		for descript in self.nm_LandAreaInfo:
			num = descript.get('CadastralNumber')
			category = descript.get('LandCategory')
			note = descript.get('UsingNote')

			if not num or category not in value_range or not note:
				get_report(
					'LandAreaInfo', 
					f'Не валидные значения:\n \t{num=},\t{category=},\t{note=}'
				)
			else:
				tLandAreaInfo = ET.SubElement(parent, 'LandAreaInfo')
				ET.SubElement(tLandAreaInfo, 'CadastralNumber').text = num
				ET.SubElement(tLandAreaInfo, 'LandCategory').text = category
				ET.SubElement(tLandAreaInfo, 'UsingNote').text = note


class SoftwareUsed:
	""" Описание используемых программных продуктов """
	def __init__(self):
		self.n_SoftwareNote: TextBlock | None = None	# Общие сведения об используемых программных пр.

		# Name: str				(Наименование программного продукта)
		# Version: str | None 	(Версия программного продукта)
		# UsingNote: str		(Сведения при подготовки каких расчетов или какой части ПД)
		self.nm_Software: list[dict]	# Описание программного продукта

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		:parent: `SoftwareUsed`
		"""
		if self.n_SoftwareNote:
			self.n_SoftwareNote.write_xml(parent)

		for soft in self.nm_Software:
			name = soft.get('Name')
			vers = soft.get('Version')
			note = soft.get('UsingNote')

			if not name or not note:
				get_report(
					'SoftwareUsed -> Software',
					f'Не валидные значения\n\t{name=}\n\t{note=}'
				)
			else:
				element = ET.SubElement(parent, 'Software')
				ET.SubElement(element, 'Name').text = name
				if vers: ET.SubElement(element, 'Version').text = vers
				ET.SubElement(element, 'UsingNote').text = note


class StagesInfo:
	""" 
	Обоснование возможности осуществления строительства, реконструкции ОКС по этапам строительства,
	реконструкции с выделением этих этапов
	"""
	def __init__(self):
		self.o_ReasonNote: TextBlock = TextBlock()
		self.nm_Stage: list[dict[
			'Number': str, 				# Номер или наименование этапа [обязательный]
			'ConstructionDuration': float,	# Продолжительность работ этапа, месяц [обязательный]
			'BeginDate': str,			# Дата начала этапа (ISO) [не обязательный]
			'EndDate': str,				# Дата окончания этапа (ISO) [не обязательный]
			'OperationDate': str,		# Дата ввода в эксплуатацию (ISO) (при наличии) [не обязательный]
			'Note': TextBlock			# Дополнительные сведения об этапе [обязательный]
		]]	= []

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		:parent: `StagesInfo`
		"""
		element = ET.SubElement(parent, 'ReasonNote')
		self.o_ReasonNote.write_xml(element)

		def __date_process(parent: ET.Element, element_name, date):
			if date and check_date(date):
				ET.SubElement(parent, element_name).text = date
			elif date:
				get_report('StagesInfo -> Stage', f'Дата {date=} не соответствует формату ISO')
			else:
				pass

		for stage in self.nm_Stage:
			number = stage.get('Number')
			duration = stage.get('ConstructionDuration')
			begin = stage.get('BeginDate')
			end = stage.get('EndDate')
			operation = stage.get('OperationDate')
			note: TextBlock = stage.get('Note')

			if not number or not (isinstance(duration, float) and duration > 0) or not note:
				get_report(
					'StagesInfo -> Stage',
					f'Параметры не валидны:\n\t{number=},\n\t{duration=}\n\t{note=}'
				)
				continue

			tStage = ET.SubElement(parent, 'Stage')
			ET.SubElement(tStage, 'Number').text = number
			ET.SubElement(tStage, 'ConstructionDuration').text = str(duration)

			__date_process(tStage, 'BeginDate', begin)
			__date_process(tStage, 'EndDate', end)
			__date_process(tStage, 'OperationDate', operation)

			note_element = ET.SubElement(tStage, 'Note')
			note.write_xml(note_element)


class GasNetworksFeatures:
	""" Дополнительные требования к пояснительной записке в соответствии с Приложением 10 к
	Положению о составе разделов проектной документации и требованиях к их содержанию
	(в отношении сетей газораспределения и (или) газопотребления давлением до 1,2 МПа включительно) """
	def __init__(self):
		# Расчет трубопроводов на прочность и устойчивость
		self.o_StrengthCalculation: TextBlock = TextBlock()

		# Перечень мероприятий по охране окружающей среды
		self.o_EnvironmentalProtection: TextBlock = TextBlock()

		# Перечень мероприятий по обеспечению пожарной безопасности
		self.o_FireSafety: TextBlock = TextBlock()

		# Перечень мероприятий по безопасной эксплуатации линейного объекта
		self.o_OperationalSafety: TextBlock = TextBlock()

		# Нормативная периодичность выполнения работ по капитальному ремонту линейного объекта
		self.o_RepairFrequency: TextBlock = TextBlock()
	
	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		:parent: `GasNetworksFeatures`
		"""
		tStrengthCalculation = ET.SubElement(parent, 'StrengthCalculation')
		self.o_StrengthCalculation.write_xml(tStrengthCalculation)

		tEnvironmentalProtection = ET.SubElement(parent, 'EnvironmentalProtection')
		self.o_EnvironmentalProtection.write_xml(tEnvironmentalProtection)

		tFireSafety = ET.SubElement(parent, 'FireSafety')
		self.o_FireSafety.write_xml(tFireSafety)

		tOperationalSafety = ET.SubElement(parent, 'OperationalSafety')
		self.o_OperationalSafety.write_xml(tOperationalSafety)

		tRepairFrequency = ET.SubElement(parent, 'RepairFrequency')
		self.o_RepairFrequency.write_xml(tRepairFrequency)