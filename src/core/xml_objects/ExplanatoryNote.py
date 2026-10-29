# Copyright © 2026 OldNestling
# License: GPLv3 (GNU General Public License Version 3)

import xml.etree.ElementTree as ET
import re, zlib
from datetime import datetime, timezone
from pathlib import Path
from lib.tDocumentType import tDocumentType 
from lib.tEngineeringSurveyDocumentType import tEngineeringSurveyDocumentType
from lib.tOKEI import tOKEI

from .Data import Modification, TextBlock, Document, EngineeringSurveyDocument, Data
from .People_and_Orgs import Organization, IndividualEntrepreneur, EngineerPerson, PersonSNILS
from .Object_Data import FinanceSources
from .LinerObject import LinearObject
from ..support.utilities import get_report, check_date, reports

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




#							Корневой элемент пояснительной записки
#==================================================================================================

class ExplanatoryNote:
	""" Корневой элемент. Пояснительная записка раздела ПД №1 версия 01.07 """
	def __init__(self):
		self.root = ET.Element('ExplanatoryNote', {
			'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
			'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
			'xsi:noNamespaceSchemaLocation': 'explanatorynote-01-07.xsd',
			'SchemaVersion': '01.07'
		})
		self.o_ExplanatoryNoteNumber: str = ''	# Шифр объекта
		
		#Год составления пояснительной записки
		self.o_ExplanatoryNoteYear: int = datetime.now().year

		# Сведения о внесении изменений в  проектную документацию
		self.n_tExplanatoryNoteModifications: list[Modification] = []

		# Сведения о лице, подготовившем пояснительную записку - генеральном проектировщике
		self.o_IssueAuthor: Organization | IndividualEntrepreneur = Organization(necessary_NOPRIZ= True)

		# Сведения об индивидуальных предпринимателях и (или) юридических лицах, 
		# подготовивших проектную документацию (кроме генерального проектировщика)
		# наличие НОПРИЗ не обязательно
		self.n_ProjectDocumentationAuthors: list[Organization | IndividualEntrepreneur]  = []

		# Сведения о лицах, подписавших документацию
		self.Signers: dict = {
			'ChiefProjectEngineer': EngineerPerson(),
			'ChiefProjectArchitect': None,
			'ChiefProjectEngineerSurvey': [],
			'Signer': []	# НОПРИЗ не требуется, но возможно
		}

		# Сведения о застройщике(ах) и(или) техн. заказчике(ах) 
		self.devs_and_tech_customers: list[IndividualEntrepreneur | Organization | PersonSNILS] = []

		self.n_UsedAbbreviations: TextBlock | None = None # Список используемых сокращений

		# Перечень документов, обеспечивающих требования тех. регламентов
		self.o_UsedNorms: list[str] = []

		# Перечень документов, на основании которых принято решение о подготовке ПД
		self.o_ProjectDecisionDocuments: list[Document] = []

		# Перечень ИРД, кроме отчетной документации по результатам ИИ
		self.o_ProjectInitialDocuments: list[Document] = []

		# Перечень отчетной документации по результатам ИИ
		self.n_EngineeringSurveyDocuments: list[EngineeringSurveyDocument] = []

		# Дополнительные материалы, не предусмотренные ПП РФ №87 от 16.02.2008
		self.n_AdditionalData: list[Data] = []

		# Сведения об источниках финансирования ОКС
		self.n_FinanceSources: FinanceSources | None = None

		# Объект капитального строительства. 'NonIndustrialObject' и 'IndustrialObject' не разрабатываются
		self.o_object: LinearObject  = LinearObject()	

		# Дополнительное произвольное текстовое описание, подготовленное разработчиком ПД
		self.nm_DesignerNote: list[TextBlock] | None = None

		self.o_DesignerAssurance: TextBlock = TextBlock()	# Заверение проектной организации
	# ---------------------------------------------------------------------------------------------

	def write_xml(self):
		global reports
		# ---------- Шифр объекта ----------
		print('ExplanatoryNoteNumber ...', end=' ')
		ET.SubElement(self.root, 'ExplanatoryNoteNumber').text = self.o_ExplanatoryNoteNumber
		print('... записано')

		# ---------- Год составления ПЗ ----------
		print('ExplanatoryNoteYear ...', end=' ')
		ET.SubElement(self.root, 'ExplanatoryNoteYear').text = str(self.o_ExplanatoryNoteYear)
		print('... записано')

		# ---------- Сведения о внесении изменений в  ПД ----------
		if self.n_tExplanatoryNoteModifications:
			print('ExplanatoryNoteModifications ...', end=' ')
			tExplanatoryNoteModifications = ET.SubElement(self.root, 'ExplanatoryNoteModifications')
			for modification in self.n_tExplanatoryNoteModifications:
					modification: Modification
					tModification = ET.SubElement(
						tExplanatoryNoteModifications, 'Modification'
					)
					modification.write_xml(tModification)
			print('... записано')

		# ---- Сведения о лице, подготовившем ПЗ - генеральном проектировщике ----
		print('IssueAuthor ...', end=' ')
		tAuthor = ET.SubElement(self.root, 'IssueAuthor')
		if isinstance(self.o_IssueAuthor, Organization):
			tag = 'Organization'
		else:
			tag = 'IP'
		element = ET.SubElement(tAuthor, tag)
		self.o_IssueAuthor.write_xml(element)
		print('... записано')

		# ---- Сведения об ИП и (или) ЮЛ, подготовивших ПД ----
		# ---- (кроме генерального проектировщика) ----
		if self.n_ProjectDocumentationAuthors:
			print('ProjectDocumentationAuthors ...', end=' ')
			tProjectDocumentationAuthors = ET.SubElement(self.root, 'ProjectDocumentationAuthors')
			for pda in self.n_ProjectDocumentationAuthors:
				tProjectDocumentationAuthor = ET.SubElement(
					tProjectDocumentationAuthors, 'ProjectDocumentationAuthor'
				)
				if isinstance(pda, Organization):
					tag = 'Organization'
				else:
					tag = 'IP'
				element = ET.SubElement(tProjectDocumentationAuthor, tag)
				pda.write_xml(element)
			print('... записано')

		# ---------- Сведения о лицах, подписавших документацию ----------
		print('Signers ...', end=' ')
		tSigners =  ET.SubElement(self.root, 'Signers')

		element_ChiefProjectEngineer = ET.SubElement(tSigners, 'ChiefProjectEngineer')
		person: EngineerPerson = self.Signers.get('ChiefProjectEngineer')
		person.write_xml(element_ChiefProjectEngineer)

		person: EngineerPerson = self.Signers.get('ChiefProjectArchitect')
		if person:
			element_ChiefProjectArchitect = ET.SubElement(tSigners, 'ChiefProjectArchitect')
			person.write_xml(element_ChiefProjectArchitect)
		
		persons: list[EngineerPerson] = self.Signers.get('ChiefProjectEngineerSurvey')
		for chief_PES in persons:
			element_ChiefProjectEngineerSurvey = ET.SubElement(
				tSigners, 'ChiefProjectEngineerSurvey'
			)
			chief_PES.write_xml(element_ChiefProjectEngineerSurvey)

		singers: list[EngineerPerson] = self.Signers.get('Signer')
		for singer in singers:
			element_EngineerPersonNoNOPRIZ = ET.SubElement(tSigners, 'Signer')
			singer.write_xml(element_EngineerPersonNoNOPRIZ)
		print('... записано')
		
		# ---------- Сведения о застройщике(ах) и(или) техн. заказчике(ах) ----------
		print('Devolopers and TechnicalCustomers ...', end=' ')
		for big_boy in self.devs_and_tech_customers:
			match big_boy:
				case Organization(necessary_NOPRIZ = 'required') if big_boy.is_technical_customer:
					tc =  ET.SubElement(self.root, 'TechnicalCustomer')
					org = ET.SubElement(tc, 'Organization')
					big_boy.write_xml(org)
				case IndividualEntrepreneur() | Organization() | PersonSNILS() if big_boy.is_developer:
					dev =  ET.SubElement(self.root, 'Developer')
					big_boy.write_xml(dev)
				case _:
					get_report(f'Developer | TechnicalCustomer {big_boy}', 'не удалось обработать участника')
		print('... записано')

		# ---------- Список используемых сокращений ----------
		if self.n_UsedAbbreviations:
			print('UsedAbbreviations ...', end=' ')
			abbr =  ET.SubElement(self.root, 'UsedAbbreviations')
			self.n_UsedAbbreviations.write_xml(abbr)
			print('... записано')

		# --- # Перечень документов, в результате применения которых обеспечивается  требований тех. регламентов ---
		print('UsedNorms ...', end=' ')
		used_norms = ET.SubElement(self.root, 'UsedNorms')
		for norm in self.o_UsedNorms:
			tUsedNorm = ET.SubElement(used_norms, 'UsedNorm')
			tUsedNorm.text = norm
		print('... записано')

		# ---------- Перечень документов о принятии решения о подготовке ПД ----------
		print('ProjectDecisionDocuments ...', end=' ')
		tDocuments = ET.SubElement(self.root, 'ProjectDecisionDocuments')
		for doc in self.o_ProjectDecisionDocuments:
			tDocument = ET.SubElement(tDocuments, 'Document')
			doc.write_xml(tDocument)
		print('... записано')

		# ---------- Перечень ИРД, кроме отчетной документации по результатам ИИ ----------
		print('ProjectInitialDocuments ...', end=' ')
		tDocuments = ET.SubElement(self.root, 'ProjectInitialDocuments')
		for doc in self.o_ProjectInitialDocuments:
			tDocument = ET.SubElement(tDocuments, 'Document')
			doc.write_xml(tDocument)
		print('... записано')

		# ---------- Перечень отчетной документации по результатам ИИ ----------
		if self.n_EngineeringSurveyDocuments:
			print('EngineeringSurveyDocuments ...', end=' ')
			tEngineeringSurveyDocuments = ET.SubElement(self.root, 'EngineeringSurveyDocuments')
			for doc in self.n_EngineeringSurveyDocuments:
				tDoc = ET.SubElement(tEngineeringSurveyDocuments, 'Document')
				doc.write_xml(tDoc)
			print('... записано')

		# --- Дополнительные материалы, не предусмотренные ПП РФ №87 от 16.02.2008 ---
		if self.n_AdditionalData:
			print('AdditionalData ...', end=' ')
			tAdditionalData = ET.SubElement(self.root, 'AdditionalData')
			for data in self.n_AdditionalData:
				tData = ET.SubElement(tAdditionalData, 'Data')
				data.write_xml(tData)
			print('... записано')

		# ---------- Сведения об источниках финансирования ОКС ----------
		if self.n_FinanceSources:
			print('FinanceSources ...', end=' ')
			tFinanceSources = ET.SubElement(self.root, 'FinanceSources')
			self.n_FinanceSources.write_xml(tFinanceSources)
			print('... записано')

		# ---------- Объект капитального строительства ----------
		match self.o_object:
			case LinearObject():
				print('LinearObject ...', end=' ')
				tLinearObject = ET.SubElement(self.root, 'LinearObject')
				self.o_object.write_xml(tLinearObject)
				print('... LinearObject: записано')
			case _:
				get_report('LinearObject', 'ошибка типа данных')

		# ---------- Дополнительное произвольное текстовое описание ----------
		print('DesignerNote ...', end=' ')
		for tb in self.nm_DesignerNote:
			tTextBlock = ET.SubElement(self.root, 'DesignerNote')
			tb.write_xml(tTextBlock)
		print('... записано')

		# ---------- Заверение проектной организации ----------
		print('DesignerAssurance ...', end=' ')
		tTextBlock = ET.SubElement(self.root, 'DesignerAssurance')
		self.o_DesignerAssurance.write_xml(tTextBlock)
		print('... записано')


	def write_xml(self):
		tree = ET.ElementTree(self.root)
		try:
			ET.indent(tree, space='	')
		except AttributeError:
			pass  # или использовать внешнюю библиотеку lxml
		# folder = manager.file.parent.parent / 'XML'
		# folder.mkdir(parents=True, exist_ok=True)
		# output = folder / manager.file.stem 
		# D:\01_ХРАНИЛИЩЕ\01_Работа\04_Материалы\03_Проекты\Bill_of_Quantities\XML\02_Земляное_полотно
		tree.write('output.xml', encoding='utf-8', xml_declaration=True)