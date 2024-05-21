from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from rest_framework import filters, viewsets, status, exceptions
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from dish.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from .filters import CustomRecipeFilter
from .serializers import TagSerializer, IngredientSerializer, ReadRecipeSerializer, WriteRecipeSerializer, BaseRecipeSerializer
from .permissions import IsAuthorOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ReadRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomRecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('post', 'delete'), permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = self.get_queryset().get(pk=pk)
            except Exception:
                raise exceptions.ParseError()
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(dict(errors='Вы уже добавили данный рецепт в избранное.'), status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(BaseRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            recipe = self.get_object()
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(dict(errors='Этого рецепта нет в избранном.'), status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'), permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = self.get_queryset().get(pk=pk)
            except Exception:
                raise exceptions.ParseError()
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(dict(errors='Вы уже добавили данный рецепт в список покупок.'), status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(BaseRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            recipe = self.get_object()
            if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(dict(errors='Этого рецепта нет в списке покупок.'), status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = Recipe.objects.filter(
            shoppingcart__user=request.user
        ).values_list(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(Sum('recipeingredients__amount'))

        shopping_cart_list = HttpResponse(content_type='text/plain', charset="utf-8")
        shopping_cart_list['Content-Disposition'] = 'attachment; filename="Список_покупок.txt"'

        for ingredient in ingredients:
            shopping_cart_list.write(
                f'{ingredient[0]} ({ingredient[1]}) - {ingredient[2]}\n'
            )
        return shopping_cart_list
