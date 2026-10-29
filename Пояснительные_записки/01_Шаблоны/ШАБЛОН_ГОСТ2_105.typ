// Copyright © 2026 OldNestling
// License: GPLv3 (GNU General Public License Version 3)

// ======================================================================================
// ГОСТ Р 2.105–2019 — Оформление текстовых документов для Typst v 0.15.0 
// Данный шаблон пояснительной записки для раздела №1 проектной документации 
// линейного объекта капитального строительства (для автомобильных дорог) является частью 
// open-source проекта, репозиторий которого доступен по следующей ссылке: 
// https://github.com/OldNestling/ONP-Explanatory_Note.git
// ======================================================================================
// 

/// Функция для вычисления размера текста фамилий ячеек основной надписи при большой длине
///
/// - text (str): Фамилия
/// -> 
#let name_size(text) = {
	if text.len() > 10*2 {9pt} else {10pt}
}


/// Функция для вычисления сжатия текста фамилий ячеек основной надписи при большой длине
///
/// - text (str): Фамилия
/// -> 
#let name_tracking(text) = {
	if text.len() > 10*2 {-0.15mm} else {-0.1mm}
}


/// Основная функция выставления шаблона оформления
///
/// - body (): 
/// - ШИФР (str): полный шифр документа для основной надписи
/// - НАЧАЛЬНАЯ_СТРАНИЦА (int): номер первой страницы документа в томе 
/// - РАЗРАБОТЧИК (): подписант. строка с пустым значением не выводится
/// - ПРОВЕРИЛ (): подписант. строка с пустым значением не выводится
/// - РУКОВОДИТЕЛЬ (): подписант. строка с пустым значением не выводится
/// - НКОНТРОЛЬ (): подписант.
/// - ГИП (): подписант.
/// - РАЗРАБОТЧИК_ПОДПИСЬ (): ссылка на файл с изображением подписи
/// - ПРОВЕРИЛ_ПОДПИСЬ (): ссылка на файл с изображением подписи
/// - РУКОВОДИТЕЛЬ_ПОДПИСЬ (): ссылка на файл с изображением подписи
/// - НКОНТРОЛЬ_ПОДПИСЬ (): ссылка на файл с изображением подписи
/// - ГИП_ПОДПИСЬ (): ссылка на файл с изображением подписи
/// - ДАТА1 (): дата подписания 1 строки
/// - ДАТА2 (): дата подписания 2 строки
/// - ДАТА3 (): дата подписания 3 строки
/// - ДАТА4 (): дата подписания 4 строки
/// - ДАТА5 (): дата подписания 5 строки
/// - ИЗМ1 (int): метка 1 в основной надписи об изменениях
/// - ИЗМ1_ЛИСТ (): графа лист для изменения 1-ой строки изменения
/// - ИЗМ1_ДОК (): номер документа обоснования  для 1-ой строки изменения
/// - ИЗМ1_ДАТА (): дата изменения для 1-й строки
/// - ИЗМ2 (): метка 2 в основной надписи об изменениях
/// - ИЗМ2_ЛИСТ (): графа лист для изменения 2-ой строки изменения
/// - ИЗМ2_ДОК (): номер документа обоснования  для 2-ой строки изменения
/// - ИЗМ2_ДАТА (): дата изменения для 2-й строки
/// - ВСЕ_ЛИСТЫ (bool): флаг проставления метки изменения на всех листах документа
/// - СТРАНИЦЫ_ИЗМЕНЕНИЯ_1 (int|array): конкретные страницы для 1-й отметки изменения
/// - СТРАНИЦЫ_ИЗМЕНЕНИЯ_2 (int|array): конкретные страницы для 2-й отметки изменения
/// -> 
#let apply(
	body,
	// Данные документа
	ШИФР: "ШИФР",
	НАЧАЛЬНАЯ_СТРАНИЦА: 5,

	РАЗРАБОТЧИК: "OldNestling",
	ПРОВЕРИЛ: "",
	РУКОВОДИТЕЛЬ: "",
	НКОНТРОЛЬ: "",
	ГИП: "",

	РАЗРАБОТЧИК_ПОДПИСЬ: none,
	ПРОВЕРИЛ_ПОДПИСЬ: none,
	РУКОВОДИТЕЛЬ_ПОДПИСЬ: none,
	НКОНТРОЛЬ_ПОДПИСЬ: none,
	ГИП_ПОДПИСЬ: none,

	ДАТА1: "06.26",
	ДАТА2: "06.26",
	ДАТА3: "06.26",
	ДАТА4: "06.26",
	ДАТА5: "06.26",

	ИЗМ1: 0,
	ИЗМ1_ЛИСТ: none,
	ИЗМ1_ДОК: none,
	ИЗМ1_ДАТА: none,
	
	ИЗМ2: 0,
	ИЗМ2_ЛИСТ: none,
	ИЗМ2_ДОК: none,
	ИЗМ2_ДАТА: none,
	ВСЕ_ЛИСТЫ: false,
	СТРАНИЦЫ_ИЗМЕНЕНИЯ_1: (:),
	СТРАНИЦЫ_ИЗМЕНЕНИЯ_2: (:)
	) = {

	// ---------- Основной текст ----------
	set text(
		font: "Arial", 
		size: 12pt, 
		hyphenate: false, 
		lang: "ru"
	)
	set par(
		first-line-indent: (amount: 12.5mm, all: true),
		justify: true,
		leading: 0.5em,
		spacing: 0.5em
	)
	// ---------- выделение текста ----------
	// Пометка для внутренного пользования
	show label("проверить"): it => {
		highlight()[
			#text(fill: gradient.linear(red, blue))[#it]
		]
	}

	// Выделения текста цветом для экспертизы
	show label("изм1"): set text(fill: rgb("#1d6ac2"))
	show label("изм2"): set text(fill: rgb("#8d17db"))
	show label("изм3"): set text(fill: rgb("#df8f05"))
	show label("изм4"): set text(fill: rgb("#8f6305"))
	show label("изм5"): set text(fill: rgb("#5aad3a"))
	show label("изм6"): set text(fill: rgb("#e761a4"))
	show label("изм7"): set text(fill: rgb("#1abeae"))
	show label("изм8"): set text(fill: rgb("#243bc2"))
	show label("изм9"): set text(fill: rgb("#e41b1b"))


	// ---------- Заголовки ----------
	set heading(numbering: "1.1")

	// Стили для разных уровней
	show heading.where(level: 1): it => {
		set text(size: 16pt, weight: "bold")
		set par(first-line-indent: 0mm, justify: true, leading: 3mm)
		block(inset: (left: 12.5mm), it)
	}
	show heading.where(level: 2): it => {
		set text(size: 15pt, weight: "bold")
		set par(first-line-indent: 0mm, justify: true, leading: 3mm)
		block(inset: (left: 12.5mm), it)
	}
	show heading.where(level: 3): it => {
		set text(size: 14pt, weight: "bold")
		set par(first-line-indent: 12.5mm, justify: true)
		block(inset: (left: 12.5mm), it)
	}

		show heading.where(level: 4): it => {
		set text(size: 12pt, weight: "bold")
		set par(first-line-indent: 12.5mm, justify: true)
		block(inset: (left: 12.5mm), underline()[#it])
	}

	// Вертикальные отступы вокруг всех заголовков уровня 1-4
	show heading: it => {
		block(above: 16pt, below: 16pt, breakable: false, it)
	}

		show heading.where(level: 5): it => {
		set text(size: 12pt, weight: "bold")
		set par(first-line-indent: 12.5mm, justify: true)
		block(inset: (left: 12.5mm), below: 0.5em, it)
	}

		show heading.where(level: 6): it => {
		set text(size: 12pt, weight: "regular")
		set par(first-line-indent: 12.5mm, justify: true)
		block(inset: (left: 0mm), below: 0.5em, it)
	}

	// ---------- Списки  ----------
	set list(
		marker: "-",
		indent: 12.5mm,		// сдвиг всего списка вправо
		body-indent: 4mm,	// расстояние от маркера до текста
		spacing: 0.5em,		// интервал между пунктами
	)

	set enum(
		indent: 12.5mm,		// сдвиг всего списка вправо
		body-indent: 4mm,	// расстояние от маркера до текста
		spacing: 0.5em		// интервал между пунктами
	)

	set figure(numbering: "1", supplement: "Рисунок", )
	show link: set text(fill: blue, weight: 700)
	//show link: underline // чтобы в содержании не было подчёркиваний

	// ---------- Таблицы  ----------
	show figure: set block(breakable: true)

	// Базовая таблица: рамка только сверху/снизу, отступы, выравнивание
	set table(
		align: center + horizon,
		stroke: 0.5pt,
		gutter: 0pt,
		inset: 3pt,
	)
	// Заголовки таблицы – полужирные (альтернатива двойной линии)
	show table.header: set text(weight: "bold")
	show table: set par(justify: false)	// вырванивание по ширине
	
	// Подписи таблиц: "Таблица 1 — ..." над таблицей, выравнивание по левому краю, отступы
	set figure(kind: "table", numbering: "1", supplement: none)
	show figure.where(kind: "table"): it => {
		let caption_text = {
			let num = it.counter.display(it.numbering)
			if it.caption != none {
				heading("Таблица " + num + " — " + it.caption.body, level: 6, numbering: none)
			} else {
				"Таблица " + num
			}
		}
		// Выравнивание по левому краю через align(), отступы через block()
		align(left)[
			#block(
				breakable: true,
				inset: (bottom: 0mm, top: 5mm, left: 1mm),
				text(size: 13pt, caption_text)
			)
		]
		it.body + v(2.5mm)
	}

	// ---------- Рисунки  ----------
	set figure(
		caption: "Рисунок",
		numbering: "1",
		supplement: "Рисунок",
	)

	// Подрисуночный текст – слово "Рисунок", номер, тире, наименование (п. 6.9.4)
	show figure.caption: it => {
		if it.counter != none {
			let num = it.counter.display(it.numbering)
			heading([Рисунок #num — #it.body], level: 6, numbering: none)
		} else {
			it.body
		}
		block(above: 1.2em, below: 0.8em, breakable: false)
	}

	// ---------- Формулы  ----------
	// Формулы по центру, номер справа в круглых скобках
	set math.equation(numbering: "(1)", supplement: "формуле")

	// Применяем вертикальные отступы ТОЛЬКО к выключным формулам
	show math.equation.where(block: true): it => {
		block(above: 0.5em, below: 0.5em, it)
	}


	// ===================== Рамка и штампы по ГОСТ =====================
	set page(
		paper: "a4",
		margin: (left: 25mm, right: 11mm, top: 18mm, bottom: 25mm),
		background: context {

		// Определяем номер страницы (1, 2, ...)
		let current_page = counter(page).get().first()
		let current_docpage = -1+current_page+НАЧАЛЬНАЯ_СТРАНИЦА
		let total-pages = counter(page).final().first()
	
		// Размеры страницы
		let page_width = 210mm
		let page_height = 297mm

		// Отступы для внутренней рамки (одинаковые для всех листов)
		let left_margin = 20mm
		let right_margin = 5mm
		let top_margin = 5mm
		let bottom_margin = 5mm

		// Координаты основной рамки (одинаковы для всех страниц)
		let frame_left = left_margin
		let frame_top = top_margin
		let frame_width = page_width - left_margin - right_margin
		let frame_height = page_height - top_margin - bottom_margin

		// Рисуем основную рамку
		place(
			left + top,
			dx: frame_left,
			dy: frame_top,
			rect(
			width: frame_width,
			height: frame_height,
			stroke: 0.5mm,
			fill: none
			)
		)

	// Рисуем ячейку с номером страницы
		place(
			left + top,
			dx: 195mm,
			dy: 5mm,
			table(
				stroke: 0.5mm,
				columns: (10mm),
				rows: (7mm),
				inset: 1pt,
				align: horizon,
			table.cell(align: center)[#current_docpage]
			)
		)

		// Дополнительные графы
		place(
			left + top,
			dx: -28.5mm,
			dy: 243.5mm,
			rotate(
				-90deg,
				table(
						stroke: 0.5mm,
						columns: (25mm, 35mm, 25mm),
					rows: (5mm, 7mm),
					table.header(
						[#text(size: 10pt)[Инв. № подп.]], 
						[#text(size: 10pt)[Подп. и дата]], 
						[#text(size: 10pt)[Взам. инв. №]]
					),
					[],[],[]
				),
			)
		)


		if current_page == 1 {
			// Таблица для первого листа
			let table_height = 40mm
			let table_left_offset = 20mm
			let table_bottom_offset = 5mm
			let table_width = frame_width - table_left_offset

			let table_x = frame_left + table_left_offset
			let table_y = frame_top + frame_height - table_bottom_offset - table_height

			// Внешняя рамка таблицы

			place(
				left + top,
				dx: 20mm,
				dy: 297mm-45mm,
				table(
					stroke: 0.5mm,
					columns: (10mm, 10mm, 10mm, 10mm, 15mm, 10mm, 70mm, 15mm, 15mm, 20mm),
					rows: (5mm, 5mm, 5mm, 5mm, 5mm, 5mm, 5mm, 5mm),
					inset: 1pt,
					align: horizon,

					// Строка 1 (изменение 2)
					table.cell(align: center)[#text(size: 10pt)[#if ИЗМ2 == 0 {none} else {ИЗМ2}]],	// 1 столбец
					table.cell(align: center)[#if ИЗМ2 > 0 {"-"} else {none}],											// 2 столбец
					table.cell(align: center)[#text(size: 10pt)[#ИЗМ2_ЛИСТ]],												// 3 столбец
					table.cell(align: center)[#text(size: 10pt)[#ИЗМ2_ДОК]],												// 4 столбец
					table.cell(align: center)[],																										// 5 столбец
					table.cell(align: center)[#text(size: 10pt)[#ИЗМ2_ДАТА]], 											// 6 столбец

					table.cell(colspan: 4, rowspan: 3, align: center)[*#ШИФР*],

					// Строка 2 (изменение 1)
					table.cell(align: center)[#text(size: 10pt)[#if ИЗМ1 == 0 {none} else {ИЗМ1}]], 
					table.cell(align: center)[#if ИЗМ1 > 0 {"-"} else {none}],
					table.cell(align: center)[#text(size: 10pt)[#ИЗМ1_ЛИСТ]],
					table.cell(align: center)[#text(size: 10pt)[#ИЗМ1_ДОК]],
					table.cell(align: center)[],
					table.cell(align: center)[#text(size: 10pt)[#ИЗМ1_ДАТА]],
					
					// Строка 3
					text(size: 10pt)[Изм.],text(tracking: -0.3mm, size: 10pt)[Кол.уч.],
					table.cell(align: center)[#text(size: 10pt)[Лист]],
					text(tracking: -0.41mm, size: 10pt)[№ док.],
					table.cell(align: center)[#text(size: 10pt)[Подп.]],
					table.cell(align: center)[#text(size: 10pt)[Дата]],

					// 1 строка подписанта
						// Должность
					table.cell(colspan: 2)[#text(size: 10pt)[#if РАЗРАБОТЧИК.len() > 0 {"Разраб."} else {}]],
						// Фамилия
					table.cell(colspan: 2)[#text(size: name_size(РАЗРАБОТЧИК), tracking: name_tracking(РАЗРАБОТЧИК))[#РАЗРАБОТЧИК]],		
						// Подпись
					[#align(center)[#РАЗРАБОТЧИК_ПОДПИСЬ]],
						// Дата
					table.cell(align: center)[#text(size: 10pt)[#if РАЗРАБОТЧИК.len() > 0 {ДАТА1} else {}]],

					table.cell(rowspan: 5, align: center)[*Пояснительная записка*],

					table.cell(align: center)[#text(size: 10pt)[Стадия]], 
					table.cell(align: center)[#text(size: 10pt)[Лист]], 
					table.cell(align: center)[#text(size: 10pt)[Листов]],

					// 2 строка подписанта
					table.cell(colspan: 2)[#text(size: 10pt)[#if ПРОВЕРИЛ.len() > 0 {"Проверил"} else {}]],
					table.cell(colspan: 2)[#text(size: name_size(ПРОВЕРИЛ), tracking: name_tracking(ПРОВЕРИЛ))[#ПРОВЕРИЛ]],
					[#align(center)[#ПРОВЕРИЛ_ПОДПИСЬ]],
					table.cell(align: center)[#text(size: 10pt)[#if ПРОВЕРИЛ.len() > 0 {ДАТА2} else {}]],

					table.cell(align: center)[#text(size: 10pt)[П]], 
					table.cell(align: center)[#text(size: 10pt)[#current_page]], 
					table.cell(align: center)[#text(size: 10pt)[#total-pages]],

					// 3 строка подписанта
					table.cell(colspan: 2)[#text(size: 10pt)[#if РУКОВОДИТЕЛЬ.len() > 0 {"Нач.гр."} else {}]],
					table.cell(colspan: 2)[#text(size: name_size(РУКОВОДИТЕЛЬ), tracking: name_tracking(РУКОВОДИТЕЛЬ))[#РУКОВОДИТЕЛЬ]], 
					[#align(center)[#РУКОВОДИТЕЛЬ_ПОДПИСЬ]], 
					table.cell(align: center)[#text(size: 10pt)[#if РУКОВОДИТЕЛЬ.len() > 0 {ДАТА3} else {}]], 
					
					// Ячейка организации
					table.cell(colspan: 3, rowspan: 3)[#image("Лого.jpg")],

					// 4 строка подписанта
					table.cell(colspan: 2)[#text(size: 10pt)[Н.контр.]],
					table.cell(colspan: 2)[#text(size: name_size(НКОНТРОЛЬ), tracking: name_tracking(НКОНТРОЛЬ))[#НКОНТРОЛЬ]],
					[#align(center)[#НКОНТРОЛЬ_ПОДПИСЬ]], 
					table.cell(align: center)[#text(size: 10pt)[#ДАТА4]],

					// 5 строка подписанта
					table.cell(colspan: 2)[#text(size: 10pt)[ГИП]],
					table.cell(colspan: 2)[#text(size: name_size(ГИП), tracking: name_tracking(ГИП))[#ГИП]],
					[#align(center)[#ГИП_ПОДПИСЬ]], 
					table.cell(align: center)[#text(size: 10pt)[#ДАТА5]]
				)
			)
		} else {
			// Основная надпись (таблица) для остальных страниц
			let table_height = 20mm
			let table_left_offset = 10mm
			let table_bottom_offset = 5mm
			let table_width = frame_width - table_left_offset

			let table_x = frame_left + table_left_offset
			let table_y = frame_top + frame_height - table_bottom_offset - table_height

			place(
				left + top,
				dx: 20mm,
				dy: 297mm-20mm,
				table(
					stroke: 0.5mm,
					columns: (10mm, 10mm, 10mm, 10mm, 15mm, 10mm, 110mm, 10mm),
					rows: (5mm, 5mm, 5mm),
					inset: 1pt,
					align: horizon,

					// Строка 1 (изменение 2)
					table.cell(align: center)[#text(size: 10pt)[#if ВСЕ_ЛИСТЫ {if ИЗМ2 == 0 {none} else {ИЗМ2}} else {}]],
					table.cell(align: center)[#if ВСЕ_ЛИСТЫ {if ИЗМ2 > 0 {"-"} else {none}} else {}],
					table.cell(align: center)[#text(size: 10pt)[#if ВСЕ_ЛИСТЫ {ИЗМ2_ЛИСТ} else {}]],
					table.cell(align: center)[#text(size: 10pt)[#if ВСЕ_ЛИСТЫ {ИЗМ2_ДОК} else {}]],
					table.cell(align: center)[],
					table.cell(align: center)[#text(size: 10pt)[#if ВСЕ_ЛИСТЫ {ИЗМ2_ДАТА} else {}]], 
					
					table.cell(rowspan: 3, align: center)[*#ШИФР*], table.cell(align: center)[#text(size: 10pt)[Лист]],

					// Строка 2 (изменение 1)
					table.cell(align: center)[#text(size: 10pt)[#if ВСЕ_ЛИСТЫ {if ИЗМ1 == 0 {none} else {ИЗМ1}} else {}]],
					table.cell(align: center)[#if ВСЕ_ЛИСТЫ {if ИЗМ1 > 0 {"-"} else {none}} else {}],
					table.cell(align: center)[#text(size: 10pt)[#if ВСЕ_ЛИСТЫ {ИЗМ1_ЛИСТ} else {}]],
					table.cell(align: center)[#text(size: 10pt)[#if ВСЕ_ЛИСТЫ {ИЗМ1_ДОК} else {}]],
					table.cell(align: center)[], 
					table.cell(align: center)[#text(size: 10pt)[#if ВСЕ_ЛИСТЫ {ИЗМ1_ДАТА} else {}]], 
					
					table.cell(rowspan: 2, align: center)[#current_page],
					// Строка 3
					table.cell(align: center)[#text(size: 10pt)[Изм.]], 
					table.cell(align: center)[#text(tracking: -0.01em, size: 9pt)[Кол.уч.]], 
					table.cell(align: center)[#text(size: 10pt)[Лист]], 
					table.cell(align: center)[#text(tracking: -0.43mm, size: 10pt)[№ док.]], 
					table.cell(align: center)[#text(size: 10pt)[Подп.]], 
					table.cell(align: center)[#text(size: 10pt)[Дата]]
				)
			)
		}

		// Размещение в основной надписи пометки об изменениях на заданных страницах
		let pages_1 = (СТРАНИЦЫ_ИЗМЕНЕНИЯ_1, ).flatten()

		
		if current_page != 1 and current_page in pages_1 {
			place(
				bottom + left,
				dx: 24mm,
				dy: -11mm,

				grid(
					columns: (7mm, 3mm, 5.6mm, 3mm, 15.5mm, 0mm),
			    gutter: 10pt,
			    text(size: 10pt)[#ИЗМ1],
			    [#if ИЗМ1 > 0 {"-"} else {none}],
			    text(size: 10pt)[#ИЗМ1_ЛИСТ],
			    text(size: 10pt)[#ИЗМ1_ДОК],
			    [],
			    text(size: 10pt)[#ИЗМ1_ДАТА]
				),
			)
		}

		let pages_2 = (СТРАНИЦЫ_ИЗМЕНЕНИЯ_2, ).flatten() 


		if current_page != 1 and current_page in pages_2 {
			place(
				bottom + left,
				dx: 24mm,
				dy: -16mm,

				grid(
					columns: (7mm, 3mm, 5.6mm, 3mm, 15.5mm, 0mm),
			    gutter: 10pt,
			    text(size: 10pt)[#ИЗМ2],
			    [#if ИЗМ2 > 0 {"-"} else {none}],
			    text(size: 10pt)[#ИЗМ2_ЛИСТ],
			    text(size: 10pt)[#ИЗМ2_ДОК],
			    [],
			    text(size: 10pt)[#ИЗМ2_ДАТА]
				),
			)
		}
	}
)

body
}
	