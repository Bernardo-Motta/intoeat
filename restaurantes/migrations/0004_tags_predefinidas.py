from django.db import migrations


TAGS_PREDEFINIDAS = [
    'Romântico',
    'Tranquilo',
    'Música ao vivo',
    'Área externa',
    'Adequado para crianças',
    'Pet friendly',
    'Preço acessível',
    'Sofisticado',
    'Animado',
]


def criar_tags(apps, schema_editor):
    Caracteristica = apps.get_model("restaurantes", "Caracteristica")
    for nome in TAGS_PREDEFINIDAS:
        # Não duplica tags que já existam no banco, incluindo dados antigos.
        if not Caracteristica.objects.filter(nome=nome).exists():
            Caracteristica.objects.create(nome=nome)


class Migration(migrations.Migration):
    dependencies = [("restaurantes", "0003_renomear_campos")]
    operations = [migrations.RunPython(criar_tags, reverse_code=migrations.RunPython.noop)]
