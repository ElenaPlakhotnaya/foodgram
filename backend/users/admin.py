from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name',
                    'last_name', 'subscribing_count', 'recipe_count')
    search_fields = ('email', 'username',)
    empty_value_display = '---'

    @admin.display(description='Количество подписчиков')
    def subscribing_count(self, obj):
        return obj.subscribing.count()

    @admin.display(description='Количество рецептов')
    def recipe_count(self, obj):
        return obj.recipes.count()


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscribing')
    empty_value_display = '---'


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.unregister(Group)
