from django.forms import ModelForm
from .models import Room

class RoomForm(ModelForm):
    class Meta:  #MetaData
        model = Room
        fields = '__all__'