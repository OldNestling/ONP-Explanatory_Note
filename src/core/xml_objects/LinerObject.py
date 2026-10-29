# Copyright © 2026 OldNestling
# License: GPLv3 (GNU General Public License Version 3)

import xml.etree.ElementTree as ET
import re, zlib
from datetime import datetime, timezone
from pathlib import Path
from lib.tDocumentType import tDocumentType 
from lib.tEngineeringSurveyDocumentType import tEngineeringSurveyDocumentType
from lib.tOKEI import tOKEI

from .Object_Data import NationalProject, Functions, TEI, ClimateConditions, Resources, Routes, LandInfo, SoftwareUsed, StagesInfo, GasNetworksFeatures
from .People_and_Orgs import RussianAddress, ForeignAddress
from .Data import TextBlock, LinearProjectDocumentContent, Model
from ..support.utilities import get_report, check_date


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


#								Объект капитального строительства
#----------------------------------------------------------------------------------------

class LinearObject:
	""" Описание линейного объекта капитального строительства """
	def __init__(self):
		#	------ Атрибуты ------
		self.oa_ObjectID: str = '1'	# Идентификатор объекта (части объекта)
		self.oa_Placement: int[1 | 2] = 1 # Сведения о месте расположения ОКС
		self.oca_DangerousAndComplex: int = 0 # Сведения об отнесении ОКС к особо опасным и технически сложным
		self.oca_Unique: int = 0	# Сведения об отнесении объекта к уникальным объектам
		self.na_ElectronicBudgetObjectCode: str | None = None	# код ОКС в системе "Электронный бюджет"
		
		#	------ Элементы ------
		self.o_Name: str = '' 	# Наименование объекта капитального строительства

		# Сведения о включении ОКС в Гос. Проект
		self.n_NationalProject: NationalProject | None = None

		self.oc_ConstructionType: int = 3	# Вид работ, на который разрабатывается ПД
		self.n_ConstructionDuration: float | None = None # Продолжительность работ, месяц

		# Сведения о сроках строительства, вводе в эксплуатацию
		# {BeginDate: date, EndDate: date, OperationDate: date}
		self.n_ConstructionDates: dict | None = None	

		# Адрес начального пункта линейного объекта
		self.oc_Address: RussianAddress | ForeignAddress | str = RussianAddress()

		# Адрес конечного пункта линейного объекта
		self.oc_FinishAddress: RussianAddress | ForeignAddress | str = RussianAddress()

		# Сведения о функциональном назначении ОКС, состав и характеристику производства,
		#  номенклатуру выпускаемой продукции (работ, услуг)
		self.o_Functions: Functions = Functions()

		# Принадлежность к объектам транспортной инфраструктуры и к другим объектам, 
		# функционально-технологические особенности которых влияют на их безопасность
		self.o_FunctionsFeatures: TextBlock = TextBlock()

		self.om_PowerIndicator: list[TEI] = []	# Данные о проектной мощности ОКС
		self.nm_TEI: list[TEI] = []				# ТЭПы проектируемого ОКС

		# Класс опасности опасного производственного объекта
		self.oc_DangerousIndustrialObject: str = 'IV'

		self.o_LinearObjectCategory: TextBlock = TextBlock()	# Сведения о категории линейного объекта
		self.o_LinearObjectClass: TextBlock = TextBlock()		# Сведения о классе линейного объекта
		self.n_LinearObjectNote: TextBlock | None = None		# Сведения о линейном объекте

		# сведения о ...
		self.oc_inf_about: dict = {
			'FireDangerCategory': 1,					# Категория пожарной и взрывопожарной опасности
			'PeoplePermanentStay': TextBlock(),			# Сведения о наличии помещений с постоянным пребыванием людей
			'ResponsibilityLevel': ('1', '2', '3')[1],	# Уровень ответственности
			'ObjectParts': None							# Сведения о составных частях объекта, в случае если объект сложный TODO
		}
		
		# Сведения о климатической, географической и инженерно-геологической характеристике района
		self.o_ClimateConditions: ClimateConditions = ClimateConditions()

		# Описание вариантов маршрутов прохождения линейного объекта по территории района строительства,
		# обоснование выбранного варианта трассы
		self.o_Routes: Routes = Routes()

		# Сведения о потребности объекта капитального строительства в топливе, газе, воде 
		# и электрической энергии
		self.n_Resources: Resources | None = None

		# Сведения о комплексном использовании сырья, вторичных энергоресурсов, отходов производства
		self.n_ResourceUseInfo: TextBlock | None = None

		# Сведения об использовании возобновляемых источников энергии и вторичных энергетических ресурсов
		self.n_RenewableSourceInfo: TextBlock | None = None

		# Сведения о категории земель, на которых располагается ОКС
		self.om_LandCategory: list[int] = []

		# Сведения о земельных участках
		self.n_LandInfo: LandInfo | None = None

		# Сведения об использованных в проекте изобретениях
		self.n_PatentsUsed: TextBlock | None = None

		# Сведения о наличии разработанных и согласованных специальных технических условий
		self.n_SpecialRequirements: TextBlock | None = None

		# Сведения о компьютерных программах, которые использовались при выполнении расчетов 
		# конструктивных элементов зданий, строений и сооружений
		self.n_SoftwareUsed: SoftwareUsed | None = None

		# Обоснование возможности осуществления строительства, реконструкции ОКС по этапам строительства,
		# реконструкции с выделением этих этапов
		self.n_StagesInfo: StagesInfo | None = None

		# Сведения о предполагаемых затратах, связанных со сносом зданий и сооружений, 
		# переселением людей, переносом сетей ИТО
		self.n_DestroyFunds: TextBlock | None = None

		# Сведения о разделах и пунктах проектной документации, содержащих решения и 
		# мероприятия по обеспечению соблюдения требований промышленной безопасности - 
		# для опасных производственных объектов {: str,}
		self.nm_IndustrialSafetyLinks: list[dict[
			'DocNumber': str,		# Ссылка на документ ПД (Шифр из СП)
			'DocSectionLink': str	# Ссылка на главу или пункт в документе
		]] = []

		# Cведения о наличии проекта рекультивации земель
		self.n_LandReclamationLink: TextBlock | None = None

		# Дополнительные требования к пояснительной записке в соответствии с Приложением 10 к 
		# Положению о составе разделов проектной документации и требованиях к их содержанию 
		# (в отношении сетей газораспределения и (или) газопотребления давлением до 1,2 МПа включительно)
		self.n_GasNetworksFeatures: GasNetworksFeatures | None = None

		# Описание принципиальных проектных решений по инженерной защите территории при 
		# строительстве, реконструкции автомобильных дорог
		self.n_EngineeringTerritoryProtection: TextBlock | None = None

		# ---------- Выбор из двух ----------
		# Сведения о составе проектной документации линейного объекта сети газораспределения 
		# и (или) газопотребления давлением до 1,2 МПа включительно
		self.oc_GasProjectDocumentation: object = None

		# Сведения о составе проектной документации линейного объекта
		self.oc_ProjectDocumentation: LinearProjectDocumentContent = LinearProjectDocumentContent()
		# -----------------------------------

		self.n_Model: Model | None = None # Представление модели объекта

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `LinearObject`
		"""
		# ------------------------ Атрибуты ------------------------
		if self.oa_ObjectID:
			parent.set('ObjectID', self.oa_ObjectID)
		else:
			get_report('LinearObject', f'Атрибут {self.oa_ObjectID=} не валиден')

		if self.oa_Placement in (1,2):
			parent.set('Placement', self.oa_Placement)
		else:
			get_report('LinearObject', f'Атрибут {self.oa_Placement=} не валиден')

		if self.oca_DangerousAndComplex in range(15):
			parent.set('DangerousAndComplex', self.oca_DangerousAndComplex)
		else:
			get_report(
				'LinearObject', f'Атрибут {self.oca_DangerousAndComplex=} не валиден'
			)

		if self.oca_Unique in range(5):
			parent.set('Unique', self.oca_Unique)
		else:
			get_report('LinearObject', f'Атрибут {self.oca_Unique=} не валиден')

		if self.na_ElectronicBudgetObjectCode:
			parent.set('ElectronicBudgetObjectCode', self.na_ElectronicBudgetObjectCode)

		# ---------- Наименование объекта капитального строительства ----------
		ET.SubElement(parent, 'Name').text = self.o_Name

		# ---------- Сведения о включении ОКС в Гос. Проект ----------
		if self.n_NationalProject:
			tNationalProject = ET.SubElement(parent, 'NationalProject')
			self.n_NationalProject.write_xml(tNationalProject)

		# ---------- Вид работ, на который разрабатывается ПД ----------
		if self.oc_ConstructionType in tuple(range(6))[1:]:
			ET.SubElement(parent, 'ConstructionType').text = str(self.oc_ConstructionType)
		else:
			get_report('ConstructionType', 'не валидный код вида работ')

		# ---------- Продолжительность работ, месяц ----------
		if self.n_ConstructionDuration and isinstance(self.n_ConstructionDuration, float):
			ET.SubElement(parent, 'ConstructionDuration').text = str(self.n_ConstructionDuration)

		# ---------- сроки строительства, ввода в эксплуатацию ----------
		@staticmethod
		def __process_date(parent: ET.Element, name, data):
			if check_date(data):
				ET.SubElement(parent, name).text = data
			else:
				get_report(
					f'ConstructionDates -> {name}', 
					'Дата не соответствует формату YYYY-MM-DD'
				)

		if self.n_ConstructionDates:
			begin = self.n_ConstructionDates.get('BeginDate')
			end = self.n_ConstructionDates.get('EndDate')
			oper = self.n_ConstructionDates.get('OperationDate')

			if begin or end or oper:
				tConstructionDates = ET.SubElement(parent, 'ConstructionDates')
				if begin:
					__process_date(tConstructionDates, 'BeginDate', begin)
				if end:
					__process_date(tConstructionDates, 'EndDate', end)
				if oper:
					__process_date(tConstructionDates, 'OperationDate', oper)
			else:
				get_report('ConstructionDates', 'Ошибка типа данных')
		
		# ----------------------- Адрес объекта -----------------------
		def __start_end_address(parent: ET.Element, obj: RussianAddress | ForeignAddress| str):
			match obj:
				case RussianAddress():
					tRussianAddress = ET.SubElement(parent, 'RussianAddress')
					obj.write_xml(tRussianAddress)
				case ForeignAddress():
					tForeignAddress = ET.SubElement(parent, 'ForeignAddress')
					obj.write_xml(tForeignAddress)
				case str():
					ET.SubElement(parent, 'SeaRussianAddress').text = obj

		# ---------- Адрес начального пункта линейного объекта ----------
		tObjectAddress = ET.SubElement(parent, 'Address')
		__start_end_address(tObjectAddress, self.oc_Address)
		
		# ---------- Адрес конечного пункта линейного объекта ----------
		tObjectAddress = ET.SubElement(parent, 'FinishAddress')
		__start_end_address(tObjectAddress,self.oc_FinishAddress)
	
		# ---------- Сведения о функциональном назначении ОКС ----------
		tFunctions = ET.SubElement(parent, 'Functions')
		self.o_Functions.write_xml(tFunctions)

		# ---------- Данные о проектной мощности ОКС ----------
		for pi in self.om_PowerIndicator:
			tTEI = ET.SubElement(parent, 'PowerIndicator')
			pi.write_xml(tTEI)
		
		# ---------- ТЭПы проектируемого ОКС ----------
		for tei in self.nm_TEI:
			tTEI = ET.SubElement(parent, 'TEI')
			tei.write_xml(tTEI)

		# ---------- Класс опасности произв. объекта ----------
		if self.oc_DangerousIndustrialObject in ('I', 'II', 'III', 'IV'):
			ET.SubElement(parent, 'DangerousIndustrialObject').text = self.oc_DangerousIndustrialObject
		else:
			get_report('DangerousIndustrialObject', 'Значение не валидно')

		# ---------- Сведения о категории, классе и прочем линейного объекта ----------
		objCategory = ET.SubElement(parent, 'LinearObjectCategory')
		self.o_LinearObjectCategory.write_xml(objCategory)

		objClass = ET.SubElement(parent, 'LinearObjectClass')
		self.o_LinearObjectClass.write_xml(objClass)

		if self.n_LinearObjectNote:
			objNote = ET.SubElement(parent, 'LinearObjectNote')
			self.n_LinearObjectNote.write_xml(objNote)

		# ---------- Сведения о ... ----------
		match self.oc_inf_about:
			case {'ObjectParts': None}:
				fd_data = self.oc_inf_about.get('FireDangerCategory')
				people_permanent_data = self.oc_inf_about.get('PeoplePermanentStay')
				rl_data = self.oc_inf_about.get('ResponsibilityLevel')
				
				try:
					if isinstance(fd_data, int) and fd_data in tuple(range(7))[1:]:
						ET.SubElement(parent, 'FireDangerCategory').text = str(fd_data)
					else:
						get_report('FireDangerCategory', 'Не валидный ключ')

					if 	isinstance(people_permanent_data, TextBlock):
						element_PPS = ET.SubElement(parent, 'PeoplePermanentStay')
						people_permanent_data.write_xml(element_PPS)
					else:
						get_report('PeoplePermanentStay', 'Не соответствует классу TextBlock')
					
					if isinstance(rl_data, int) in tuple(range(4))[1:]:
						ET.SubElement(parent, 'ResponsibilityLevel').text = str(rl_data)
					else:
						get_report('ResponsibilityLevel', 'Не валидный ключ')
				except Exception as e:
					get_report('FireDangerCategory | PeoplePermanentStay | ResponsibilityLevel', e)
			case _:
				pass	# TODO Разработать систему со сложным объектом

		# ---------- Сведения о климатической, географической и ----------
		# 			инженерно-геологической характеристике района
		tClimateConditions = ET.SubElement(parent, 'ClimateConditions')
		self.o_ClimateConditions.write_xml(tClimateConditions)

		# ---------- Сведения о вариантах прохождения маршрутов ----------
		tRoutes = ET.SubElement(parent, 'Routes')
		self.o_Routes.write_xml(tRoutes)

		# ---------- Сведения о потребности ОКС в топливе, газе, воде и энергии ----------
		if self.n_Resources:
			tResources = ET.SubElement(parent, 'Resources')
			self.n_Resources.write_xml(tResources)

		# ---------- Сведения о комплексном использовании сырья ----------
		if self.n_ResourceUseInfo:
			element = ET.SubElement(parent, 'ResourceUseInfo')
			self.n_ResourceUseInfo.write_xml(element)
		
		# ---------- Сведения о возобновляемых источников энергии ----------
		if self.n_RenewableSourceInfo:
			element = ET.SubElement(parent, 'RenewableSourceInfo')
			self.n_RenewableSourceInfo.write_xml(parent)

		# ---------- Сведения о категории земель ----------
		value_range = tuple(range(1, 8))

		for value in self.om_LandCategory:
			if value not in value_range:
				ET.SubElement(parent, 'LandCategory').text = str(value)
			else:
				get_report('LandCategory', f'Не валидный параметр {value}')
		
		# ---------- Сведения о земельных участках ----------
		if self.n_LandInfo:
			tLandInfo = ET.SubElement(parent, 'LandInfo')
			self.n_LandInfo.write_xml(tLandInfo)

		# ---------- Сведения об использованных в проекте изобретениях ----------
		if self.n_PatentsUsed:
			element = ET.SubElement(parent, 'LandInfo')
			self.n_PatentsUsed.write_xml(element)

		# ---------- Сведения об использованных в проекте изобретениях ----------
		if self.n_SpecialRequirements:
			element = ET.SubElement(parent, 'SpecialRequirements')
			self.n_SpecialRequirements.write_xml(element)

		# ---------- Сведения о компьютерных программах ----------
		if self.n_SoftwareUsed:
			tSoftwareUsed = ET.SubElement(parent, 'SoftwareUsed')
			self.n_SoftwareUsed.write_xml(tSoftwareUsed)

		# ---------- Сведения о этапах ----------
		if self.n_StagesInfo:
			tStagesInfo = ET.SubElement(parent, 'StagesInfo')
			self.n_StagesInfo.write_xml(tStagesInfo)

		# ---------- Сведения о предполагаемых затратах, связанных со демантажом --------
		if self.n_DestroyFunds:
			tDestroyFunds = ET.SubElement(parent, 'DestroyFunds')
			self.n_DestroyFunds.write_xml(tDestroyFunds)

		# ---------- Сведения о разделах и пунктах  ПД   по обеспечению соблюдения --------
		# 						требований промышленной безопасности 
		if self.nm_IndustrialSafetyLinks:
			tProjectDocumentationLinks = ET.SubElement(parent, 'IndustrialSafetyLinks')
			for pdl in self.nm_IndustrialSafetyLinks:
				number = pdl.get('DocNumber')
				link = pdl.get('DocSectionLink')
				if not number:
					get_report(
						'ProjectDocumentationLink', 
						'Не заполнен обязательный параметр DocNumber'
					)
					continue
				tProjectDocumentationLink  = ET.SubElement(
					tProjectDocumentationLinks, 
					'ProjectDocumentationLink'
				)
				ET.SubElement(tProjectDocumentationLink, 'DocNumber').text = number
				if link:
					ET.SubElement(tProjectDocumentationLink, 'DocSectionLink').text = link

		# ---------- Cведения о наличии проекта рекультивации земель ----------
		if self.n_LandReclamationLink:
			tLandReclamationLink = ET.SubElement(parent, 'LandReclamationLink')
			self.n_LandReclamationLink.write_xml(tLandReclamationLink)

		# ---------- Дополнительные сведения о сетях газораспределения ----------
		if self.n_GasNetworksFeatures:
			tGasNetworksFeatures = ET.SubElement(parent, 'GasNetworksFeatures')
			self.n_GasNetworksFeatures.write_xml(tGasNetworksFeatures)

		# ---------- Cведения о инженерной защите для автомобильных дорог ----------
		if self.n_EngineeringTerritoryProtection:
			tEngineeringTerritoryProtection = ET.SubElement(parent, 'EngineeringTerritoryProtection')
			self.n_EngineeringTerritoryProtection.write_xml(tEngineeringTerritoryProtection)

		# ---------- Сведения о составе проектной документации линейного объекта ----------
		if self.oc_GasProjectDocumentation:
			pass	# TODO
		else:
			tLinearProjectDocumentContent = ET.SubElement(parent, 'ProjectDocumentation')
			self.oc_ProjectDocumentation.write_xml(tLinearProjectDocumentContent)

		# ---------- Представление модели объекта ---------
		if self.n_Model:
			model_element = ET.SubElement(parent, 'Model')
			self.n_Model.write_xml(model_element)
			