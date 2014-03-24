
from django.shortcuts import render
from django.views.generic import ListView
from ssdfrontend.models import Target

class TargetList(ListView):
        model = Target
