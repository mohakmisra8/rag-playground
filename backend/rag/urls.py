# backend/rag/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('ping', views.ping),
    path('upload', views.upload_docs),     # POST
    path('search', views.search_docs),     # POST
    path('ask', views.ask),                # POST (optional RAG answer)
]
