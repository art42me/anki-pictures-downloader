import json
import os
import re
import requests
import sys
import urllib.parse

from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QDialog

from aqt import mw
from aqt.utils import tooltip, showInfo
from anki.hooks import addHook

from .dialog import Ui_Dialog


headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"
}


def addPictures(browser):
    # Список карточек, которые были выделены в браузере, в виде note id
    nids = browser.selectedNotes()
    if not nids:
        tooltip("No cards selected.")
        return
    
    # Создаем окно аддона (dialog.ui)
    d = QDialog(browser)
    frm = Ui_Dialog()
    frm.setupUi(d)

    # Получаем первую карточку, чтобы узнать поля и заполнить окно аддона
    note = mw.col.getNote(nids[0])
    # Названия полей
    fields = note.keys()
    # Source Field:
    frm.srcField.addItems(fields)
    # Destination Field:
    frm.dstField.addItems(fields)
    # Выбираем последнее поле по умолчанию
    frm.dstField.setCurrentIndex(len(fields)-1)

    # Показываем окно диалога аддона и ждем, пока будет нажата кнопка OK или Cancel
    if not d.exec_():
        # Если была нажата
        return

    # Получаем название полей, которые были выбраны в интерфейса аддона
    srcField = frm.srcField.currentText()
    dstField = frm.dstField.currentText()

    # Для простоты используем встроенный в Анки диалог прогресса
    mw.progress.start(parent=browser)
    mw.progress._win.setWindowTitle("Downloading Pictures...")

    # Итерируемся по карточкам (notes)
    for idx, nid in enumerate(nids, 1):
        # Если юзер прервал скачивание картинок, то выходим из цикла for
        if mw.progress._win.wantCancel:
            break

        # Получаем карточку по nid
        note = mw.col.getNote(nid)

        # Обновляем окно прогресса
        mw.progress.update("[{}/{}] {}".format(idx, len(nids), note[srcField]))

        # Получем поле со словом для запроса в Google
        # Предполагается, что поле содержит только текст, а не HTML
        q = note[srcField]
        r = requests.get("https://www.google.com/search?tbm=isch&safe=active&q={}".format(q), headers=headers, timeout=15)
        # Проверяем, что запрос прошел без ошибок (4xx или 5xx)
        r.raise_for_status()

        results = []
        # Формируем регулярное выражения для поиска картинок
        regex = re.escape(r'AF_initDataCallback({') + r'[^<]*?data:[^<]*?(\[[^<]+\])'
        for txt in re.findall(regex, r.text):
            # Превращаем найденный текст в JSON
            data = json.loads(txt)
            # Для простоты игнорируем любые ошибки Exception, в особенности IndexError
            try:
                for d in data[31][0][12][2]:
                    try:
                        # Нашли ссылку на картинку
                        results.append(d[1][3][0])
                    except Exception as e:
                        pass
            except Exception as e:
                pass
        
        fname = None
        # Проходим по ссылкам на картинки
        for url in results:
            try:
                # Скачиваем картику
                r = requests.get(url, headers=headers, timeout=15)
                r.raise_for_status()
                data = r.content
                # Если content-type был text/html, пробуем скачать следующую картинку
                if 'text/html' in r.headers.get('content-type', ''):
                    continue
                # Игнорируем картинки в виде svg
                if 'image/svg+xml' in r.headers.get('content-type', ''):
                    continue
                # Генерируем имя файла из url картинки
                url = re.sub(r"\?.*?$", "", url)
                fname = os.path.basename(urllib.parse.unquote(url))
                break
            except Exception:
                pass
        if not fname:
            continue
        # Говорим Анки записать картинку (data) в папку collection.media с именем fname
        # Если fname уже существует и отличается, то Анки к имени файла добавит хеш и запишет с новым именем
        fname = mw.col.media.writeData(fname, data)
        # Форматируем имя файла в виде <img> тега HTML. 
        #Размещаем картинку по центру, чтобы она не была растянута на весь экран (максимум 90%), минимальная ширина 50% от экрана
        filename = f'<p style="text-align: center;"><img src="{fname}" max-height="90%" max-width="90%" min-width="50%"></p>'
        # И добавляем в поле dstField
        note[dstField] += filename
        # Записываем изменения из памяти в базу данных
        note.flush()

    # Завершаем индикатор прогресса
    mw.progress.finish()
    # Показываем новое окно, что загрузка картинок завершена
    showInfo("Download completed!", parent=browser)
    # Обновляем интерфейс в Анки
    # Например, если была выделена только одна карточка, чтобы отобразилась в окне редактора уже с картинкой
    mw.reset()        


def setupMenu(browser):
    # Получаем меню Edit
    menu = browser.form.menuEdit
    # Добавляем новое действие
    a = menu.addAction('Add Pictures To Cards')
    # При клике, вызвать функцию addPictures и передать в качестве параметра browser
    a.triggered.connect(lambda _, b=browser: addPictures(b))

# Используем Legacy Hook, чтобы добавить новое действие в меню Edit браузера
addHook("browser.setupMenus", setupMenu)
