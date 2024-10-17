from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
