from django.urls import path

from .views import Get_Configuration,ExportExcelView

urlpatterns = [
    path("extension/config",Get_Configuration.as_view(), name="configuration_it"),
    path("export-excel/", ExportExcelView.as_view(), name="export-excel"),
]