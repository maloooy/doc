import pyaudio
import threading
import json
import datetime
import pyttsx3
from extractor import NumberExtractor
from vosk import Model, KaldiRecognizer


button_state = False
recognized_data = []
model = Model('vosk_small')
rec = KaldiRecognizer(model, 16000)


def extractor():
    return NumberExtractor()


def format_string(input_string):
    digits = [char for char in input_string if char.isdigit()]
    return ''.join(digits)


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def replace_symbols(text):
    text = text.replace('тире', '-')
    text = text.replace('запятая', ',')
    text = text.replace('точка', '.')
    return text


def check_record(target_key):
    text = ''
    if target_key == '-NAME-':
        text = 'Имя'
    elif target_key == '-SURNAME-':
        text = 'Фамилия'
    elif target_key == '-PATRONYMIC-':
        text = 'Отчество'
    elif target_key == '-DATE_OF_BIRTH-':
        text = 'Дата рождения'
    elif target_key == '-SEX-M-':
        text = 'Пол'
    elif target_key == '-PASSPORT-':
        text = 'Паспорт'
    elif target_key == '-HEIGHT-':
        text = 'Рост'
    elif target_key == '-WEIGHT-':
        text = 'Вес'
    elif target_key == '-COMPLAINTS-':
        text = 'Жалобы'
    elif target_key == '-INSPECTION-':
        text = 'Осмотр'
    elif target_key == '-DIAGNOSIS-':
        text = 'Диагноз'
    elif target_key == '-THERAPY-':
        text = 'Лечение'
    elif target_key == '-DATE_OF_RECEIPT-':
        text = 'Дата приёма'
    return text


def start_record(window, target_key):
    global button_state
    if button_state:
        button_state = False
        window['check_load_1'].update(value="ИДЁТ ЗАПИСЬ В ПОЛЕ", text_color='gray94')
        window['check_load_2'].update(value=check_record(target_key), text_color='gray94')
    else:
        button_state = True
        threading.Thread(target=recording_and_recognizing, args=(window, target_key)).start()
        window['check_load_1'].update(value="ИДЁТ ЗАПИСЬ В ПОЛЕ", text_color='red')
        window['check_load_2'].update(value=check_record(target_key), text_color='red')


def recording_and_recognizing(window, target_key):
    global recognized_data
    number_extractor = extractor()
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    def listen():
        while button_state:
            data = stream.read(4000, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                answer = json.loads(rec.Result())
                if answer['text']:
                    yield answer['text']

    for text in listen():
        recognized_data = replace_symbols(text)
        check = window[target_key].get()
        if target_key == '-PASSPORT-':
            if len(window['-PASSPORT-'].get()) == 4:
                window[target_key].update(' ', append=True)
            recognized_data = number_extractor.replace_groups(recognized_data)
            recognized_data = format_string(recognized_data)
            window[target_key].update(value=recognized_data + '', append=True)
        elif target_key == '-SEX-M-':
            if recognized_data == 'мужской':
                window['-SEX-M-'].update(value=True)
                window['-SEX-F-'].update(value=False)
            elif recognized_data == 'женский':
                window['-SEX-M-'].update(value=False)
                window['-SEX-F-'].update(value=True)
        elif target_key in ['-SURNAME-', '-NAME-', '-PATRONYMIC-']:
            recognized_data = recognized_data.capitalize()
            window[target_key].update(value=recognized_data)
        elif target_key in ['-DATE_OF_BIRTH-', '-DATE_OF_RECEIPT-', '-HEIGHT-', '-WEIGHT-']:
            recognized_data = number_extractor.replace_groups(recognized_data)
            window[target_key].update(value=recognized_data.replace(' ', ''))
        elif check.strip() == '' and target_key in ['-COMPLAINTS-', '-INSPECTION-', '-DIAGNOSIS-', '-THERAPY-']:
            recognized_data = number_extractor.replace_groups(recognized_data)
            recognized_data = recognized_data.capitalize()
            window[target_key].update(value=recognized_data + ' ')
        else:
            recognized_data = number_extractor.replace_groups(recognized_data)
            window[target_key].update(value=recognized_data + ' ', append=True)

    stream.stop_stream()
    stream.close()
    audio.terminate()


def start_record_multi(window):
    threading.Thread(target=whole_card_record, args=(window,), daemon=True).start()


def whole_card_record(window):
    number_extractor = extractor()
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    def listen():
        window['check_load_1'].update(value="ИДЁТ ЗАПИСЬ", text_color='red')
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            answer = json.loads(rec.Result())
            if answer['text']:
                return answer['text']

    text_fields = {
        'Фамилия': window['-SURNAME-'],
        'Имя': window['-NAME-'],
        'Отчество': window['-PATRONYMIC-'],
        'Дата рождения': window['-DATE_OF_BIRTH-'],
        'Пол': window['-SEX-M-'],
        'Паспорт': window['-PASSPORT-'],
        'Рост': window['-HEIGHT-'],
        'Вес': window['-WEIGHT-'],
        'Жалобы': window['-COMPLAINTS-'],
        'Осмотр': window['-INSPECTION-'],
        'Диагноз': window['-DIAGNOSIS-'],
        'Лечение': window['-THERAPY-'],
        'Дата приёма': window['-DATE_OF_RECEIPT-']
    }

    for field_name, field in text_fields.items():
        speak(f"Запись в поле {field_name}")
        field.update(value='')
        while True:
            text = listen()
            window['check_load_1'].update(value="ИДЁТ ЗАПИСЬ", text_color='gray94')
            if text:
                check = field.get()
                text = replace_symbols(text)
                text = number_extractor.replace_groups(text)
                print(f"Recognized: {text}")
                if field_name == 'Пол':
                    window['-SEX-M-'].update(value=False)
                    window['-SEX-F-'].update(value=False)
                    if text == 'мужской':
                        window['-SEX-M-'].update(value=True)
                        window['-SEX-F-'].update(value=False)
                        break
                    elif text == 'женский':
                        window['-SEX-M-'].update(value=False)
                        window['-SEX-F-'].update(value=True)
                        break
                    else:
                        window['-SEX-M-'].update(value=False)
                        window['-SEX-F-'].update(value=False)
                        break
                if field_name == 'Паспорт':

                    current_text = field.get().replace(' ', '')
                    if len(current_text) == 4:
                        field.update(' ', append=True)
                        current_text = field.get().replace(' ', '')
                    if len(current_text) < 10:
                        field.update(value=text, append=True)
                        current_text = field.get().replace(' ', '')
                        if len(current_text) != 10:
                            continue
                        else:
                            break
                if field_name in ['Фамилия', 'Имя', 'Отчество']:
                    text = text.capitalize()
                    field.update(value=text)
                    break
                if field_name in ['Дата рождения', 'Рост', 'Вес']:
                    text = number_extractor.replace_groups(text)
                    field.update(value=text.replace(' ', ''))
                    break
                if field_name == 'Дата приёма':
                    if text == 'сегодня':
                        text = datetime.date.today().isoformat()
                        field.update(value=text)
                        break
                    else:
                        text = number_extractor.replace_groups(text)
                        field.update(value=text.replace(' ', ''))
                        break
                if check.strip() == '' and field_name in ['Жалобы', 'Осмотр', 'Диагноз', 'Лечение']:
                    text = text.capitalize()
                    field.update(value=text + ' ')
                    break
    speak('запись закончена')
    stream.stop_stream()
    stream.close()
    audio.terminate()