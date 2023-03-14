from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import *

router = routers.SimpleRouter()
router.register('location', LocationViewSet)

urlpatterns = [
    path('', UserListView.as_view()),
    path('<int:pk>/', UserDetailView.as_view()),
    path('<int:pk>/update/', UserUpdateView.as_view()),
    path('<int:pk>/delete/', UserDeleteView.as_view()),
    path('create/', UserCreateView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='get_user_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_user_token'),

]

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
