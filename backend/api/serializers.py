from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from dish.models import Tag, Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
from .fields import Base64ImageField


User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True, source='ingredient')
    name = serializers.StringRelatedField(read_only=True, source='ingredient')
    measurement_unit = serializers.SlugRelatedField(read_only=True, source='ingredient', slug_field='measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class BaseIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class BaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ReadRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = AuthorSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(read_only=True, many=True, source='recipeingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()
        return False


class WriteRecipeSerializer(serializers.ModelSerializer):
    ingredients = BaseIngredientSerializer(many=True, source='recipeingredients')
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')

    def to_representation(self, instance):
        serializer = ReadRecipeSerializer(instance=instance, context={'request': self.context.get('request')})
        return serializer.data

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredients')  # ПОЧЕМУ RECIPEINGREDIENTS???
        # tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(**ingredient, recipe=recipe)
        # recipe.tags.set(tags)
        return recipe
        # return super().create(validated_data)

    def update(self, recipe, validated_data):
        new_ingredients = validated_data.pop('recipeingredients')
        # new_tags = validated_data.pop('tags')
        recipe.ingredients.clear()
        for ingredient in new_ingredients:
            RecipeIngredient.objects.create(**ingredient, recipe=recipe)
        recipe.tags.clear()  # set(new_tags, clear=True)
        return super().update(recipe, validated_data)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError(detail='Необходимо указать ингредиенты.')
        ingredients_list = (ingredient['ingredient'] for ingredient in ingredients)
        if len(ingredients) > len(set(ingredients_list)):
            raise ValidationError(detail='В рецепте не должно быть повторяющихся ингредиетов.')
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError(detail='Необходимо указать тэги.')
        if len(tags) > len(set(tags)):
            raise ValidationError(detail='В рецепте не должно быть повторяющихся тэгов.')
        return tags

    def validate(self, data):
        if not data.get('recipeingredients'):
            raise ValidationError('Укажите поле ingredients.')
        if not data.get('tags'):
            raise ValidationError('Укажите поле tags.')
        return data
