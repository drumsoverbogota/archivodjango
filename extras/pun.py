from importlib.metadata import metadata
from pathlib import Path
import re
import zipfile
from pun_utils import ConciertoUpload
from pun_utils import LanzamientoUpload

import audio_metadata
import datetime
import os
import sys
import shutil


from datetime import date
from time import ctime

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDateEdit
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QListView
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QGroupBox

from PyQt5.QtCore import QAbstractListModel
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QDate
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QSignalMapper

from PyQt5.QtGui import QImage

import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

tick = QImage(dname + '/files/tick.png')
wtick = QImage(dname + '/files/tick-white.png')
rtick = QImage(dname + '/files/cross.png')


conciertos_dict = {
    "nombre": "line",
    "artista": "line",    
    "fecha": "date",
    "notas_archivo": "text",
    "notas_internet_archive": "text",
    "topics": "line",
}

lanzamientos_dict = {
    "nombre": "line",
    "banda": "line",
    "referencia": "line", 
    "formato": "combo",
    "anho": "line",
    "tracklist": "text",
    "creditos": "text",
    "indice_referencia": "line",
    "nota_digitalizacion": "text",
    "notas_internet_archive": "text",
    "topics": "line",
}

combobox_contents = {
    "formatos": ['CD', 'Digipack','12"','10"','7"','Flexi','Cassette','Digital','Mini CD','DVD','Otros','Bootleg']
}

settings_dict = {
    "url_api_conciertos": ("URL API Conciertos", ""),
    "url_api_lanzamientos": ("URL API Lanzamientos", ""),
    "user_el_muladar": ("User El Muladar", ""),
    "password_el_muladar": ("Password El Muladar", ""),
    "s3_access_key": ("S3 Access Key Internet Archive", ""),
    "s3_secret_key": ("S3 Secret Key Internet Archive", ""),
    "timeout_time": ("Timeout time", 3),
    "default_location": ("Default Location", "H:\RIPS\Archivo Punk"),
    "time_offset": ("Time Offset", 0.25),
    "check_test_item": ("Test items", 0)
}

class QueueModel(QAbstractListModel):
    def __init__(self, *args, queue=None, **kwargs):
        super(QueueModel, self).__init__(*args, **kwargs)
        self.queue = queue or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the data structure.
            _, event = self.queue[index.row()]
            # Return the todo text only.
            if isinstance(event, dict):
                return event.get('nombre')
        
        if role == Qt.DecorationRole:
            status, _ = self.queue[index.row()]
            if status == 'w':
                return wtick
            if status == 's':
                return tick
            if status == 'f':
                return rtick

    def get_idx_with_nombre(self, nombre):
        for idx, x in enumerate(self.queue):
            _, event = self.queue[idx]
            if event.get("nombre") == nombre:
                return idx

    def rowCount(self, index):
        return len(self.queue)


class Application(QWidget):

    tabs = {}

    signal_mapper_image = QSignalMapper()
    signal_mapper_file = QSignalMapper()

    signal_mapper_add = QSignalMapper()
    signal_mapper_update = QSignalMapper()
    signal_mapper_clear_selection = QSignalMapper()
    signal_mapper_clear_form = QSignalMapper()
    signal_mapper_delete = QSignalMapper()
    signal_mapper_upload = QSignalMapper()
    signal_mapper_row_selected = QSignalMapper()
    
    output_textedit = None

    upload_image = None
    open_image_label = None

    upload_list = None

    upload_concert_queue = QueueModel()
    upload_lanzamiento_queue = QueueModel()

    #Default settings
    settings = QSettings("Pun", "El Muladar")

    for key in settings_dict:
        if not settings.contains(key):
            setting = settings_dict[key]
            settings.setValue(key, setting[1])
            
    settings.sync()
    """
    upload_concert_queue.queue.append(
        [
            'w',
            {
                'nombre': 'Ataquesero - Gonorrea Fest IV  ',
                'artista': 'Ataquesero',
                'fecha': QDate(2022, 9, 7), 
                'notas_archivo': 'Ataquesero en el gonorrea fest', 
                'notas_internet_archive': 'Ataquesero live', 
                'link': '123', 
                'topics': '123', 
                'imagen': '/media/sergio/CEDA26A8DA268CB1/Users/Sergio/Documents/Proyectos/Grabaciones/2022-01-29 Asfixia 6 Dia 2/flyer.jpeg', 
                'file': '/home/sergio/Documents/proyectos/ELMA0001NumenNaif.zip'
            }
        ]
    )

    upload_lanzamiento_queue.queue.append(
        [
            'w',
            {
                'nombre': 'Uñas Púnk Siempre lokás', 
                'banda': "Asco, ZD, Ira, lOS sUZIOX", 
                'referencia': '2', 
                'formato': 3, 
                'anho': '4', 
                'tracklist': '5\n6', 
                'creditos': '7+8\t\n8', 
                'indice_referencia': '9', 
                'nota_digitalizacion': '10', 
                'imagen': 'zipfile:Treno.1.jpg', 
                'file': '/home/sergio/Documents/ELMA0001NumenNaif.zip',
                'notas_internet_archive': 'Punk band Numen Naif\nFrom Bogota Colomiba',
                'topics': "Punk, colombia",
            }
        ]
    )
    """
    upload_concert_form = {}
    upload_lanzamiento_form = {}
    settings_form = {}
    

    def __init__(self, parent=None):

        super(Application, self).__init__(parent)

        self.setWindowTitle("Pun")
        self.tab_widget = QTabWidget()
        self.resize(1280, 900)

        tab1 = QWidget()
        tab2 = QWidget()
        tab3 = QWidget()
        tab4 = QWidget()

        self.tabs["&List Songs"] = tab1
        self.tabs["Upload &Concert"] = tab2
        self.tabs["Upload &Lanzamiento"] = tab3
        self.tabs["&Settings"] = tab4

        tab1.setLayout(self.create_list_tab())
        tab2.setLayout(self.upload_concierto_tab())
        tab3.setLayout(self.upload_lanzamiento_tab())
        tab4.setLayout(self.settings_tab())

        for tab in self.tabs:
            self.tab_widget.addTab(self.tabs[tab], tab)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

        #Variables

        self.path = self.settings.value("default_location")
        self.time_offset = 0.25
        self.song_metadata = []
        self.supported_extensions_audio = [".mp3", ".flac"]
        self.supported_extensions_images = (".jpg", ".jpeg", ".png")

        #Signal Mappers
        self.signal_mapper_image.mapped[int].connect(self.image_button)
        self.signal_mapper_file.mapped[int].connect(self.file_button)

        self.signal_mapper_add.mapped[int].connect(self.add_to_queue)
        self.signal_mapper_update.mapped[int].connect(self.update_queue)
        self.signal_mapper_clear_selection.mapped[int].connect(self.clear_selection)
        self.signal_mapper_clear_form.mapped[int].connect(self.clear_form)
        self.signal_mapper_delete.mapped[int].connect(self.delete_from_queue)
        self.signal_mapper_upload.mapped[int].connect(self.upload)
        self.signal_mapper_row_selected.mapped[int].connect(self.on_row_selected)
        
    def create_list_tab(self):

        layout = QGridLayout()

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)

        self.output_textedit = text_edit

        self.update_textedit("Open a folder to list the songs.")
        button = QPushButton('&Open Folder')
        button.clicked.connect(self.on_button_clicked)
        layout.addWidget(text_edit, 0, 0)
        layout.addWidget(button, 1, 0)

        checkbox_layout = QHBoxLayout()
        layout.addLayout(checkbox_layout, 2, 0)

        self.artist_checkbox = QCheckBox("&Artist")
        self.artist_checkbox.toggled.connect(self.update_list)
        checkbox_layout.addWidget(self.artist_checkbox)

        self.time_checkbox = QCheckBox("&Time")
        self.time_checkbox.toggled.connect(self.update_list)
        checkbox_layout.addWidget(self.time_checkbox)

        self.header_checkbox = QCheckBox("&Header")
        self.header_checkbox.toggled.connect(self.update_list)
        checkbox_layout.addWidget(self.header_checkbox)

        return layout

    def upload_concierto_tab(self):
    
        layout = QGridLayout()

        position = 0
        for label in conciertos_dict:
            layout.addWidget(QLabel(f"{label}:".replace("_", " ").capitalize()), position, 0)
            if conciertos_dict[label] == "line":
                self.upload_concert_form[label] = QLineEdit()
                layout.addWidget(self.upload_concert_form[label], position, 1)
            if conciertos_dict[label] == "text":
                self.upload_concert_form[label] = QTextEdit()
                #self.upload_concert_form[label].
                layout.addWidget(self.upload_concert_form[label], position, 1)
                layout.setRowStretch(position, 1)
            if conciertos_dict[label] == "date":
                today_date = date.today()
                self.upload_concert_form[label] = QDateEdit(calendarPopup=True)
                self.upload_concert_form[label].setDate(QDate(today_date.year, today_date.month , today_date.day))
                layout.addWidget(self.upload_concert_form[label], position, 1)             
            
            position += 1

        #Image field
        open_image_button = QPushButton('&Select image')
        open_image_button.clicked.connect(self.signal_mapper_image.map)
        self.signal_mapper_image.setMapping(open_image_button, 0)
        
        self.open_image_label = QLabel()
        self.open_image_label.setFixedWidth(400)
        self.open_image_label.setAlignment(Qt.AlignRight)
        self.upload_concert_form["imagen"] = self.open_image_label

        layout.addWidget(QLabel("Image:"), position, 0)
        layout.addWidget(open_image_button, position, 0)

        layout.addWidget(self.open_image_label, position, 1, 1, 3)

        self.upload_image_zip = QCheckBox("&Upload image if ZIP File")
        layout.addWidget(self.upload_image_zip, position , 2)

        position +=1

        #Upload file field
        open_file_button = QPushButton('Select &file')
        open_file_button.clicked.connect(self.signal_mapper_file.map)
        self.signal_mapper_file.setMapping(open_file_button, 0)

        
        self.open_file_label = QLabel()
        self.open_file_label.setFixedWidth(400)
        self.open_file_label.setAlignment(Qt.AlignRight)
        self.upload_concert_form["file"] = self.open_file_label

        layout.addWidget(QLabel("File:"), position, 0)
        layout.addWidget(open_file_button, position, 0)
        layout.addWidget(self.open_file_label, position, 1, 1, 1)

        position +=1

        self.upload_list = QListView()
        self.upload_list.setModel(self.upload_concert_queue)
        self.upload_list.clicked.connect(self.signal_mapper_row_selected.map)
        self.upload_list.activated.connect(self.signal_mapper_row_selected.map)
        self.signal_mapper_row_selected.setMapping(self.upload_list, 0)


        layout.addWidget(self.upload_list, 0, 2, position - 3, 1)
        

        self.retry_checkbox = QCheckBox("&Retry upload if failure")
        layout.addWidget(self.retry_checkbox, position - 3, 2)

        #Buttons

        horizontal_group_box = QGroupBox("Queued items options")
        layout_botones = QHBoxLayout()

        add_queue_button = QPushButton('&Add to Queue')
        add_queue_button.clicked.connect(self.signal_mapper_add.map)        
        self.signal_mapper_add.setMapping(add_queue_button, 0)        
        layout_botones.addWidget(add_queue_button)

        add_queue_button = QPushButton('&Update item in queue')
        add_queue_button.clicked.connect(self.signal_mapper_update.map)        
        self.signal_mapper_update.setMapping(add_queue_button, 0)
        layout_botones.addWidget(add_queue_button)        

        add_queue_button = QPushButton('&Clear selection')
        add_queue_button.clicked.connect(self.signal_mapper_clear_selection.map)        
        self.signal_mapper_clear_selection.setMapping(add_queue_button, 0)        
        layout_botones.addWidget(add_queue_button)

        add_queue_button = QPushButton('Clear &form')
        add_queue_button.clicked.connect(self.signal_mapper_clear_form.map)        
        self.signal_mapper_clear_form.setMapping(add_queue_button, 0)
        layout_botones.addWidget(add_queue_button)        

        add_queue_button = QPushButton('&Delete')
        add_queue_button.clicked.connect(self.signal_mapper_delete.map)
        self.signal_mapper_delete.setMapping(add_queue_button, 0)
        layout_botones.addWidget(add_queue_button)

        upload_button = QPushButton('U&pload')
        upload_button.clicked.connect(self.signal_mapper_upload.map)
        self.signal_mapper_upload.setMapping(upload_button, 0)
        layout_botones.addWidget(upload_button)

        horizontal_group_box.setLayout(layout_botones)
        layout.addWidget(horizontal_group_box, position, 0, 1, 3)
        position +=1

        #Status terminal

        self.status_box = QTextEdit()
        self.status_box.setReadOnly(True)
        layout.addWidget(self.status_box, position, 0, 2, 3)
        position +=1

        return layout

    def upload_lanzamiento_tab(self):
        layout = QGridLayout()

        position = 0
        for label in lanzamientos_dict:
            layout.addWidget(QLabel(f"{label}:".replace("_", " ").capitalize()), position, 0)
            if lanzamientos_dict[label] == "line":
                self.upload_lanzamiento_form[label] = QLineEdit()
                layout.addWidget(self.upload_lanzamiento_form[label], position, 1)
            if lanzamientos_dict[label] == "text":
                self.upload_lanzamiento_form[label] = QTextEdit()
                layout.addWidget(self.upload_lanzamiento_form[label], position, 1)
                layout.setRowStretch(position, 1)
            if lanzamientos_dict[label] == "date":
                today_date = date.today()
                self.upload_lanzamiento_form[label] = QDateEdit(calendarPopup=True)
                self.upload_lanzamiento_form[label].setDate(QDate(today_date.year, today_date.month , today_date.day))
                layout.addWidget(self.upload_lanzamiento_form[label], position, 1)
            if lanzamientos_dict[label] == "combo":
                today_date = date.today()
                self.upload_lanzamiento_form[label] = QComboBox()
                self.upload_lanzamiento_form[label].addItems(combobox_contents.get("formatos"))
                layout.addWidget(self.upload_lanzamiento_form[label], position, 1)                
            position += 1


        #List for the queue

        self.upload_list_lanzamiento = QListView()
        self.upload_list_lanzamiento.setModel(self.upload_lanzamiento_queue)
        self.upload_list_lanzamiento.clicked.connect(self.signal_mapper_row_selected.map)
        self.upload_list_lanzamiento.activated.connect(self.signal_mapper_row_selected.map)
        self.signal_mapper_row_selected.setMapping(self.upload_list_lanzamiento, 1)

        layout.addWidget(self.upload_list_lanzamiento, 0, 2, position, 1)
        

        self.retry_checkbox_lanzamiento = QCheckBox("&Retry upload if failure")
        layout.addWidget(self.retry_checkbox_lanzamiento, position, 2)

        #Image field
        open_image_button = QPushButton('&Select image')
        open_image_button.clicked.connect(self.signal_mapper_image.map)
        self.signal_mapper_image.setMapping(open_image_button, 1)
        
        self.open_image_label_lanzamiento = QLabel()
        self.open_image_label_lanzamiento.setFixedWidth(400)
        self.open_image_label_lanzamiento.setAlignment(Qt.AlignRight)
        self.upload_lanzamiento_form["imagen"] = self.open_image_label_lanzamiento

        layout.addWidget(QLabel("Image:"), position, 0)
        layout.addWidget(open_image_button, position, 0)
        layout.addWidget(self.open_image_label_lanzamiento, position, 1, 1, 3)

        position +=1

        #Upload file field
        open_file_button = QPushButton('Select &file')
        open_file_button.clicked.connect(self.signal_mapper_file.map)
        self.signal_mapper_file.setMapping(open_file_button, 1)
        
        self.open_file_label_lanzamiento = QLabel()
        self.open_file_label_lanzamiento.setFixedWidth(400)
        self.open_file_label_lanzamiento.setAlignment(Qt.AlignRight)
        self.upload_lanzamiento_form["file"] = self.open_file_label_lanzamiento

        layout.addWidget(QLabel("File:"), position, 0)
        layout.addWidget(open_file_button, position, 0)
        layout.addWidget(self.open_file_label_lanzamiento, position, 1, 1, 1)

        position +=1

        horizontal_group_box = QGroupBox("Queued items options")
        layout_botones = QHBoxLayout()

        add_queue_button = QPushButton('&Add to Queue')
        add_queue_button.clicked.connect(self.signal_mapper_add.map)        
        self.signal_mapper_add.setMapping(add_queue_button, 1)        
        layout_botones.addWidget(add_queue_button)

        add_queue_button = QPushButton('&Update item in queue')
        add_queue_button.clicked.connect(self.signal_mapper_update.map)        
        self.signal_mapper_update.setMapping(add_queue_button, 1)
        layout_botones.addWidget(add_queue_button)        

        add_queue_button = QPushButton('&Clear selection')
        add_queue_button.clicked.connect(self.signal_mapper_clear_selection.map)        
        self.signal_mapper_clear_selection.setMapping(add_queue_button, 1)        
        layout_botones.addWidget(add_queue_button)

        add_queue_button = QPushButton('Clear &form')
        add_queue_button.clicked.connect(self.signal_mapper_clear_form.map)        
        self.signal_mapper_clear_form.setMapping(add_queue_button, 1)
        layout_botones.addWidget(add_queue_button)        

        add_queue_button = QPushButton('&Delete')
        add_queue_button.clicked.connect(self.signal_mapper_delete.map)
        self.signal_mapper_delete.setMapping(add_queue_button, 1)
        layout_botones.addWidget(add_queue_button)

        upload_button = QPushButton('U&pload')
        upload_button.clicked.connect(self.signal_mapper_upload.map)
        self.signal_mapper_upload.setMapping(upload_button, 1)
        layout_botones.addWidget(upload_button)

        horizontal_group_box.setLayout(layout_botones)
        layout.addWidget(horizontal_group_box, position, 0, 1, 3)
        position +=1

        #Status terminal

        self.status_box_lanzamiento = QTextEdit()
        self.status_box_lanzamiento.setReadOnly(True)
        layout.addWidget(self.status_box_lanzamiento, position, 0, 2, 3)
        position +=1


        return layout

    def settings_tab(self):
        layout = QFormLayout()


        for key in settings_dict:
            label = settings_dict.get(key)[0]
            setting = str(self.settings.value(key))
            if key.startswith("check"):
                self.settings_form[key]  = QCheckBox()
                self.settings_form[key].setChecked(True if setting == "1" else False)
            else:
                self.settings_form[key]  = QLineEdit()
                self.settings_form[key].setText(setting)

            if key.startswith("password"):            
                self.settings_form[key].setEchoMode(QLineEdit.Password)

            layout.addRow(label, self.settings_form[key])


        update_settings_button = QPushButton('U&pdate Settings')
        update_settings_button.clicked.connect(self.update_settings)
        layout.addRow(update_settings_button)

        return layout

    def image_button(self, index):
        path = ""
        options = QFileDialog.Options()

        dialog = QFileDialog()
        dialog.setOptions(options)
        dialog.setDirectory(self.path)

        if dialog.exec_() == QDialog.Accepted:
            self.path = os.path.dirname(path)
            self.path = path
            if index == 0:
                self.open_image_label.setText(path)
            if index == 1:
                self.open_image_label_lanzamiento.setText(path)

    def read_file_metadata(self, file_to_read):
        metadata = {}
        
        concierto = os.path.basename(os.path.dirname(file_to_read))
        directorio = os.path.dirname(file_to_read)
        banda = Path(file_to_read).stem

        for files_directorio in os.listdir(directorio):
            if files_directorio.endswith(self.supported_extensions_images):
                metadata["imagen"] = os.path.join(directorio, files_directorio)
                break


        nombre_banda = ""

        regex_banda = r"^[0-9]*\s-?\s?([\w\d, ]*)$"
        regex_concierto = r"^(\d*)-(\d*)-(\d*)\s([\w\d, ]*)$"
        matches_banda = re.finditer(regex_banda, banda, re.MULTILINE)
        matches_concierto = re.finditer(regex_concierto, concierto, re.MULTILINE)
        for match in matches_banda:
            nombre_banda = match.group(1)
            metadata["artista"] = nombre_banda
        for match in matches_concierto:
            anho = int(match.group(1))
            mes = int(match.group(2))
            dia = int(match.group(3))
            nombre_concierto = match.group(4)
            metadata["fecha"] = QDate(anho, mes, dia)
            metadata["nombre"] = f"{nombre_banda} - {nombre_concierto}"
            metadata["notas_archivo"] = f'Grabación de la banda "{nombre_banda}" en el concierto "{nombre_concierto}"\nGrabado en Bogotá'
            metadata["notas_internet_archive"] = f'Live recording of Punk band "{nombre_banda}" on "{nombre_concierto}".\nRecorded in Bogotá, Colombia.'
        return metadata


    def read_zip_file(self, file_to_open):
        
        #Store the song metadata in case is still being used in the first tab
        temp_song_metadata = self.song_metadata

        artist_set = set()
        album_set = set()
        date_set = set()

        metadata = {}

        is_zip = zipfile.is_zipfile(file_to_open)
        if is_zip:
            with zipfile.ZipFile(file_to_open, 'r') as zip:
                
                filename = os.path.basename(file_to_open)
                #If file name begins with ELMA we know that the files are following
                #the reference of ELMAXXXX where XXXX is a number from 0000 to 9999
                if filename.startswith("ELMA"):
                    metadata["indice_referencia"] = filename[:8]

                self.append_terminal('Extracting all the files now...')
                zip.extractall(path=f'{dname}/tmp')
                files_ia = [f"{dname}/tmp/{file}" for file in zip.namelist() if not file.endswith("/")]
                if files_ia:
                    
                    #Get the first image
                    images = []
                    for files_in_zip in files_ia:
                        if files_in_zip.endswith(self.supported_extensions_images):
                            images.append(files_in_zip)
                    
                    if images:
                        images.sort()
                        metadata["imagen"] = f"zipfile:{os.path.basename(images[0])}"

                    path = os.path.dirname(files_ia[0])
                    self.load_songs(path)

                    for song in self.song_metadata:

                        artist = song.get("tags", {}).get("artist", [None])[0]
                        album = song.get("tags", {}).get("album", [None])[0]
                        year = song.get("tags", {}).get("date", [None])[0]

                        if artist:
                            artist_set.add(artist)
                        if album:
                            album_set.add(album)
                        if year:
                            date_set.add(year) 
                    
                    #If there are more than one artist we add the name to the tracklist
                    metadata["tracklist"] = self.create_list(artist_name=len(artist_set)>1)
                    metadata["banda"] = ', '.join(artist_set)
                    
                    if len(album_set) == 1:
                        album, = album_set
                        metadata["nombre"] = album

                    if len(date_set) == 1:
                        anho, = date_set
                        metadata["anho"] = anho


                self.append_terminal('Deleting temporary extracted files...')
                shutil.rmtree(path=f'{dname}/tmp')
                self.append_terminal('Files deleted!')

        self.song_metadata = temp_song_metadata
        return metadata

    def file_button(self,index):
        path = ""
        options = QFileDialog.Options()

        dialog = QFileDialog()
        dialog.setOptions(options)
        dialog.setDirectory(self.path)

        if dialog.exec_() == QDialog.Accepted:
            path = dialog.selectedFiles()[0]
            self.path = os.path.dirname(path)
            if index == 0:
                self.open_file_label.setText(path)
                metadata = self.read_file_metadata(path)
                for field in metadata:
                    if field == 'imagen':
                        self.open_image_label.setText(metadata.get(field))
                    if field == 'fecha':
                        self.upload_concert_form[field].setDate(metadata.get(field))                        
                    else:
                        self.upload_concert_form[field].setText(metadata.get(field))                
            if index == 1:
                self.open_file_label_lanzamiento.setText(path) 
                metadata = self.read_zip_file(path)
                for field in metadata:
                    if field == 'imagen':
                        self.open_image_label_lanzamiento.setText(metadata.get(field))
                    else:
                        self.upload_lanzamiento_form[field].setText(metadata.get(field))


    def add_to_queue(self, index):
        
        if index == 0:
            form = self.upload_concert_form
            event_queue = self.upload_concert_queue
            upload_list = self.upload_list
        elif index == 1:
            form = self.upload_lanzamiento_form
            event_queue = self.upload_lanzamiento_queue
            upload_list = self.upload_list_lanzamiento

        event = {}
        
        for key in form:
            field = form[key]
            if isinstance(field, QLineEdit) or isinstance(field, QLabel):
                event[key] = field.text()
            elif isinstance(field, QDateEdit):
                event[key] = field.date()
            elif isinstance(field, QTextEdit):
                event[key] = field.toPlainText()
            elif isinstance(field, QComboBox):
                event[key] = field.currentIndex()

        event_queue.queue.append(['w', event])
        event_queue.layoutChanged.emit()

        upload_list.clearSelection()
        self.clear_form(index)

    def update_queue(self, index):

        if index == 0:
            form = self.upload_concert_form
            event_queue = self.upload_concert_queue
            upload_list = self.upload_list
        elif index == 1:
            form = self.upload_lanzamiento_form
            event_queue = self.upload_lanzamiento_queue
            upload_list = self.upload_list_lanzamiento

        event = {}
        
        for key in form:
            field = form[key]
            if isinstance(field, QLineEdit) or isinstance(field, QLabel):
                event[key] = field.text()
            elif isinstance(field, QDateEdit):
                event[key] = field.date()
            elif isinstance(field, QTextEdit):
                event[key] = field.toPlainText()
            elif isinstance(field, QComboBox):
                event[key] = field.currentIndex()                

        indexes = upload_list.selectedIndexes()

        if indexes:
            index_to_update = indexes[0]
            event_queue.queue[index_to_update.row()] = ['w', event]

        upload_list.clearSelection()

        self.clear_form(index)

    def clear_selection(self, index):
        if index == 0:
            self.upload_list.clearSelection()
        if index == 1:
            self.upload_list_lanzamiento.clearSelection()            

    def clear_form(self, index):
        if index == 0:
            form = self.upload_concert_form
            today_date = date.today()
            form['fecha'].setDate(QDate(today_date.year, today_date.month , today_date.day))            
        if index == 1:
            form = self.upload_lanzamiento_form

        for key in form:
            field = form[key]
            if isinstance(field, QLineEdit) or isinstance(field, QDateEdit) or isinstance(field, QLabel):
                field.clear()
            elif isinstance(field, QTextEdit):
                field.clear()

    def delete_from_queue(self, index):
        
        if index == 0:
            list_queue = self.upload_list
            event_queue = self.upload_concert_queue
        if index == 1:
            list_queue = self.upload_list_lanzamiento
            event_queue = self.upload_lanzamiento_queue

        indexes = list_queue.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            # Remove the item and refresh.
            del event_queue.queue[index.row()]
            event_queue.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            list_queue.clearSelection()

    def upload(self, index):

        if index == 0:
            event_queue = self.upload_concert_queue
            retry = self.retry_checkbox.isChecked()
            workerthread = ConciertoUpload
        if index == 1:
            event_queue = self.upload_lanzamiento_queue
            retry = self.retry_checkbox_lanzamiento.isChecked()
            workerthread = LanzamientoUpload

        for _, x in enumerate(event_queue.queue):
            status = x[0]
            event = x[1]

            upload_status = ['w']

            band_name = event.get("nombre")

            if retry:
                upload_status.append('f')

            if status in upload_status:
                if status == 'w':
                    self.append_terminal(f'Starting creation of {band_name}')
                if status == 'f':
                    self.append_terminal(f'Retrying creation of {band_name}')

                worker = workerthread(self, event)
                worker.progress.connect(self.append_terminal)
                worker.update_signal.connect(self.failure)
                worker.start()

            else:
                self.append_terminal(f"Skipping creating {band_name}")
                self.append_terminal("=====================")
                continue         

    def on_row_selected(self, index):

        if index == 0:
            list_queue = self.upload_list
            event_queue = self.upload_concert_queue
            form = self.upload_concert_form
        if index == 1:
            list_queue = self.upload_list_lanzamiento
            event_queue = self.upload_lanzamiento_queue
            form = self.upload_lanzamiento_form

        event = event_queue.queue[list_queue.currentIndex().row()][1]

        for key in form:
            field = form[key]
            if isinstance(field, QLineEdit) or isinstance(field, QLabel):
                field.setText(event[key])
            if isinstance(field, QDateEdit):
                field.setDate(event[key])
            elif isinstance(field, QTextEdit):
                field.setText(event[key])
            elif isinstance(field, QComboBox):
                field.setCurrentIndex(int(event[key]))

    def append_terminal(self, text):
        self.status_box.append(f"[{ctime()}] {text}")
        self.status_box_lanzamiento.append(f"[{ctime()}] {text}")

    def failure(self, result, nombre, evento):
        
        if evento == "concierto":
            upload_queue = self.upload_concert_queue
        elif evento == "lanzamiento":
            upload_queue = self.upload_lanzamiento_queue

        idx = upload_queue.get_idx_with_nombre(nombre)

        if not result:
            upload_queue.queue[idx][0] = 'f'
            upload_queue.layoutChanged.emit()
            self.append_terminal(f"Failure creating {nombre}")
        else:
            upload_queue.queue[idx][0] = 's'
            upload_queue.layoutChanged.emit()
            self.append_terminal(f"Success creating {nombre}")        

    def update_settings(self):
        for key in settings_dict:
            if key.startswith("check"):
                value_to_set = "1" if self.settings_form[key].isChecked() else "0"
                self.settings.setValue(key, value_to_set)
            else:
                self.settings.setValue(key, self.settings_form[key].text())
        self.settings.sync()

        self.path = self.settings.value("default_location")

    def update_textedit(self, text):
        self.output_textedit.setPlainText(text)

    def create_list(self, header=False, artist_name=False, show_time=False):
        
        if header:
            song_list = "Visiten El Muladar, un archivo de punk colombiano http://elmuladar.com\n\n"
        else:
            song_list = ""

        duration = datetime.datetime(10, 1, 1, 0, 0, 0)
        for song in self.song_metadata:
            
            tracknumber = song.tags.tracknumber[0]
            artist = song.tags.artist[0]
            title = song.tags.title[0]
            seconds = song.streaminfo.duration

            total_minutes = duration.minute + (duration.hour * 60)
            total_seconds = duration.second

            if total_seconds <= 9:
                total_seconds = "0" + str(total_seconds)

            track = ""

            # Add track number
            track += f"{tracknumber}. "

            # Add Artist
            if artist_name:
                track += f"{artist} - "

            # Add title
            track += f"{title} "

            # Add time
            if show_time:
                track += f"{total_minutes}:{total_seconds}"

            track = track.strip() + "\n"

            song_list += track

            duration += datetime.timedelta(seconds=int(seconds + self.time_offset))

        if not song_list:
            song_list = "No files were found."

        return song_list

    def load_songs(self, path):
        song_metadata = []
        try:
            for filename in os.listdir(path):
                _, extension = os.path.splitext(filename)
                if extension in self.supported_extensions_audio:
                    try:
                        metadata = audio_metadata.load(f"{path}/{filename}")
                        
                        song_metadata.append(metadata)
                    except audio_metadata.exceptions.UnsupportedFormat:
                        print(f"Filerror opening {filename}")
                    except PermissionError:
                        print("Denied access")
        except PermissionError:
            print("Denied access")
        except Exception as e:
            print("Unknown exception while opening the folder. ", str(e))

        song_metadata.sort(key=lambda x: x.get("tags", {}).get("tracknumber", [])[0])
        self.song_metadata = song_metadata

    def update_list(self):

        header = self.header_checkbox.isChecked()
        artist = self.artist_checkbox.isChecked()
        show_time = self.time_checkbox.isChecked()
        self.update_textedit(self.create_list(
                header=header,
                artist_name=artist,
                show_time=show_time
            )
        )

    def on_button_clicked(self):

        options = QFileDialog.Options()

        dialog = QFileDialog()
        dialog.setOptions(options)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setDirectory(self.path)

        if dialog.exec_() == QDialog.Accepted:
            self.path = dialog.selectedFiles()[0]
            self.load_songs(self.path)
            self.update_list()

if __name__ == '__main__':
    app = QApplication([])
    app.setStyle("WindowsVista")
    main_app = Application()
    main_app.show()
    sys.exit(app.exec_())
