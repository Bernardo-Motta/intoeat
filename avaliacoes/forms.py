from django import forms
from restaurantes.models import Caracteristica
from .models import Avaliacao


class AvaliacaoForm(forms.ModelForm):
    # A opção vazia impede que a nota 0 seja enviada como padrão sem escolha explícita.
    nota = forms.TypedChoiceField(
        label="Nota (0 a 5 estrelas)",
        required=True,
        coerce=int,
        choices=[(i, f"{i} {'estrela' if i == 1 else 'estrelas'} · {'★' * i}{'☆' * (5 - i)}") for i in range(6)],
        widget=forms.RadioSelect,
    )
    caracteristicas = forms.ModelMultipleChoiceField(
        label="Tags da experiência (opcional)",
        queryset=Caracteristica.objects.order_by("nome"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Avaliacao
        fields = ["nota", "comentario", "caracteristicas"]
        widgets = {
            "comentario": forms.Textarea(attrs={
                "rows": 4, "placeholder": "Conte como foi sua experiência (opcional)",
            }),
        }
        labels = {"comentario": "Comentário (opcional)"}

    def clean_comentario(self):
        return (self.cleaned_data.get("comentario") or "").strip()
