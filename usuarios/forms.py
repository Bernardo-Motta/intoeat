from django import forms
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, UnidentifiedImageError
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


MAX_FOTO_BYTES = 5 * 1024 * 1024
MAX_FOTO_DIMENSAO = 4096


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

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        # Uma foto existente pode permanecer sem novo upload.
        if not isinstance(foto, UploadedFile):
            return foto
        if foto.size > MAX_FOTO_BYTES:
            raise forms.ValidationError("A foto deve ter no máximo 5 MB.")
        try:
            foto.seek(0)
            with Image.open(foto) as imagem:
                largura, altura = imagem.size
                formato = imagem.format
            foto.seek(0)
        except (UnidentifiedImageError, OSError, ValueError):
            raise forms.ValidationError("Envie um arquivo de imagem válido.")

        if formato not in ("PNG", "JPEG"):
            raise forms.ValidationError("A foto deve estar no formato PNG ou JPEG.")
        if largura > MAX_FOTO_DIMENSAO or altura > MAX_FOTO_DIMENSAO:
            raise forms.ValidationError("A foto deve ter no máximo 4096 pixels em cada dimensão.")
        return foto

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


class CadastroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("nome_completo", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe um usuário com este e-mail.")
        return email