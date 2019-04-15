from django.contrib import admin
from .models import Element

@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ('id','value','changed', 'parentID', 'level','status')

# Register your models here.
