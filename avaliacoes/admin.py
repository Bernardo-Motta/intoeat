from django.contrib import admin
from .models import Avaliacao


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("restaurante", "usuario", "nota", "data")
    list_filter = ("nota", "data")
    search_fields = ("restaurante__nome", "usuario__email")
    readonly_fields = ("data",)
