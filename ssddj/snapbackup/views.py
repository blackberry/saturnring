from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
class SnapConfigView(TemplateView):
    template_name = "snapbackup/snapconfig.html"

    def get_context_data(self, **kwargs):
        context = super(SnapConfigView, self).get_context_data(**kwargs)
        context['foo']='bar'
#        context['targets']=context['targets']
        return context



