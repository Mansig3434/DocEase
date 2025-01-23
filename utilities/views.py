import os
from django.shortcuts import render, redirect
from django.http import HttpResponse,FileResponse,Http404
from django.conf import settings
from django.template.context_processors import media
from .forms import UploadFileForm
from docx import Document
from .utils import merge_doc_files
from .models import UploadedDocument
from django.contrib import messages
from .forms import UploadSplitFileForm
from .utils import split_docx_by_sections
from django.core.files.storage import FileSystemStorage
from .forms import FileUploadForm
from django.core.files.storage import default_storage
from .utils import convert_docx_to_pdf
from .utils import apply_watermark_to_doc
from .utils import docx_to_pptx




def index(request):
    return render(request, 'index.html')

def merge_doc(request):
    return render(request, 'merge_docs.html')

def doc_to_pdf(request):
    return render(request,'doc_to_pdf.html')

def watermarking(request):
    return  render(request,'watermarking.html')


# merge document
def merge_docs(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('docs')

            if len(files) < 2:
                messages.error(request, "Please upload at least two documents to merge.")
                return redirect('merge_docs')

            for file in files:
                UploadedDocument.objects.create(file=file)
            merged_path = merge_doc_files(files)
            request.session['merged_file_path'] = merged_path
            return redirect('merge_result')

    else:
        form = UploadFileForm()

    return render(request, 'merge_docs.html', {'form': form})


def merge_result(request):
    merged_file_path = request.session.get('merged_file_path', None)

    if merged_file_path:
        return render(request, 'merge_result.html', {'merged_file_path': merged_file_path})
    else:
        return redirect('merge_docs')


def download_merged_file(request):
    merged_file_path = request.session.get('merged_file_path', None)

    if merged_file_path:
        with open(merged_file_path, 'rb') as merged_file:
            response = HttpResponse(
                merged_file.read(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = 'attachment; filename=merged_document.docx'
            return response
    else:
        return redirect('merge_docs')


# split document
def split_doc(request):
    if request.method == "POST" and request.FILES["doc_file"]:
        doc_file = request.FILES["doc_file"]
        fs = FileSystemStorage()
        filename = fs.save(doc_file.name, doc_file)
        uploaded_file_url = fs.path(filename)

        split_files = split_docx_by_sections(uploaded_file_url, fs)

        context = {
            "split_files": split_files,
        }
        return render(request, "split_result.html", context)

    return render(request, "split_docs.html")


def split_result(request):
    return render(request, "split_result.html")


def download_split_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            response = HttpResponse(f.read(),content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            response["Content-Disposition"] = f"attachment; filename={filename}"
            return response
    else:
        raise Http404("File not found.")


# doc_to_pdf

def doc_to_pdf(request):
    if request.method == 'POST' and request.FILES.get('doc_file'):
        doc_file = request.FILES['doc_file']
        fs = FileSystemStorage()

        doc_path = fs.save(doc_file.name, doc_file)
        doc_path_full = fs.path(doc_path)

        pdf_filename = os.path.splitext(doc_file.name)[0] + '.pdf'
        pdf_path = fs.path(pdf_filename)

        try:
            convert_docx_to_pdf(doc_path_full, pdf_path)
        except Exception as e:
            return render(request, 'doc_to_pdf.html', {'error': f'Conversion failed: {e}'})

        fs.delete(doc_path)

        return render(request, 'doc_to_pdf_result.html', {'pdf_file': pdf_filename})

    return render(request, 'doc_to_pdf.html')


def download_pdf_file(request, filename):
    filename = os.path.basename(filename)
    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    else:
        raise Http404("File not found.")


#watermarking

def watermark_doc(request):
    if request.method == 'POST' and 'doc_file' in request.FILES:
        doc_file = request.FILES['doc_file']
        watermark_text = request.POST.get('watermark_text', 'Watermark')

        fs = FileSystemStorage(location='media/uploads')
        doc_path = fs.save(doc_file.name, doc_file)
        doc_path_full = fs.path(doc_path)
        watermarked_dir = os.path.join(settings.MEDIA_ROOT, 'watermarked_docs')
        os.makedirs(watermarked_dir, exist_ok=True)

        watermarked_filename = f'watermarked_{doc_file.name}'
        watermarked_file_path = os.path.join(watermarked_dir, watermarked_filename)
        try:
            apply_watermark_to_doc(doc_path_full, watermarked_file_path, watermark_text)
        except Exception as e:
            print(f"Failed to apply watermark: {e}")
            return render(request, 'watermarking.html', {'error': f'Failed to apply watermark:'})
        fs.delete(doc_path)

        return render(request, 'watermarking_result.html', {'watermarked_file': watermarked_filename})

    return render(request, 'watermarking.html')



def download_watermarked_file(request, filename):
    file_path = os.path.join('media', 'watermarked_docs', filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    raise Http404("File not found.")


#doc to ppt

def convert_docx_to_pptx(request):
    if request.method == 'POST' and request.FILES['docfile']:
        doc_file = request.FILES['docfile']
        fs = FileSystemStorage()
        filename = fs.save(doc_file.name, doc_file)
        input_path = os.path.join(settings.MEDIA_ROOT, filename)
        output_filename = f"{os.path.splitext(filename)[0]}.pptx"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        docx_to_pptx(input_path, output_path)
        return render(request, 'doc_to_ppt_result.html', {
            'download_url': fs.url(output_filename)
        })

    return render(request, 'doc_to_ppt.html')  

def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response
    else:
        return HttpResponse("File not found.", status=404)


