import json

from django.http import JsonResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from ads.models import Category
from ads.serializers import CategorySerializer, CategoryPostSerializer


class CategoryListView(ListView):
    model = Category

    def get(self, request, *args, **kwargs) -> JsonResponse:
        super().get(request, *args, **kwargs)

        cat_serializer = CategorySerializer(self.object_list.order_by('name'), many=True)
        return JsonResponse(cat_serializer.data, safe=False, status=200)



@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    fields = '__all__'

    def post(self, request, *args, **kwargs) -> JsonResponse:
        super(CategoryCreateView, self).post(request, *args, **kwargs)
        data = json.loads(request.body)

        serializer = CategoryPostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False)
        return JsonResponse(serializer.errors, safe=False, status=422)


class CategoryDetailView(DetailView):
    model = Category

    def get(self, request, *args, **kwargs) -> JsonResponse:
        try:
            super(CategoryDetailView, self).get(request, *args, **kwargs)
        except Http404 as error:
            return JsonResponse({'error': error.args}, status=404)
        categories_serializer = CategorySerializer(self.object)

        return JsonResponse(categories_serializer.data, safe=False, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['name']

    def patch(self, request, *args, **kwargs) -> JsonResponse:
        super(CategoryUpdateView, self).post(request, *args, **kwargs)
        data = json.loads(request.body)
        serializer = CategoryPostSerializer(data=data, partial=True)
        if serializer.is_valid():
            serializer.update(self.object, serializer.validated_data)
            model = CategorySerializer(self.object)
            return JsonResponse(model.data, safe=False)
        return JsonResponse(serializer.errors, safe=False, status=422)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    success_url = '/'

    def delete(self, request, *args, **kwargs) -> JsonResponse:
        super(CategoryDeleteView, self).delete(request, *args, **kwargs)

        return JsonResponse({'status': 'ok'}, safe=False, status=204)
