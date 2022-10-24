from rest_framework import serializers

from archivo.models import Banda

class BandasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banda
        fields = '__all__'
