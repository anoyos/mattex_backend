from django import forms
from django.forms import ModelForm
from SMMapp.models import *

from datetime import datetime


class PDF(forms.Form):
    file1 = forms.FileField()  # for creating file input
    file2 = forms.FileField()  # for creating file input