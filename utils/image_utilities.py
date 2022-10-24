from django.core.files.uploadedfile import InMemoryUploadedFile

from io import BytesIO
from PIL import Image

import os
import sys

def upload_image(nueva_entrada):

    id_concierto = nueva_entrada.id
    nombrecorto = nueva_entrada.nombrecorto

    imagen = nueva_entrada.imagen

    if imagen:
        output = BytesIO()
        output_thumbnail = BytesIO()

        _, extension = os.path.splitext(str(imagen))

        extension = extension.lower()
        filetype = extension[1:]
        if filetype == 'jpg':
            filetype = 'jpeg'
        
        ruta =  str(id_concierto) + nombrecorto + 'image' + extension
        ruta_thumbnail = str(id_concierto) + nombrecorto + 'image_small' + extension

        im = Image.open(imagen)
        im.thumbnail(resize(800, im.size[0], im.size[1]))
        im.save(output, filetype)

        nueva_entrada.imagen = InMemoryUploadedFile(
            output,
            'FileField',
            ruta,
            'image/' + filetype,
            sys.getsizeof(output),
            None
        )

        im = Image.open(imagen)
        im.thumbnail(resize(200, im.size[0], im.size[1]))
        im.save(output_thumbnail, filetype)

        nueva_entrada.imagen_thumbnail = InMemoryUploadedFile(
            output_thumbnail,
            'FileField',
            ruta_thumbnail,
            'image/' + filetype,
            sys.getsizeof(output_thumbnail),
            None
        )
    
    return nueva_entrada


def resize(max_width, width, height):
    wpercent = (max_width/float(width))
    hsize = int((float(height)*float(wpercent)))
    return (max_width, hsize)
