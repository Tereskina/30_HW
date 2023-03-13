from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework import routers

from users.views import *

router = routers.SimpleRouter()
router.register('location', LocationViewSet)


urlpatterns = [
    path('', UserListView.as_view()),
    path('<int:pk>/', UserDetailView.as_view()),
    path('<int:pk>/update/', UserUpdateView.as_view()),
    path('<int:pk>/delete/', UserDeleteView.as_view()),
    path('create/', UserCreateView.as_view()),

]

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
