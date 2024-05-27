from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from dish.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    RecipeIngredient)
from .filters import CustomRecipeFilter
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    WriteRecipeSerializer,
    BaseRecipeSerializer)
from .pagination import LimitNumberPagination
from .permissions import IsAuthorOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ReadRecipeSerializer
    pagination_class = LimitNumberPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomRecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def favorite_shoppingcart_logic(self, request, pk, model):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = self.get_queryset().get(pk=pk)
            except Recipe.DoesNotExist:
                raise ParseError(detail='Такого рецепта не существует.')
            _, creation_status = model.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not creation_status:
                raise ParseError(detail='Данный рецепт уже добавлен.')
            return Response(
                BaseRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        recipe = self.get_object()
        try:
            model.objects.get(user=user, recipe=recipe).delete()
        except model.DoesNotExist:
            raise ParseError(detail='Этот рецепт еще не добавлен.')
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        return self.favorite_shoppingcart_logic(request, pk, Favorite)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        return self.favorite_shoppingcart_logic(request, pk, ShoppingCart)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcart__user=request.user
            ).values_list(
                'ingredient__name', 'ingredient__measurement_unit'
            ).annotate(amount=Sum('amount'))
        )
        shopping_cart_list = HttpResponse(
            content_type='text/plain', charset="utf-8"
        )
        shopping_cart_list['Content-Disposition'] = (
            'attachment; filename="Shopping_cart.txt"'
        )

        for ingredient, measurement_unit, amount in ingredients:
            shopping_cart_list.write(
                f'{ingredient} ({measurement_unit}) - {amount}\n'
            )
        return shopping_cart_list
