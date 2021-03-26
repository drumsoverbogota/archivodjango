from django.contrib import admin


from .models import Banda
from .models import Lanzamiento
from .models import Publicacion
from .models import BandaLanzamiento
# Register your models here.

admin.site.register(Banda)
admin.site.register(Lanzamiento)
admin.site.register(Publicacion)
admin.site.register(BandaLanzamiento)

