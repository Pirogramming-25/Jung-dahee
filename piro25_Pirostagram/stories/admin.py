from django.contrib import admin

from .models import Story, StoryItem


class StoryItemInline(admin.TabularInline):
    model = StoryItem
    extra = 1


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    inlines = [StoryItemInline]
