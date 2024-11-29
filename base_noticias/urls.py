from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoticiaViewSet, NoticiaCreateUpdateView

router = DefaultRouter()
router.register(r'noticias', NoticiaViewSet, basename='noticias')

urlpatterns = router.urls + [
    path('noticia-create-update/', NoticiaCreateUpdateView.as_view(), name='noticia-create-update')
]