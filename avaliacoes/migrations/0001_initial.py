from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("restaurantes", "0001_initial")]
    operations = [
        migrations.CreateModel(name="Avaliacao", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("nota", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
            ("comentario", models.TextField()),
            ("data", models.DateTimeField(auto_now_add=True)),
            ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="avaliacoes", to=settings.AUTH_USER_MODEL)),
            ("restaurante", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="avaliacoes", to="restaurantes.restaurante")),
            ("ocasioes", models.ManyToManyField(blank=True, related_name="avaliacoes", to="restaurantes.ocasiao")),
            ("caracteristicas", models.ManyToManyField(blank=True, related_name="avaliacoes", to="restaurantes.caracteristica")),
        ], options={"ordering": ["-data"]}),
        migrations.AddConstraint(model_name="avaliacao", constraint=models.CheckConstraint(condition=models.Q(nota__gte=0, nota__lte=5), name="avaliacao_nota_entre_0_e_5")),
    ]
