from django.contrib import admin
from .models import URL

@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'url', 'created_at', 'access_count')
    search_fields = ('short_code', 'url')
    readonly_fields = ('created_at', 'updated_at')
