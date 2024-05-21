from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet
from .views import TagViewSet, IngredientViewSet, RecipeViewSet

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('users', CustomUserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
