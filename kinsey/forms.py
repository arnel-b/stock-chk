from django import forms


class ImportFileForm(forms.Form):
	# filename = forms.CharField(max_length=300)
	file = forms.FileField()
