from django import forms
from .models import Restaurante
from .services import validar_cnpj

class RestauranteForm(forms.ModelForm):
    class Meta:
        model = Restaurante
        fields = ["nome", "categoria", "descricao", "endereco", "cidade", "cnpj"]

    def clean_cnpj(self):
        return validar_cnpj(self.cleaned_data["cnpj"])
