from django import forms
from random import choice
from string import ascii_lowercase, digits


class UploadFileForm(forms.Form):
	title = choice(5, ascii_lowercase + digits)
	file = forms.ImageField()
