from django import forms
from .models import Avaliacao


class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ["nota", "comentario"]
        widgets = {
            "nota": forms.Select(choices=[(i, str(i)) for i in range(6)]),
            "comentario": forms.Textarea(attrs={"rows": 4, "placeholder": "Conte como foi sua experiência"}),
        }

    def clean_comentario(self):
        comentario = self.cleaned_data["comentario"].strip()
        if not comentario:
            raise forms.ValidationError("Escreva um comentário sobre sua experiência.")
        return comentario
