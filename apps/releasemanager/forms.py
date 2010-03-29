#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from releasemanager.models import *
import datetime

class BuildForm(forms.ModelForm):
    jar_file_upload = forms.FileField()
    jad_file_upload = forms.FileField()    
    
    class Meta:
        model = Build
        exclude = ('jar_file', 'jad_file','uploaded_by',
                   'package_created', 'released_by', 'released')
           
        
