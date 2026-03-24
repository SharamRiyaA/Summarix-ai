from django.urls import path

from .views import SummaryCreateView, SummaryDeleteView, SummaryDetailView, SummaryListView


urlpatterns = [
    path("", SummaryListView.as_view(), name="summary-list"),
    path("create/", SummaryCreateView.as_view(), name="summary-create"),
    path("<int:pk>/", SummaryDetailView.as_view(), name="summary-detail"),
    path("<int:pk>/delete/", SummaryDeleteView.as_view(), name="summary-delete"),
]
