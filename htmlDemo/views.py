from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404


# Create your views here.
def wanted(request):
    # return HttpResponse('New')
    return render(request, 'htmlDemo/wanted.html')
