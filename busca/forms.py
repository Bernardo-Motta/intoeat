from django import forms

from restaurantes.models import Caracteristica, Ocasiao


class BuscaForm(forms.Form):
    q = forms.CharField(label="Nome ou tipo de cozinha", max_length=120, required=False,
                        widget=forms.TextInput(attrs={"placeholder": "Ex.: cantina ou italiana"}))
    ocasioes = forms.ModelMultipleChoiceField(label="Ocasiões", required=False,
                 queryset=Ocasiao.objects.all().order_by("nome"),
                 widget=forms.CheckboxSelectMultiple)
    caracteristicas = forms.ModelMultipleChoiceField(label="Características", required=False,
                 queryset=Caracteristica.objects.all().order_by("nome"),
                 widget=forms.CheckboxSelectMultiple)
