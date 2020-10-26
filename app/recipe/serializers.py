from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe

class TagSerializer(serializers.ModelSerializer):
    """Serialzer for tag objects"""

    class Meta:
        model =  Tag
        fields = ('id', 'name')
        read_only_fields = ('id', )


class IngredientSerializer(serializers.ModelSerializer):
    """Serialzer for ingredient objects"""

    class Meta:
        model =  Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id', )

class RecipeSerializer(serializers.ModelSerializer):
    """Serialzer for recipe objects"""
    ingredient = serializers.PrimaryKeyRelatedField(
    many=True,
    queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
    many=True,
    queryset=Tag.objects.all()
    )

    class Meta:
        model =  Recipe
        fields = ('id', 'title','ingredient','tags','time_minutes', 'price',
        'link' )
        read_only_fields = ('id', )
