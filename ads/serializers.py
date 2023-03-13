from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str

from ads.models import Category, Ad
from rest_framework import serializers

from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategoryPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Category
        fields = ('id', 'name')


class AdListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        depth = 2
        fields = '__all__'


class CreatableSlugRelatedField(serializers.SlugRelatedField):

    def to_internal_value(self, data):
        try:
            print(type(data))
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except ObjectDoesNotExist:
            self.fail('does_not_exist', slug_name=self.slug_field, value=smart_str(data))
        except (TypeError, ValueError):
            self.fail('invalid')


class AdPostSerializer(serializers.ModelSerializer):
    category = CreatableSlugRelatedField(
        queryset=Category.objects.all(),
        many=True,
        slug_field='name',
    )
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username'
    )
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Ad
        fields = ('id', 'name', 'author', 'price', 'description', 'is_published', 'image', 'category')


class PatchModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(PatchModelSerializer, self).__init__(*args, **kwargs)


class AdUpdateSerializer(PatchModelSerializer):
    category = CreatableSlugRelatedField(
        queryset=Category.objects.all(),
        many=True,
        slug_field='name',
    )
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username'
    )
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Ad
        fields = '__all__'
