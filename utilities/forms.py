from django import forms

class UploadFileForm(forms.Form):
    docs = forms.FileField(
        widget=forms.FileInput(attrs={'multiple': False}),
        label='Select DOCX files'
    )

class UploadSplitFileForm(forms.Form):
        doc = forms.FileField()

class FileUploadForm(forms.Form):
    doc_file = forms.FileField(label='Select a DOC file to convert')
