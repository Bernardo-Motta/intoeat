from django.db import migrations

OCASIOES = ["Encontro", "Família", "Amigos", "Trabalho", "Comemoração", "Casual", "Outro"]


def cadastrar_ocasioes(apps, schema_editor):
    Modelo = apps.get_model("restaurantes", "Ocasiao")
    for nome in OCASIOES:
        if not Modelo.objects.filter(nome__iexact=nome).exists():
            Modelo.objects.create(nome=nome)


class Migration(migrations.Migration):
    dependencies = [("restaurantes", "0005_perfil_horario_telefone_fotos")]
    operations = [migrations.RunPython(cadastrar_ocasioes, reverse_code=migrations.RunPython.noop)]
