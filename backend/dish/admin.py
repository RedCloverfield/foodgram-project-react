from django.contrib import admin

from .models import Recipe, Ingredient, Tag, RecipeIngredient, RecipeTag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    fields = ('ingredient', 'amount')


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    fields = ('tag',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = (
        RecipeIngredientInline,
        RecipeTagInline
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
