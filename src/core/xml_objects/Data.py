# Copyright © 2026 OldNestling
# License: GPLv3 (GNU General Public License Version 3)

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from lib.tDocumentType import tDocumentType 
from lib.tEngineeringSurveyDocumentType import tEngineeringSurveyDocumentType
from lib.tOKEI import tOKEI

from ..support.utilities import get_report, check_date, get_CRC32_checksum
from core.xml_objects.People_and_Orgs import Organization, IndividualEntrepreneur, EngineerPerson


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




#											Данные
#----------------------------------------------------------------------------------------

class Modification:
	""" Сведения о внесении изменения в пояснительную записку """
	def __init__(self):
		self.o_ModificationNumber: int = 1 # Номер изменения

		# Дата изменения
		self.o_ModificationDate: str = datetime.date.today().isoformat() # '2026-06-11'

		self.n_ModificationNote: str | None  = None # Описание изменения

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет элемент `Modification`
		
		:parent:  `Modification`
		"""
		ET.SubElement(parent, 'ModificationNumber').text = self.o_ModificationNumber
		ET.SubElement(parent, 'ModificationDate').text = self.o_ModificationDate
		if self.n_ModificationNote:
			ET.SubElement(parent, 'ModificationNote').text = self.n_ModificationNote


class Image:
	""" Изображение """
	def __init__(self):
		self.oa_Type: str = 'jpeg'	# Формат изображения jpg | gif | png | jpeg
		self.o_ImageData: str = ''	# Изображение в формате base64
		self.n_Comment: str = ''	# Комментарий к изображению

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `Image`
		"""
		global reports

		if self.oa_Type in ('jpg','gif','png','jpeg'):
			parent.set('Type', self.oa_Type)
		else:
			get_report(f'tImage {self.n_Comment}', f'Некорректное расширение')

		ET.SubElement(parent, 'ImageData').text = self.o_ImageData

		if self.n_Comment:
			ET.SubElement(parent, 'Comment').text = self.n_Comment


class Cell:
	""" Ячейка строки таблицы """
	def __init__(self):
		self.na_align: str = 'center'	# Параметр выравнивания данных в ячейке  
		self.o_content: str = ''		# содержимое ячейки
	
	def write_xml(self, parent: ET.Element):
		"""
		Добавляет в переданный элемент `parent` 1 элемент `Cell`

		:parent: `Row` | `TitleRow`
		"""
		cell = ET.SubElement(parent, 'Cell')
		cell.text = self.o_content
		if self.na_align:
			cell.set('align', self.na_align)


class Table:
	""" Таблица """
	def __init__(self):
		self.n_TitleRow: list[Cell] = []		# Строка заголовка таблицы
		self.o_Rows: list[list[Cell]] = [] 		# Строка(и) таблицы
	
	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `Table`
		"""
		if self.n_TitleRow:
			tTytleRow = ET.SubElement(parent, 'TitleRow')
			for cell in self.n_TitleRow:
				cell: Cell
				cell.write_xml(tTytleRow)
		for row in self.o_Rows:
			tRow = ET.SubElement(parent, 'Row')
			for cell in row:
				cell.write_xml(tRow)


class TextBlock:
	""" Блок текстового описания """
	def __init__(self):
		self.na_Title: str | None = None		# Заголовок текстового блока
		self.om_elements: list[dict | Image | Table] = [] 
		# dict = {'type': str['SubTitle'|'Text], 'content': str}
	
	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `UsedAbbreviations`, `DesignerNote`, `DesignerAssurance` ...
		"""
		if self.na_Title:
			parent.set('Title', self.na_Title)
		for element in self.om_elements:
			match element:
				case {'type': 'SubTitle'}:
					ET.SubElement(parent, 'SubTitle').text = element.get('content', '')
				case {'type': 'Text'}:
					ET.SubElement(parent, 'Text').text = element.get('content', '')
				case Table():
					tTable = ET.SubElement(parent, 'Table')
					element: Table
					element.write_xml(tTable)
				case Image():
					tImage = ET.SubElement(parent, 'Image')
					element: Image
					element.write_xml(tImage)


class SignFile:
	""" Файл подписи к документу """
	def __init__(self):
		self.o_FileName: str = ''			# Имя файла документа
		self.o_FileFormat: str = ''			# Формат файла документа (Текстовая строка длиной до 4 символов)
		self.n_FileRelativePath: str = ''	# Относительный путь к файлу

		self.file_path: Path | None = None	# Путь к файлу
	
	@property
	def o_FileChecksum(self):
		""" Контрольная сумма файла, рассчитанная по алгоритму CRC32-IEEE """
		return get_CRC32_checksum(self.file_path)

	def __str__(self):
		return f'{self.o_FileName}.{self.o_FileFormat}: {self.n_FileRelativePath}'

	
	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `SignFile`
		"""
		ET.SubElement(parent, 'FileName').text = self.o_FileName
		ET.SubElement(parent, 'FileFormat').text = self.o_FileFormat

		if self.n_FileRelativePath:
			ET.SubElement(parent, 'FileRelativePath').text = self.n_FileRelativePath
		
		ET.SubElement(parent, 'FileChecksum').text = self.o_FileChecksum


class File(SignFile):
	""" Файл документа или файл фрагмента документа """
	def __init__(self):
		super().__init__()
		self.nm_SignFile: list[SignFile] = []	# Файл подписи к основному файлу документа

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `File`
		"""
		super().write_xml(parent)
		for sf in self.nm_SignFile:
			tSignFile = ET.SubElement(parent, 'SignFile')
			sf.write_xml(tSignFile)

class Data:
	""" Дополнительный материал """
	def __init__(self):
		self.o_DataDescription: str = ''	# Описание материала
		self.om_File: list[File] = []		# Файл, содержащий материал
	
	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `Data`
		"""
		ET.SubElement(parent, 'DataDescription').text = self.o_DataDescription
		for file in self.om_File:
			tFile = ET.SubElement(parent, 'File')
			file.write_xml(tFile)

class Document:
	""" Описание документа """
	def __init__(self):
		self.o_DocType: str = ''			# Код типа документа по tDocumentType
		self.o_DocName: str = ''			# Наименование документа
		self.o_DocNumber: str = ''			# Номер (обозначение, шифр) документа
		self.o_DocDate: str = ''			# Дата документа
		self.o_DocIssueAuthor: str = '' 	# Юридическое лицо, ИП или физическое лицо - автор документа
		self.oc_doc: list[File] | dict = []	# 1. Файл документа 2. Ссылка на документ 3. Приложенный документ

	def __str__(self):
		return self.o_DocNumber + self.o_DocName
	
	def check_type(self):
		if self.o_DocType in tDocumentType:
			return True
		else: 
			return False
	
	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `Document` | `OtherDocument`
		"""
		ET.SubElement(parent, 'DocType').text = self.o_DocType
		ET.SubElement(parent, 'DocName').text = self.o_DocName
		ET.SubElement(parent, 'DocNumber').text = self.o_DocNumber

		if check_date(self.o_DocDate):
			ET.SubElement(parent, 'DocDate').text = self.o_DocDate
		else:
			get_report(f'Document {self}', f'дата {self.o_DocDate} не соответствует формату')

		ET.SubElement(parent, 'DocIssueAuthor').text = self.o_DocIssueAuthor

		match self.oc_doc:
			case {'type': 'Included'}:
				ET.SubElement(parent, 'Included').text = self.oc_doc.get('content', '')
			case {'type': 'Link'}:
				ET.SubElement(parent, 'Link').text = self.oc_doc.get('content', '')
			case list():
				for file in self.oc_doc:
					doc = ET.SubElement(parent, 'File')
					file.write_xml(doc)


class EngineeringSurveyDocument:
	""" Описание документа """
	def __init__(self):
		self.o_DocType: str = ''			# Код типа документа по tDocumentType
		self.o_DocName: str = ''			# Наименование документа
		self.o_DocNumber: str = ''			# Номер (обозначение, шифр) документа
		self.o_DocDate: str = ''			# Дата документа

		# Сведения об исполнителе отчета о результатах ИИ 
		# (организация или индивидуальный предприниматель)
		self.om_FullDocIssueAuthor: list[Organization | IndividualEntrepreneur] = []

		self.n_DocChanges: str = ''			# Отметка об изменении документа

		# Сведения о лицах, принимавших участие в разработке, 
		# осуществлении нормоконтроля и согласовании документа
		# (НОПРИЗ не обязателен, но возможен)
		self.o_SurveyDocParticipants: list[EngineerPerson] = []

		# Файл (фрагмента) отчета о результатах инженерных изысканий
		self.om_File: list[File] = []	

	def __str__(self):
			return self.o_DocNumber + self.o_DocName
	
	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `Document` | `OtherDocument`
		"""
		ET.SubElement(parent, 'DocType').text = self.o_DocType
		ET.SubElement(parent, 'DocName').text = self.o_DocName
		ET.SubElement(parent, 'DocNumber').text = self.o_DocNumber

		if check_date(self.o_DocDate):
			ET.SubElement(parent, 'DocDate').text = self.o_DocDate
		else:
			get_report(f'Document {self}', f'дата {self.o_DocDate} не соответствует формату')
		
		for doc_autor in self.om_FullDocIssueAuthor:
			print(f'... EngineeringSurveyDocument [FullDocIssueAuthor {self}] ...', end=' ')
			tProjectDocumentationAuthor = ET.SubElement(parent, 'FullDocIssueAuthor')

			match doc_autor:
				case IndividualEntrepreneur(necessary_NOPRIZ = 'option'):
					ip = ET.SubElement(tProjectDocumentationAuthor, 'IP')
					doc_autor.write_xml(ip)
				case Organization(necessary_NOPRIZ = 'option'):
					org = ET.SubElement(tProjectDocumentationAuthor, 'Organization')
					doc_autor.write_xml(org)
				case _:
					get_report(f'FullDocIssueAuthor {self}', f'не удалось обработать')
			print(f'... FullDocIssueAuthor {self} записано')
		
		if self.n_DocChanges:
			ET.SubElement(parent, 'DocChanges').text = self.n_DocChanges
		
		tDocParticipants = ET.SubElement(parent, 'SurveyDocParticipants')
		for doc in self.o_SurveyDocParticipants:
			print(f'... DocParticipant [{doc}] ...', end=' ')
			match doc:
				case EngineerPerson(necessary_NOPRIZ = 'option'):
					tEngineerPersonNoNOPRIZ = ET.SubElement(tDocParticipants, 'DocParticipant')
					doc.write_xml(tEngineerPersonNoNOPRIZ)
			print(f'... DocParticipant [{doc}] записано')

		for file in self.om_File:
			tFile = ET.SubElement(parent, 'File')
			file.write_xml(tFile)


class ProjectDocument:
	""" Описание документа - часть проектной документации """
	def __init__(self):
		# Идентификатор(ы) объекта (части объекта), описание которого(ой) содержится в томе документации
		self.na_ObjectIDREFS = ''

		self.o_DocName: str = '' 	# Наименование документа
		self.o_DocNumber: str = ''	# Номер (обозначение, шифр) документа
		self.n_DocChanges: str = ''	# Отметка об изменении документа

		# Сведения о лицах, принимавших участие в разработке, осуществлении нормоконтроля и
		# согласовании документа - части проектной документации
		self.om_ProjectDocParticipants: list[EngineerPerson] = []

		self.om_File: list[File]	# Файл документа или файл фрагмента документа

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`

		:parent: `Document`
		"""
		if self.na_ObjectIDREFS:
			parent.set('ObjectIDREFS', self.na_ObjectIDREFS)

		ET.SubElement(parent, 'DocName').text = self.o_DocName
		ET.SubElement(parent, 'DocNumber').text = self.o_DocNumber

		if self.n_DocChanges:
			ET.SubElement(parent, 'DocChanges').text = self.n_DocChanges

		if not self.om_ProjectDocParticipants:
			get_report('tProjectDocument (ProjectDocParticipants)', 'Должен быть хотя бы один участник')
		else:
			tDocParticipants = ET.SubElement(parent, 'ProjectDocParticipants')
			for person in self.om_ProjectDocParticipants:
				tEngineerPersonNoNOPRIZ = ET.SubElement(tDocParticipants, 'DocParticipant')
				person.write_xml(tEngineerPersonNoNOPRIZ)
		if not self.om_File:
			get_report(
				'tProjectDocument (File)', 
				f'{self.o_DocName}: отсутствуют файл документа или файл фрагмента документа'
			)
			return
		for file in self.om_File:
			tFile = ET.SubElement(parent, 'File')
			file.write_xml(tFile)



class SectionContent:
	""" Состав раздела проектной документации 
	Является объединением типов tProjectDocumentSectionContent, tProjectDocumentSubSection"""
	def __init__(self):
		self.na_Name: str | None = None		# Наименование подраздела
		self.is_sub_section: bool = False	# Отметка принадлежности к подразделу
		self.content: list[ProjectDocument | SectionContent] = []

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		:parent: `SectionContent` | `SubSection`
		"""
		if self.is_sub_section and self.na_Name:
			parent.set('Name', self.na_Name)
		elif self.is_sub_section:
			get_report('ProjectDocumentSectionContent', f'Атрибут {self.na_Name=} не может быть пустым')

		if not self.content:
			get_report('ProjectDocumentSectionContent', 'Необходим минимум 1 элемент данных')
			return
		
		for element in self.content:
			subparent = ET.SubElement(parent, 'Document' if isinstance(element, Document) else 'SubSection')
			element.write_xml(subparent)
			


class ProjectDocumentSection:
	""" Документы и подразделы, в составе раздела проектной документации """
	def __init__(self):
		# ---------- Выбор из двух ----------
		# Отметка о том, что раздел не разрабатывался. Должна содержать текст "Раздел не разрабатывался"
		self.oc_NotDeveloped: str = 'Раздел не разрабатывался'

		# Сведения о составе проектной документации линейного объекта
		self.oc_SectionContent: SectionContent | SectionOtherContent = SectionContent()
		# -----------------------------------
		self.is_not_developed: bool = False	# выбор используемого атрибута

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		:parent: `Section1`, `Section2` ... 
		"""
		if self.is_not_developed:
			ET.SubElement(parent, 'NotDeveloped').text = self.oc_NotDeveloped
		else:
			tProjectDocumentSectionContent = ET.SubElement(parent, 'SectionContent')
			self.oc_SectionContent.write_xml(tProjectDocumentSectionContent)



class SectionEstimate:
	""" Состав раздела "Смета на строительство" """
	def __init__(self):
		# Отметка о том, что раздел не разрабатывался. Должна содержать текст "Раздел не разрабатывался"
		self.oc_NotDeveloped: str = 'Раздел не разрабатывался'
		self.is_not_developed: bool = False	# выбор используемого атрибута

		# Пояснительная записка к сметной документации
		self.n_EstimateExplanatoryNote: SectionContent | None = None

		# Сводка затрат
		self.n_CostSummary: SectionContent | None = None

		# Сводный сметный расчет
		self.n_SummaryEstimate: SectionContent | None = None

		# Объектные расчеты
		self.n_ObjectEstimates: SectionContent | None = None

		# Локальные расчеты
		self.n_LocalEstimates: SectionContent | None = None

		# Сметные расчеты на отдельные виды затрат
		self.n_CostsEstimates: SectionContent | None = None

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		:parent: `SectionContent`
		"""
		if self.is_not_developed:
			ET.SubElement(parent, 'NotDeveloped').text = self.oc_NotDeveloped
			return
		
		attributes = {
			'EstimateExplanatoryNote': self.n_EstimateExplanatoryNote, 
			'CostSummary': self.n_CostSummary,
			'SummaryEstimate': self.n_SummaryEstimate,
			'ObjectEstimates': self.n_ObjectEstimates,
			'LocalEstimates': self.n_LocalEstimates,
			'CostsEstimates': self.n_CostsEstimates,
		}

		checker = False
		for attr in attributes.values():
			if attr: 
				checker = True
				break

		if not checker:
			get_report(
				'SectionEstimate',
				'Для разрабатываемого раздела необходим как минимум один подраздел'
			)
			return

		for key, value in attributes.items():
			if not value:
				continue
			element = ET.SubElement(parent, key)
			value.write_xml(element)
		


class ProjectDocumentNotNecessarySectionContent:
	""" Документы и подразделы, в составе раздела проектной документации (не обязательные) """
	def __init__(self):
		# Документ, разработанный в рамках проектной документации
		self.nm_Document: list[ProjectDocument] = []

		# Иной документ, предусмотренный законодательными
		# и иными нормативными правовыми актами Российской Федерации
		self.nm_OtherDocument: list[Document] = []

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		"""
		if not self.nm_Document and not self.nm_OtherDocument:
			get_report(
				'ProjectDocumentNotNecessarySectionContent',
				'Должен быть ходя бы 1 документ'
			)

		for doc in self.nm_Document:
			element = ET.SubElement(parent, 'Document')
			doc.write_xml(element)

		for doc in self.nm_OtherDocument:
			element = ET.SubElement(parent, 'OtherDocument')
			doc.write_xml(element)



class SectionOtherContent:
	""" Раздел "Иная документация в случаях, предусмотренных законодательными
	и иными нормативными правовыми актами Российской Федерации" """
	def __init__(self):
		# Отметка о том, что раздел не разрабатывался. Должна содержать текст "Раздел не разрабатывался"
		self.oc_NotDeveloped: str = 'Раздел не разрабатывался'
		self.is_not_developed: bool = True	# выбор используемого атрибута

		# -------------------
		
		# Декларация промышленной безопасности опасных производственных объектов
		self.n_IndustrialSafetyDeclaration: ProjectDocumentNotNecessarySectionContent | None = None

		# Декларация безопасности гидротехнических сооружений
		self.n_HydraulicStructuresSafetyDeclaration: ProjectDocumentNotNecessarySectionContent | None = None

		# Перечень мероприятий по гражданской обороне, мероприятий по предупреждению 
		# чрезвычайных ситуаций природного и техногенного характера
		self.n_CivilDefense: ProjectDocumentNotNecessarySectionContent | None = None

		# Мероприятия по противодействию терроризму для объектов использования атомной энергии,
		# опасных производственных объектов, особо опасных, технически сложных, уникальных объектов, 
		# объектов обороны и безопасности
		self.n_CounteringTerrorism: ProjectDocumentNotNecessarySectionContent | None = None

		# Мероприятия по радиационной и ядерной безопасности
		self.n_RadiationNuclearSafety: ProjectDocumentNotNecessarySectionContent | None = None

		# Санитарно-эпидемиологическая безопасность
		self.n_SanitarySafety: ProjectDocumentNotNecessarySectionContent | None = None

		# Охрана объектов культурного наследия
		self.n_CulturalHeritageSites: ProjectDocumentNotNecessarySectionContent | None = None

		# Мероприятия по рекультивации нарушенных земель
		self.n_LandsReclamation: ProjectDocumentNotNecessarySectionContent | None = None

		# Оценка воздействия на водные биологические ресурсы
		self.n_BiologicalResourcesImpact: ProjectDocumentNotNecessarySectionContent | None = None

		# Иная документация, установленная законодательными и иными нормативными правовыми актами Российской Федерации
		self.n_OtherDocuments: ProjectDocumentNotNecessarySectionContent | None = None

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
		:parent: `SectionContent`
		"""
		if self.is_not_developed:
			ET.SubElement(parent, 'NotDeveloped').text = self.oc_NotDeveloped
			return

		attributes = {
			'IndustrialSafetyDeclaration': self.n_IndustrialSafetyDeclaration, 
			'HydraulicStructuresSafetyDeclaration': self.n_HydraulicStructuresSafetyDeclaration,
			'CivilDefense': self.n_CivilDefense,
			'CounteringTerrorism': self.n_CounteringTerrorism,
			'RadiationNuclearSafety': self.n_RadiationNuclearSafety,
			'SanitarySafety': self.n_SanitarySafety, 
			'CulturalHeritageSites': self.n_CulturalHeritageSites,
			'LandsReclamation': self.n_LandsReclamation,
			'BiologicalResourcesImpact': self.n_BiologicalResourcesImpact,
			'OtherDocuments': self.n_OtherDocuments
		}
		checker = False
		for attr in attributes.values():
			if attr: 
				checker = True
				break

		if not checker:
			get_report(
				'SectionOtherContent',
				'Для разрабатываемого раздела необходим как минимум один подраздел'
			)
			return
		for key, value in attributes.items():
			if not value:
				continue
			element = ET.SubElement(parent, key)
			value.write_xml(element)



class LinearProjectDocumentContent:
	""" Состав проектной документации линейного объекта капитального строительства """
	def __init__(self):
		# Раздел 2. «Проект полосы отвода»
		self.o_Section2: ProjectDocumentSection = ProjectDocumentSection() 

		# Раздел 3. «Технологические и конструктивные решения линейного объекта. Искусственные сооружения»
		self.o_Section3: ProjectDocumentSection = ProjectDocumentSection()

		# Раздел 4. «Здания, строения и сооружения, входящие в инфраструктуру линейного объекта»
		self.o_Section4: ProjectDocumentSection = ProjectDocumentSection()

		# Раздел 5. «Проект организации строительства»
		self.o_Section5: ProjectDocumentSection = ProjectDocumentSection()

		# Раздел 6. «Мероприятия по охране окружающей среды»
		self.o_Section6: ProjectDocumentSection = ProjectDocumentSection()

		# Раздел 7. «Мероприятия по обеспечению пожарной безопасности»
		self.o_Section7: ProjectDocumentSection = ProjectDocumentSection()

		# Раздел 8. «Требования к обеспечению безопасной эксплуатации линейного объекта»
		self.o_Section8: ProjectDocumentSection = ProjectDocumentSection()

		# Раздел 9. «Смета на строительство, реконструкцию, капитальный ремонт, снос ОКС»
		self.o_Section9: SectionEstimate = SectionEstimate()

		# Раздел 10. «Иная документация в случаях, предусмотренных ...»
		self.o_Section10: SectionOtherContent = SectionOtherContent()

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
			:parent: `ProjectDocumentation`
		"""
		sections = (
			self.o_Section2, self.o_Section3, self.o_Section4, self.o_Section5,
			self.o_Section6, self.o_Section7, self.o_Section8, self.o_Section9, 
			self.o_Section10
		)

		for i, sec in enumerate(sections, 2):
			element = ET.SubElement(parent, f'Section{i}')
			sec.write_xml(element)


class ModelFile:
	""" Файл модели или файл части модели """
	def __init__(self):
		self.na_description: str = ''							# Произвольное описание файла модели
		self.o_FileName: str = ''								# Имя файла модели
		self.o_FileFormat: str['IFC'|'XML'|'LandXML'] = 'IFC'	# Формат модели
		self.n_FileRelativePath: Path | None = None 			# Относительный путь к файлу
		self.nm_SignFile: list[SignFile] 						# Файл подписи к основному файлу модели

	@property
	def o_FileChecksum(self):
		""" Контрольная сумма файла, рассчитанная по алгоритму CRC32-IEEE """
		if isinstance(self.n_FileRelativePath, Path) and self.n_FileRelativePath.exists():
			return get_CRC32_checksum(self.n_FileRelativePath)

	def get_filename(self):
		if isinstance(self.n_FileRelativePath, Path) and self.n_FileRelativePath.exists():
			self.o_FileName = self.n_FileRelativePath.stem
			return self.o_FileName

	def select_file(self, path: str):
		filepath = Path(path)
		self.n_FileRelativePath = filepath
		self.get_filename()

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
			:parent: `ModelFile`
		"""
		if self.na_description:
			parent.set('description', self.na_description)

		if not self.o_FileName:
			request = self.get_filename()
			if request:
				ET.SubElement(parent, 'FileName').text = request
			else:
				get_report('ModelFile', 'Отсутствуем имя файла и путь к нему')
		else:
			ET.SubElement(parent, 'FileName').text = request

		if self.o_FileFormat in ('IFC','XML','LandXML'):
			ET.SubElement(parent, 'FileFormat').text = self.o_FileFormat
		else:
			get_report('ModelFile', 'Формат не соответствует паттерну "IFC"|"XML"|"LandXML"')

		if self.n_FileRelativePath:
			ET.SubElement(parent, 'FileFormat').text = self.o_FileFormat

		checksum = self.o_FileChecksum
		if checksum:
			ET.SubElement(parent, 'FileChecksum').text = checksum
		else:
			get_report('ModelFile', 'Не удалось посчитать кэш-сумму файла')
			
		for sign_file in self.nm_SignFile:
			sf_element = ET.SubElement(parent, 'SignFile')
			sign_file.write_xml(sf_element)


		
class Model:
	""" Модель объекта """
	def __init__(self):
		self.n_Description: str = ''	# Описание модели

		# Файл, содержащий модель объекта (части объекта)
		self.om_ModelFile: list[ModelFile] = []

	def write_xml(self, parent: ET.Element):
		"""
		Заполняет переданный элемент `parent`
			:parent: `Model`
		"""
		if self.n_Description:
			ET.SubElement(parent, 'Description').text = self.n_Description
		for file in self.om_ModelFile:
			element = ET.SubElement(parent, 'ModelFile')
			file.write_xml(element)
