from django.db import models
from django.forms import ModelForm
from django.shortcuts import render
from django.views.generic import TemplateView
from ssdfrontend.models import SnapJob
from django.views.generic import (
        CreateView, UpdateView
        )

# Create your views here.

class SnapJobForm(ModelForm):
    class Meta:
        model = SnapJob
        fields = ['numsnaps','iqntar','cronstring','enqueued','run_now']

class SnapConfigView(TemplateView):
    template_name = "snapbackup/snapconfig.html"

    def get_context_data(self, **kwargs):
        context = super(SnapConfigView, self).get_context_data(**kwargs)
        context['foo']='bar'
#        context['targets']=context['targets']
        return context


class SnapJobCreateView(CreateView):
    model = SnapJob
    template_name = "snapbackup/snapconfig.html"
    fields = ['numsnaps','iqntar','cronstring','enqueued','run_now']
