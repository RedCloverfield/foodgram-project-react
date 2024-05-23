from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (
    Recipe,
    Ingredient,
    Tag,
    Favorite,
    ShoppingCart,
    RecipeIngredient,
    RecipeTag
)


User = get_user_model()


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    fields = ('ingredient', 'amount', 'measure')
    min_num = 1
    extra = 0


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    fields = ('tag',)
    min_num = 1
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    inlines = (
        RecipeIngredientInline,
        RecipeTagInline
    )
    list_display = (
        'name',
        'author',
        'favorites'
    )
    list_filter = (
        'author',
        'name',
        'tags'
    )

    @admin.display(description="В избранном")
    def favorites(self, obj):
        return obj.favorites.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = (
        'name',
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
