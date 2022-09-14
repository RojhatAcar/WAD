from django.contrib import admin
from upskill_photography.models import UserProfile, Picture, Comment, Category

class CategoryAdmin(admin.ModelAdmin):
    prepoluated_fields = {'slug': ('name',)}


admin.site.register(UserProfile)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Picture)
admin.site.register(Comment)