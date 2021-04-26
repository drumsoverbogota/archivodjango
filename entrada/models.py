from django.db import models

class Entrada(models.Model):

    NOTICIA = 'noticia'
    BLOG = 'blog'

    TIPO = [
        (NOTICIA, 'Noticia'),
        (BLOG, 'Blog')
    ]

    titulo = models.CharField(max_length=100)
    contenido = models.TextField()
    resumen = models.TextField(blank=True)
    tipo = models.CharField(
        max_length=10,
        choices=TIPO,
        default=NOTICIA
        )
    fecha = models.DateField()

    class Meta:
        managed = False
        db_table = 'entrada'