from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Job, Application

class CustomUserAdmin(UserAdmin):
    model=User
    list_display=('email','role','is_active')
    ordering=('email',)
    fieldsets=(
        (None,{'fields':('email','password')}),
        ('Permissions',{'fields':('role','is_active','is_staff','is_superuser')}),
        ('Dates',{'fields':('last_login','created_at')}),
    )
    add_fieldsets=(
        (None,{
            'classes':('wide',),
            'fields':('email','password1','password2','role','is_active'),
        }),
    )
    search_fields=('email',)

admin.site.register(User,CustomUserAdmin)

admin.site.register(Job)
admin.site.register(Application)