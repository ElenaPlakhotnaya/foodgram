from django.contrib import admin

from users.models import User, Subscription
from rest_framework.authtoken.models import TokenProxy
from django.contrib.auth.models import Group

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'subscribing_count', 'recipe_count')
    search_fields = ('email', 'username',)
    empty_value_display = '---'

    def subscribing_count(self, obj):
        return obj.subscribing.count()

    def recipe_count(self, obj):
        return obj.recipe_set.count()

    subscribing_count.short_description = 'Количество подписчиков'
    recipe_count.short_description = 'Количество рецептов'

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscribing')
    empty_value_display = '---'


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.unregister(Group)
