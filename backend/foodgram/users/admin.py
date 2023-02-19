from django.contrib import admin

from .models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email',)


admin.site.register(Follow)
