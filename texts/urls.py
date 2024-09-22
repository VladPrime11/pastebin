from django.urls import path
from .views import CreateTextBlockView, RetrieveTextBlockView

urlpatterns = [
    path('create/', CreateTextBlockView.as_view(), name='create_text_block'),
    path('<str:hash>/', RetrieveTextBlockView.as_view(), name='retrieve_text_block'),
]
