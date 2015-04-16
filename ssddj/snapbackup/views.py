from django.db import models
from django.forms import ModelForm
from django.shortcuts import render
from django.views.generic import TemplateView
from ssdfrontend.models import SnapJob
from snapbackup.forms import SnapJobForm
from django.views.generic import (
        CreateView, UpdateView
        )

# Create your views here.

class SnapJobCreateView(CreateView):
    snapjobForm = SnapJobForm()
    template_name = "snapbackup/snapconfig.html"
    form_class = SnapJobForm
#    return render_to_response(template_name, {'form': snapjobForm})

