from django import forms

from .models import Usuario


class PerfilForm(forms.ModelForm):
    """Formulario de edicao dos dados pessoais do proprio usuario."""

    class Meta:
        model = Usuario
        fields = ["nome_completo", "email", "biografia", "foto"]
        labels = {
            "nome_completo": "Nome completo",
            "email": "Login (e-mail)",
            "biografia": "Biografia",
            "foto": "Foto de perfil",
        }
        widgets = {
            "biografia": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_email(self):
        # O manager guarda e-mails em minusculas, e a restricao unique do banco
        # diferencia maiusculas de minusculas. Normalizamos e checamos aqui para
        # "ANA@x.com" e "ana@x.com" contarem como o mesmo login.
        email = self.cleaned_data["email"].lower()
        ja_existe = (
            Usuario.objects.filter(email__iexact=email)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if ja_existe:
            raise forms.ValidationError("Já existe um usuário com este e-mail.")
        return email
