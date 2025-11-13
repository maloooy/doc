import datetime
import PySimpleGUI as sg
import recognizing
import database

recording_const = False
buttons_visible = False

help_text = """
    Программа "Голосовой помощник врача" предназначена для упрощения работы докторов, избавления их от лишней ручной работы. 
    С её помощью вам будет удобнее вести учёт медицинских карт, добавлять пациентов и изменять о них информацию.

    Приветственное меню показывает основные функции, доступные при работе, такие как функция добавления пациента и открытие списка пациентов. 

    При нажатии на кнопку "Добавить пациента" откроется окно добавления пациента, в котором необходимо ввести всю информацию о пациенте. После заполнения 
    всех полей необходимо нажать кнопку "Добавить" и информация о пациенте будет добавлена в базу данных, о чём будет сказано с помощью уведомления. 

    При нажатии на кнопку "Список пациентов" открывается окно, в котором расположены карточки всех пациентов.
    Также здесь находится поиск, который осуществляется по любому введённому полю, будь то ФИО, дата рождения или паспорт.

    При нажатии на кнопку "Обновить" происходит обновление таблицы пациентов, которое пригодится в том случае, если были внесены какие то изменения 
    в карточках пациентов и они не отображаются.

    Для того чтобы открыть карточку нужного пациента, необходимо нажать на него в таблице. В этом случае откроется ещё одно окно "Карточка пациента". 
    Расскажем о нём поподробнее.

     В этом окне отображается вся информация по выбранному ранее пациенту, такая как:
     - Номер медицинской карты пациента. 
     - Фамилия, Имя, Отчество 
     - Дата рождения
     - Пол
     - Паспорт
     - Рост, Вес
     - Жалобы, Осмотр, Диагноз, Лечение
     - Дата приёма

     Также в окне расположены несколько типов кнопок:
     - Кнопки "Сохранить" и "Закрыть": Кнопки для сохранения изменений и закрытия окна. 
     - Кнопка "Изменить метод записи": Переключает метод записи данных (либо заполняется полностью карточка, либо по каждому полю отдельно). 
     - Кнопка "Удалить пациента": Удаляет пациента. 
     - Кнопка ⚙ нужна для ручного выбора даты.
     - Кнопка ⭕ отвечает за начало записи голоса. В режиме "Каждое поле отдельно" она находится возле каждого поля и отвечает за его заполнение.
       В режиме "Все поля вместе" на экране находится только одна такая кнопка, которая отвечает за заполнение всей карточки целиком. 
       Текущий режим записи отображается рядом с кнопкой смены режима.
     - Кнопка ❌ очищает те поля, возле которых находится, т.е. "Жалобы", "Осмотр", "Диагноз" и "Лечение" соответственно.

     В зависимости от выбранного режима записи, заполнение карточки пациента будет проходить по разному. По умолчанию при запуске программы данные записываются
     для каждого поля отдельно. В этом случае при нажатии на кнопку возле определённого поля, начнётся запись вашего голоса, что будет показано на экране.
     Например : "ИДЁТ ЗАПИСЬ В ПОЛЕ "Дата рождения" ". Для завершения записи голоса нужно повторно нажать на кнопку, индикатор погаснет и можно будет 
     продолжать работу.

     Если выбран режим записи "Все поля вместе", то при нажатии на кнопку начнётся голосовое сопровождение, которое поможет заполнить карточку пациента.

     При записи таких полей как "Диагноз" и "Лечение" есть возможность выбрать заболевание и необходимые лекарства из выпадающих списков под каждым полем.
     Если необходимая вам болезнь или лекарство не было найдено, пишите на почту basargin123@gmail.com и я добавлю их в базу данных.

     Если в процессе работы распознавателя были допущены какие то ошибки, то их легко можно исправить записав заново отдельное поле, или же вручную,
     просто вписав необходимую информацию в нужное поле.

     Для лучшего качества распознавания информации советуем придерживаться следующих правил:
     - При записи номера паспорта, говорить по 2 цифры, отделяя ноль. 
     Например, номер "2345 056493" лучше сказать как "двадцать три_сорок пять_ноль_пять_шестьдесят четыре_девяносто три".
     - При записи даты рождения и даты приёма, сначала нужно говорить год, потом месяц и день, разделяя их знаками "тире". 
     Например, дату "1988-11-12" лучше сказать как "тысяча девятьсот восемьдесят восемь_тире_одиннадцать_тире_двенадцать".
     - Если при записи таких полей как "Жалобы", "Осмотр", "Диагноз" и "Лечение" вам понадобилось использовать знаки препинания, то просто проговаривайте их.
     Например, текст "Сонливость, апатия, грусть." лучше сказать как "Сонливость_запятая_апатия_запятая_грусть_точка".
     - Для выбора пола необходимо просто сказать "мужской" или "женский".
        """


def show_patient_details(patient):
    global buttons_visible
    sex_default = 'муж' if patient[4] == 'муж' else 'жен'
    layout = [
        [sg.Text('Медицинская карта №', font='Helvetica 11 bold'), sg.Text(patient[0], font='Helvetica 17'),
         sg.Button('⭕', button_color=('red', 'gray94'), key='whole_card', border_width=0, disabled_button_color=("gray94", "gray94"), disabled=True,
                   mouseover_colors=('red', 'gray94')),
         sg.Button('Изменить метод записи', pad=((100, 0), (0, 0)), key='method'),
         sg.Text('Текущий метод записи:'), sg.Text('Каждое поле отдельно', size=(20, 1), key='record_type', font='Helvetica 10 underline'),
         sg.Button('Удалить пациента', pad=((75, 0), (0, 0)))],
        [sg.Text('Фамилия', font='Helvetica 11 bold'),
         sg.Multiline(patient[1], no_scrollbar=True, size=(20, 1), key='-SURNAME-'),
         sg.Button('⭕', button_color=('red', 'gray94'), key='surname', border_width=0, disabled_button_color=("gray94", "gray94"),
                   mouseover_colors=('red', 'gray94')),
         sg.Text('Имя', font='Helvetica 11 bold'),
         sg.Multiline(patient[2], no_scrollbar=True, size=(20, 1), key='-NAME-'),
         sg.Button('⭕', button_color=('red', 'gray94'), key='name', border_width=0, disabled_button_color=("gray94", "gray94"),
                   mouseover_colors=('red', 'gray94')),
         sg.Text('Отчество', font='Helvetica 11 bold'),
         sg.Multiline(patient[3], no_scrollbar=True, size=(20, 1), key='-PATRONYMIC-'),
         sg.Button('⭕', button_color=('red', 'gray94'), key='patronymic', border_width=0, disabled_button_color=("gray94", "gray94"),
                   mouseover_colors=('red', 'gray94')),
         sg.Text('', text_color='gray94', key='check_load_1', pad=((100, 0), (0, 0)))],
        [sg.Text('Дата рождения', font='Helvetica 11 bold'),
         sg.CalendarButton('⚙', target='-DATE_OF_BIRTH-', format='%Y-%m-%d', no_titlebar=False, title='Выбор даты', begin_at_sunday_plus=1,
                           default_date_m_d_y=(1, 1, 2000),
                           month_names=('Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'),
                           day_abbreviations=('Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб')),
         sg.Multiline(patient[5], no_scrollbar=True, size=(10, 1), key='-DATE_OF_BIRTH-'),
         sg.Button('⭕', button_color=('red', 'gray94'), key='date_of_birth', border_width=0, disabled_button_color=("gray94", "gray94"),
                   mouseover_colors=('red', 'gray94')),
         sg.Text('Пол', font='Helvetica 11 bold'),
         sg.Radio('муж', 'RADIO1', default=(sex_default == 'муж'), key='-SEX-M-'),
         sg.Radio('жен', 'RADIO1', default=(sex_default == 'жен'), key='-SEX-F-'),
         sg.Button('⭕', button_color=('red', 'gray94'), key='sex', border_width=0, disabled_button_color=("gray94", "gray94"),
                   mouseover_colors=('red', 'gray94')),
         sg.Text('', justification='right', text_color='gray94', key='check_load_2', pad=((420, 0), (0, 0)))],
        [sg.Text('Паспорт', font='Helvetica 11 bold'),
         sg.Multiline(patient[6], no_scrollbar=True, size=(15, 1), key='-PASSPORT-'),
         sg.Button('⭕', button_color=('red', 'gray94'), key='passport', border_width=0, disabled_button_color=("gray94", "gray94"),
                   mouseover_colors=('red', 'gray94')),
         sg.Text('Рост', font='Helvetica 11 bold'),
         sg.Multiline(patient[8], no_scrollbar=True, size=(5, 1), key='-HEIGHT-'),
         sg.Button('⭕', button_color=('red', 'gray94'), key='height', border_width=0, disabled_button_color=("gray94", "gray94"),
                   mouseover_colors=('red', 'gray94')),
         sg.Text('Вес', font='Helvetica 11 bold'),
         sg.Multiline(patient[9], no_scrollbar=True, size=(5, 1), key='-WEIGHT-'),
         sg.Button('⭕', button_color=('red', 'gray94'), key='weight', border_width=0, disabled_button_color=("gray94", "gray94"),
                   mouseover_colors=('red', 'gray94'))],
        [sg.Text('Жалобы', font='Helvetica 11 bold'), sg.Text('Осмотр', font='Helvetica 11 bold', pad=((480, 0), (0, 0)))],
        [sg.Multiline(patient[10], no_scrollbar=True, size=(70, 7), key='-COMPLAINTS-', enable_events=True),
         sg.Column([[sg.Button('⭕', button_color=('red', 'gray94'), key='complaints', border_width=0,
                               disabled_button_color=("gray94", "gray94"), mouseover_colors=('red', 'gray94'))],
                    [sg.Button('❌', button_color=('red', 'gray94'), key='clear_complaints', border_width=0,
                               disabled_button_color=("gray94", "gray94"), mouseover_colors=('red', 'gray94'))]]),
         sg.Multiline(patient[11], no_scrollbar=True, size=(70, 7), key='-INSPECTION-', enable_events=True),
         sg.Column([[sg.Button('⭕', button_color=('red', 'gray94'), key='inspection', border_width=0,
                               disabled_button_color=("gray94", "gray94"), mouseover_colors=('red', 'gray94'))],
                    [sg.Button('❌', button_color=('red', 'gray94'), key='clear_inspection', border_width=0,
                               disabled_button_color=("gray94", "gray94"), mouseover_colors=('red', 'gray94'))]])],
        [sg.Text('Диагноз', font='Helvetica 11 bold'), sg.Text('Лечение', font='Helvetica 11 bold', pad=((485, 0), (0, 0)))],
        [sg.Multiline(patient[12], no_scrollbar=True, size=(70, 7), key='-DIAGNOSIS-', enable_events=True),
         sg.Column([[sg.Button('⭕', button_color=('red', 'gray94'), key='diagnosis', border_width=0,
                               disabled_button_color=("gray94", "gray94"), mouseover_colors=('red', 'gray94'))],
                    [sg.Button('❌', button_color=('red', 'gray94'), key='clear_diagnosis', border_width=0,
                               disabled_button_color=("gray94", "gray94"), mouseover_colors=('red', 'gray94'))]]),
         sg.Multiline(patient[13], no_scrollbar=True, size=(70, 7), key='-THERAPY-', enable_events=True),
         sg.Column([[sg.Button('⭕', button_color=('red', 'gray94'), key='therapy', border_width=0,
                               disabled_button_color=("gray94", "gray94"), mouseover_colors=('red', 'gray94'))],
                    [sg.Button('❌', button_color=('red', 'gray94'), key='clear_therapy', border_width=0,
                               disabled_button_color=("gray94", "gray94"), mouseover_colors=('red', 'gray94'))]])],
        [sg.Combo(values=[], size=(68, 1), key='disease_select', enable_events=True, readonly=True, auto_size_text=False),
         sg.Combo(values=[], size=(68, 1), key='medicine_select', enable_events=True, readonly=True, auto_size_text=False, pad=((52, 0), (0, 0)))],
        [sg.Button('Сохранить'),
         sg.Button('Закрыть'),
         sg.Text('Дата приёма', font='Helvetica 11 bold', pad=((600, 0), (0, 0))),
         sg.CalendarButton('⚙', target='-DATE_OF_RECEIPT-', format='%Y-%m-%d', no_titlebar=False, title='Выбор даты', begin_at_sunday_plus=1,
                           month_names=('Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'),
                           day_abbreviations=('Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб')),
         sg.Multiline(patient[7], no_scrollbar=True, size=(10, 1), key='-DATE_OF_RECEIPT-'),
         sg.Button('⭕', button_color=('red', 'gray94'), key='date_of_receipt', border_width=0, disabled_button_color=("gray94", "gray94"),
                   mouseover_colors=('red', 'gray94'))]]
    window = sg.Window('Карточка пациента', layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Закрыть':
            break
        elif event == 'Сохранить':
            surname = values['-SURNAME-']
            name = values['-NAME-']
            patronymic = values['-PATRONYMIC-']
            date_of_birth = values['-DATE_OF_BIRTH-']
            passport = values['-PASSPORT-']
            sex = 'муж' if values['-SEX-M-'] else 'жен'
            height = values['-HEIGHT-']
            weight = values['-WEIGHT-']
            complaints = values['-COMPLAINTS-']
            inspection = values['-INSPECTION-']
            diagnosis = values['-DIAGNOSIS-']
            therapy = values['-THERAPY-']
            date_of_receipt = values['-DATE_OF_RECEIPT-']
            database.update_patient(patient[0], surname, name, patronymic, sex, date_of_birth, passport,
                                    height, weight, complaints, inspection, diagnosis, therapy, date_of_receipt)
            sg.popup('Данные сохранены!')
            break
        elif event == 'method':
            buttons_visible = not buttons_visible
            keys_to_update = [
                'surname', 'name', 'patronymic', 'date_of_birth', 'sex', 'passport',
                'height', 'weight', 'complaints', 'clear_complaints', 'inspection',
                'clear_inspection', 'diagnosis', 'clear_diagnosis', 'therapy',
                'clear_therapy', 'date_of_receipt'
            ]
            for key in keys_to_update:
                window[key].update(disabled=buttons_visible)
            window['whole_card'].update(disabled=not buttons_visible)
            if buttons_visible:
                text = 'Все поля вместе'
            else:
                text = 'Каждое поле отдельно'
            window['record_type'].update(value=text)
        elif event == 'Удалить пациента':
            database.remove_patient(patient[0])
            sg.popup('Пациент успешно удалён!')
            break
        elif event == 'surname':
            if not recognizing.button_state:
                window['-SURNAME-'].update(value='')
            recognizing.start_record(window, '-SURNAME-')
        elif event == 'name':
            if not recognizing.button_state:
                window['-NAME-'].update(value='')
            recognizing.start_record(window, '-NAME-')
        elif event == 'date_of_birth':
            if not recognizing.button_state:
                window['-DATE_OF_BIRTH-'].update(value='')
            recognizing.start_record(window, '-DATE_OF_BIRTH-')
        elif event == 'patronymic':
            if not recognizing.button_state:
                window['-PATRONYMIC-'].update(value='')
            recognizing.start_record(window, '-PATRONYMIC-')
        elif event == 'passport':
            if not recognizing.button_state:
                window['-PASSPORT-'].update(value='')
            recognizing.start_record(window, '-PASSPORT-')
        elif event == 'sex':
            recognizing.start_record(window, '-SEX-M-')
        elif event == 'height':
            if not recognizing.button_state:
                window['-HEIGHT-'].update(value='')
            recognizing.start_record(window, '-HEIGHT-')
        elif event == 'weight':
            if not recognizing.button_state:
                window['-WEIGHT-'].update(value='')
            recognizing.start_record(window, '-WEIGHT-')
        elif event == 'complaints':
            recognizing.start_record(window, '-COMPLAINTS-')
        elif event == 'clear_complaints':
            window['-COMPLAINTS-'].update(value='')
        elif event == 'clear_inspection':
            window['-INSPECTION-'].update(value='')
        elif event == 'clear_diagnosis':
            window['-DIAGNOSIS-'].update(value='')
        elif event == 'clear_therapy':
            window['-THERAPY-'].update(value='')
        elif event == 'inspection':
            recognizing.start_record(window, '-INSPECTION-')
        elif event == 'diagnosis':
            recognizing.start_record(window, '-DIAGNOSIS-')
        elif event == 'therapy':
            recognizing.start_record(window, '-THERAPY-')
        elif event == 'date_of_receipt':
            if not recognizing.button_state:
                window['-DATE_OF_RECEIPT-'].update(value='')
            recognizing.start_record(window, '-DATE_OF_RECEIPT-')
        elif event == '-DIAGNOSIS-':
            text = values['-DIAGNOSIS-'].strip()
            if text:
                prefix = text.split()[-1]
                diseases = database.get_diseases(prefix)
                window['disease_select'].update(values=diseases)
                if diseases:
                    window['disease_select'].update(set_to_index=0)
        elif event == 'disease_select':
            selected_disease = values['disease_select']
            current_text = values['-DIAGNOSIS-'].strip()
            if current_text:
                words = current_text.split()
                if words:
                    last_word = words[-1]
                    if last_word.lower() == selected_disease[:len(last_word)].lower():
                        words[-1] = selected_disease
                    else:
                        words.append(selected_disease)
                else:
                    words.append(selected_disease)
                new_text = ' '.join(words)
            else:
                new_text = selected_disease
            window['-DIAGNOSIS-'].update(new_text)
        elif event == '-THERAPY-':
            text = values['-THERAPY-'].strip()
            if text:
                prefix = text.split()[-1]
                medicines = database.get_medicines(prefix)
                window['medicine_select'].update(values=medicines)
                if medicines:
                    window['medicine_select'].update(set_to_index=0)
        elif event == 'medicine_select':
            selected_medicine = values['medicine_select']
            current_text = values['-THERAPY-'].strip()
            if current_text:
                words = current_text.split()
                if words:
                    # Соединяем все слова введенного текста
                    current_text_joined = ' '.join(words)
                    # Проверяем, начинается ли выбранное лекарство с введенного текста (игнорируем регистр)
                    if selected_medicine.lower().startswith(current_text_joined.lower()):
                        new_text = selected_medicine
                    else:
                        new_text = current_text_joined + ' ' + selected_medicine
                else:
                    new_text = selected_medicine
            else:
                new_text = selected_medicine
            window['-THERAPY-'].update(new_text)
        elif event == 'whole_card':
          #  keys_to_update = [
           #     '-SURNAME-', '-NAME-', '-DATE_OF_BIRTH-', '-PATRONYMIC-', '-PASSPORT-',
          #      '-HEIGHT-', '-WEIGHT-', '-COMPLAINTS-', '-INSPECTION-', '-DIAGNOSIS-',
          #      '-THERAPY-', '-DATE_OF_RECEIPT-'
         #   ]
           # for key in keys_to_update:
          #      window[key].update(value='')
          #  window['-SEX-M-'].update(value=False)
          #  window['-SEX-F-'].update(value=False)
            recognizing.start_record_multi(window)

    window.close()


def show_patient_data_window():
    patients = database.get_all_patients()
    table_data = [[patient[0], patient[1] + " " + patient[2] + " " + patient[3], patient[5], patient[6]] for patient in patients]
    column_widths = [5, 45, 15, 15]
    layout = [
        [sg.Text('Данные пациентов', font='Helvetica 16'), sg.Text('Поиск', pad=((250, 0), (0, 0))),
         sg.InputText(size=(30, 1), enable_events=True, key='search')],
        [sg.Table(values=table_data, headings=['№', 'ФИО', 'Дата рождения', 'Паспорт'], key='-TABLE-', auto_size_columns=False,
                  enable_events=True, col_widths=column_widths, justification="center", num_rows=15)],
        [sg.Button('Обновить'), sg.Button('Закрыть')]
    ]
    window = sg.Window('Данные пациентов', layout, size=(800, 400))

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Закрыть'):
            break
        elif event == '-TABLE-':
            if values['-TABLE-']:
                selected_row = values['-TABLE-'][0]
                selected_patient = patients[selected_row]
                show_patient_details(selected_patient)
        elif event == 'Обновить':
            patients = database.get_all_patients()
            table_data = [[patient[0], patient[1] + " " + patient[2] + " " + patient[3], patient[5], patient[6]] for patient in patients]
            window['-TABLE-'].update(values=table_data)
        elif event == 'search':
            patients = database.find_patient(values['search'])
            table_data = [[patient[0], patient[1] + " " + patient[2] + " " + patient[3], patient[5], patient[6]] for patient in patients]
            window['-TABLE-'].update(values=table_data)

    window.close()


def show_add_patient_window():
    layout = [
        [sg.Text('Добавление пациента', font='Helvetica 16')],
        [sg.Text('Фамилия:'), sg.InputText(key='-SURNAME-', size=(30, 1))],
        [sg.Text('Имя:'), sg.InputText(key='-NAME-', size=(30, 1))],
        [sg.Text('Отчество:'), sg.InputText(key='-PATRONYMIC-', size=(30, 1))],
        [sg.Text('Пол'), sg.Radio('мужской', 'gen', key='-MALE-'), sg.Radio('женский', 'gen', key='-FEMALE-')],
        [sg.Text('Рост:'), sg.InputText(key='-HEIGHT-', size=(7, 1)), sg.Text('Вес:'), sg.InputText(key='-WEIGHT-', size=(7, 1))],
        [sg.Text('Дата рождения:'), sg.InputText(key='-DATE_OF_BIRTH-', size=(15, 1))],
        [sg.Text('Паспорт:'), sg.InputText(key='-PASSPORT-', size=(20, 1))],
        [sg.Button('Добавить'), sg.Button('Отмена')]
    ]
    window = sg.Window('Добавление пациента', layout, size=(300, 300))
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Отмена':
            break
        elif event == 'Добавить':
            surname = values['-SURNAME-']
            name = values['-NAME-']
            patronymic = values['-PATRONYMIC-']
            sex = 'муж' if values['-MALE-'] else 'жен' if values['-FEMALE-'] else ''
            height = values['-HEIGHT-']
            weight = values['-WEIGHT-']
            date_of_birth = values['-DATE_OF_BIRTH-']
            passport = values['-PASSPORT-']
            passport = passport.replace(" ", "")
            passport = passport[:4] + " " + passport[4:]
            date_of_receipt = datetime.date.today().isoformat()
            database.add_patient(surname, name, patronymic, sex, height, weight, date_of_birth, passport, date_of_receipt)
            sg.popup('Пациент успешно добавлен!')
            break
    window.close()


sg.theme('GrayGrayGray')
sg.set_global_icon('resources/icon.ico')
sg.popup_no_buttons(no_titlebar=True, auto_close=True, auto_close_duration=3, image='resources/screen.png')
layout = [
    [sg.Menu([['Пациент', ['Список пациентов', 'Добавить пациента']], ['Справка', ['Помощь', 'О программе', 'Выход']]])],
    [sg.Text('Здравствуйте!', font=('Helvetica', 16), justification='center')],
    [sg.Text('Пожалуйста, выберите одно из действий в меню.', font=('Helvetica', 12), justification='center')],
    [sg.Button('Добавить пациента', size=(20, 2)), sg.Button('Список пациентов', size=(20, 2))],
    [sg.Button('О программе', size=(15, 2)), sg.Button('Помощь', size=(15, 2)), sg.Button('Выход', size=(15, 2))],
    [sg.Image('resources/screen.png')]
]

window = sg.Window('Помощник', layout, size=(800, 400), element_justification='c')
while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, 'Exit', 'Выход'):
        break
    elif event == 'Список пациентов':
        show_patient_data_window()
    elif event == 'Добавить пациента':
        show_add_patient_window()
    elif event == 'Помощь':
        sg.popup_scrolled(help_text, size=(150, 30), text_color='black', font='Helvetica 12', title='Помощь')
    elif event == 'О программе':
        sg.popup('Голосовой помощник врача\nВерсия 1.0 (2024)\nАвтор : Басаргин Михаил, гр.ИП-011', title='О программе')

window.close()
