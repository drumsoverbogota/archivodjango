
import re
import zipfile
import internetarchive
import requests
import os
import shutil


from requests.auth import HTTPBasicAuth
from zipfile import ZipFile

from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

settings = QSettings("Pun", "El Muladar")

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

class ConciertoUpload(QThread):
    progress = pyqtSignal(str)
    update_signal = pyqtSignal(bool, str, str)
    result = False
    event = {}

    def __init__(self, parent, event):
        QThread.__init__(self, parent)
        self.event = event

    def run(self):

        self.result = conciertos_upload(self.event, self.progress.emit)
        self.finished.connect(self.onfinish)

    def onfinish(self):        
        self.update_signal.emit(self.result, self.event.get('nombre'), "concierto")
        self.progress.emit("=====================")

class LanzamientoUpload(QThread):
    progress = pyqtSignal(str)
    update_signal = pyqtSignal(bool, str, str)
    result = False
    event = {}

    def __init__(self, parent, event):
        QThread.__init__(self, parent)
        self.event = event

    def run(self):

        self.result = lanzamientos_upload(self.event, self.progress.emit)
        self.finished.connect(self.onfinish)

    def onfinish(self):        
        self.update_signal.emit(self.result, self.event.get('nombre'), "lanzamiento")
        self.progress.emit("=====================")


def page_title_ia_test(nombre):
    return "test-" + page_title_ia(nombre)

def page_title_ia(nombre):
    nombre = nombre.lower().strip().replace(" ", "-")
    return re.sub('\-+', '-', nombre)

def conciertos_upload(event, terminal):
    terminal(f'Uploading Concierto to El Muladar {event.get("nombre")}')

    date = event.get("fecha").toString("yyyy-MM-dd")

    identifier = page_title_ia_test(event.get("nombre"))

    metadata_ia = {
        "identifier": identifier,
        "title": event.get("nombre").strip(),
        "creator": event.get("artista").strip(),
        "mediatype": "audio",
        "collection": "test_collection",
        "description": event.get("notas_internet_archive"),
        "subject": event.get("topics").strip(),
        "date": date,
        "language": "spa"
    }

    payload_muladar = {
        "nombre": event.get("nombre").strip(),
        "fecha_grabacion": date,
        "notas": event.get("notas_archivo"),
        "link": f"https://archive.org/details/{identifier}"
    }

    result = False

    try:
        files_muladar = {
            'imagen': open(event.get("imagen"), "rb")
        }

        files_ia = []
        upload_file = event.get("file")

        is_zip = zipfile.is_zipfile(upload_file)

        if is_zip:
            with ZipFile(event.get("file"), 'r') as zip:
                terminal('Extracting all the files now...')
                zip.extractall(path=f'{dname}/tmp')
                files_ia = [f"{dname}/tmp/{file}" for file in zip.namelist() if not file.endswith("/")]

        else:
            files_ia = [upload_file, event.get("imagen")]

        terminal('Uploading the following files to the Internet Archive')
        terminal('*'*10)
        for file in files_ia:
            terminal(file)
        terminal('*'*10)

        result = upload_to_internet_archive(metadata=metadata_ia, files=files_ia,terminal=terminal)
        result = result and upload_to_muladar(
            payload=payload_muladar, 
            files=files_muladar, 
            terminal=terminal, 
            api=settings.value("url_api_conciertos")
            )

        if is_zip:
            terminal('Deleting temporary extracted files...')
            shutil.rmtree(path=f'{dname}/tmp')
            terminal('Files deleted!')

    except Exception as e:
        terminal(str(e))
        terminal("Error opening the file")
    
    return result

def lanzamientos_upload(event, terminal):
    terminal(f'Uploading lanzamiento to El Muladar {event.get("nombre")}')

    identifier = page_title_ia_test(event.get("nombre"))

    metadata_ia = {
        "identifier": identifier,
        "title": event.get("nombre").strip(),
        "creator": None,
        "mediatype": "audio",
        "collection": "test_collection",
        "description": event.get("notas_internet_archive"),
        "subject": event.get("topics").strip(),
        "date": event.get("anho"),
        "language": "spa"
    }

    payload_muladar = {
        "nombre": event.get("nombre").strip(),
        "referencia": event.get("referencia").strip(),
        "anho": event.get("anho").strip(),
        "notas": event.get("notas_archivo"),
        "link": f"https://archive.org/details/{identifier}",
        "formato": event.get("formato"),
        "tracklist": event.get("tracklist"),
        "creditos": event.get("creditos"),
        "indice_referencia": event.get("indice_referencia"),
        "nota_digitalizacion": event.get("nota_digitalizacion"),
        "notas_internet_archive": event.get("notas_internet_archive"),
        "topics": event.get("topics"),
        "disponible": True,
        "bandas": [{"nombre": event.get("banda")}]
    }

    result = False

    try:
        files_muladar = {
            'imagen': open(event.get("imagen"), "rb")
        }


        files_ia = []
        upload_file = event.get("file")

        if not os.path.exists(upload_file):
            raise FileNotFoundError()

        is_zip = zipfile.is_zipfile(upload_file)

        if is_zip:
            with ZipFile(event.get("file"), 'r') as zip:
                terminal('Extracting all the files now...')
                zip.extractall(path=f'{dname}/tmp')
                files_ia = [f"{dname}/tmp/{file}" for file in zip.namelist() if not file.endswith("/")]
        else:
            files_ia = [upload_file, event.get("imagen")]

        terminal('Uploading the following files to the Internet Archive')
        terminal('*'*10)
        for file in files_ia:
            terminal(file)
        terminal('*'*10)

        #result = upload_to_internet_archive(metadata=metadata_ia, files=files_ia,terminal=terminal)
        #result = result and upload_to_muladar(payload=payload_muladar, files=files_muladar, terminal=terminal)
        result = upload_to_muladar(payload=payload_muladar, files=files_muladar, terminal=terminal, api=settings.value("url_api_lanzamientos"))

        if is_zip:
            terminal('Deleting temporary extracted files...')
            shutil.rmtree(path=f'{dname}/tmp')
            terminal('Files deleted!')

    except Exception as e:
        terminal(str(e))
        terminal("Error opening the file")
    
    return result



def upload_to_muladar(payload, files, terminal, api):
    terminal(f'Uploading El Muladar {payload.get("nombre")}')

    user_el_muladar = settings.value("user_el_muladar")
    password_el_muladar = settings.value("password_el_muladar")
    timeout_time = int(settings.value("timeout_time"))

    try:
        response = requests.post(
            api, 
            data=payload, 
            files=files, 
            timeout=timeout_time,
            auth= HTTPBasicAuth(user_el_muladar, password_el_muladar)
        )
        response.raise_for_status()        
        terminal(f'Success inserting {payload.get("nombre")} in El Muladar')
        terminal('-'*10)
        return True 
    except Exception as e:
        terminal(f'Error sending to El Muladar {str(e)}')
        terminal('-'*10)

    return False


def upload_to_internet_archive(metadata, files, terminal):
    terminal(f'Uploading to Internet Archive "{metadata.get("title")}"')
    
    try:
        identifier = metadata.pop("identifier")

        archive_session = internetarchive.ArchiveSession(config={})
        item = internetarchive.Item(identifier=identifier, archive_session=archive_session)

        s3_access = settings.value('s3_access_key')
        s3_secret = settings.value('s3_secret_key')

        if not internetarchive.get_item(identifier=identifier).exists:
            response = item.upload(files=files, metadata=metadata, access_key=s3_access, secret_key=s3_secret, verbose=True)
            terminal(str(response))
            terminal(f'Success inserting "{metadata.get("title")}" in the Internet Archive.')
        else:
            terminal(f'Item already exists in the Internet Archive, skipping the upload.')
        terminal('-'*10)
        return True
    except Exception as e:
        terminal("There was an error uploading to the Internet Archive")
        terminal(str(e))
        terminal('-'*10)
        return False
