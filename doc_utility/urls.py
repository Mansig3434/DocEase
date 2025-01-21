"""
URL configuration for doc_utility project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from utilities import views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
def favicon_view(request):
    return HttpResponse(status=204)


urlpatterns = [
    path('', views.index, name='index'),
    path('merge-docs/', views.merge_docs, name='merge_docs'),
    path('merge-result/', views.merge_result, name='merge_result'),
    path('download-merged-file/', views.download_merged_file, name='download_merged_file'),
    path('split-docs/', views.split_doc, name='split_docs'),
    path('split-result/', views.split_result, name='split_result'),
    path('download-split-file/<str:filename>/', views.download_split_file, name='download_split_file'),
    path('doc-to-pdf/', views.doc_to_pdf, name='doc_to_pdf'),
    path('doc-to-pdf/', views.doc_to_pdf, name='doc_to_pdf'),
    path('download-pdf/<str:filename>/', views.download_pdf_file, name='download_pdf_file'),
    path('watermark-doc/', views.watermark_doc, name='watermark_doc'),
    path('download-watermarked-file/<str:filename>/', views.download_watermarked_file, name='download_watermarked_file'),
    path('convert-doc-to-ppt/', views.convert_docx_to_pptx, name='convert_docx_to_pptx'),
    path('download/<str:filename>/', views.download_file, name='download_file'),
    path('protect-doc/', views.protect_doc_with_password, name='protect_doc_with_password'),
    path('download/<str:filename>/', views.download_file, name='download_file'),
]




urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
