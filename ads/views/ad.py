import json


from django.db.models import Q
from django.http import JsonResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from ads.models import Ad, Selection
from ads.permissions import SelectionUpdatePermission

from ads.serializers import AdListSerializer, AdPostSerializer, AdUpdateSerializer, SelectionSerializer, \
    SelectionDetailSerializer, SelectionListSerializer, AdDetailSerializer


def index(request) -> JsonResponse:
    return JsonResponse({"status": "ok"}, status=200)


class SelectionListView(ListAPIView):
    queryset = Selection.objects.all()
    serializer_class = SelectionListSerializer


class SelectionRetrieveView(RetrieveAPIView):
    queryset = Selection.objects.all()
    serializer_class = SelectionDetailSerializer


class SelectionCreateView(CreateAPIView):
    queryset = Selection.objects.all()
    serializer_class = SelectionSerializer
    permission_classes = [IsAuthenticated]


class SelectionUpdateView(UpdateAPIView):
    queryset = Selection.objects.all()
    serializer_class = SelectionSerializer
    permission_classes = [IsAuthenticated, SelectionUpdatePermission]


class SelectionDeleteView(DestroyAPIView):
    queryset = Selection.objects.all()
    serializer_class = SelectionSerializer
    permission_classes = [IsAuthenticated, SelectionUpdatePermission]


class AdListView(ListAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdListSerializer

    def get(self, request, *args, **kwargs):
        search_query = None

        category_ids = request.GET.getlist('cat', None)
        for category_id in category_ids:
            if search_query is None:
                search_query = Q(category__id__exact=category_id)
            else:
                search_query |= Q(category__id__exact=category_id)

        # 127.0.0.1:8000/ad?text=Стол
        text = request.GET.get('text', None)
        if text:
            self.queryset = self.queryset.filter(
                name__icontains=text
            )

        location = request.GET.get('location', None)
        if location:
            if search_query is None:
                search_query = Q(author__location__name__icontains=location)
            else:
                search_query |= Q(author__location__name__icontains=location)

        if price_from := request.GET.get('price_from', None):
            self.queryset = self.queryset.filter(price__gte=price_from)
        if price_to := request.GET.get('price_to', None):
            self.queryset = self.queryset.filter(price__lte=price_to)

        if search_query:
            self.queryset = self.queryset.select_related('author').prefetch_related('category').filter(search_query).\
                order_by('-price')
        return super(AdListView, self).get(request, *args, **kwargs)


@method_decorator(csrf_exempt, name="dispatch")
class AdCreateView(CreateView):
    model = Ad
    fields = '__all__'

    def post(self, request, *args, **kwargs):
        super(AdCreateView, self).post(request, *args, **kwargs)
        data = json.loads(request.body)
        serializer = AdPostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False)
        return JsonResponse(serializer.errors, safe=False, status=422)


class AdDetailView(RetrieveAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdDetailSerializer
    permission_classes = [IsAuthenticated]


@method_decorator(csrf_exempt, name="dispatch")
class AdUpdateView(UpdateView):
    model = Ad
    fields = ('name',)

    def patch(self, request, *args, **kwargs):
        super(AdUpdateView, self).post(request, *args, **kwargs)
        data = json.loads(request.body)
        serializer = AdUpdateSerializer(data=data, partial=True)
        if serializer.is_valid():
            serializer.update(self.object, serializer.validated_data)
            model = AdListSerializer(self.object)
            return JsonResponse(model.data, safe=False)

        return JsonResponse(serializer.errors, safe=False, status=422)


@method_decorator(csrf_exempt, name="dispatch")
class AdDeleteView(DeleteView):
    model = Ad
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        super(AdDeleteView, self).delete(request, *args, **kwargs)
        return JsonResponse({'status': 'ok'}, safe=False, status=204)


@method_decorator(csrf_exempt, name="dispatch")
class AdImageView(UpdateView):
    model = Ad
    fields = ('name', 'image')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.image = request.FILES['image']
        self.object.save()
        return JsonResponse(
            {
                'id': self.object.id,
                'name': self.object.name,
                'image': self.object.image.url
            }
        )
