from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.template.loader import render_to_string

import pdb
# pdb.set_trace()

from .models import *


def wanted(request):
    return render(
        request,
        'onmyoji/wanted.html',
        {'wanted': Wanted.get_all(), 'hint': Hint.get_all_with_wanted()}
    )


def find(request):
    if request.method == 'POST':
        wanted_id = request.POST.getlist('data[]')
        wanted_id = wanted_id[0:3]

        # wanted_id = ['5a697e690a975a0108275c29']
        if len(wanted_id) > 0:
            wanted_data = Wanted.get_appearance_by_ids(wanted_id)
            # return JsonResponse(wanted_data)
            recommend_data = Map.get_most_appearance_by_wanted_ids(wanted_id)
            # return JsonResponse(recommend_data)   # Not working because recommend_data is list
            if wanted_data is not False and recommend_data is not False:
                if len(wanted_data) > 0:
                    html = render_to_string('onmyoji/find_result.html',
                                            {'wanted_data': wanted_data, 'recommendations': recommend_data})
                    return JsonResponse({'success': True, 'html': html})
                else:
                    return JsonResponse({'success': False, 'msg': 'Not found any location!'})
            else:
                return JsonResponse({'success': False, 'msg': 'Error occurred!'})
        else:
            return JsonResponse({'success': False, 'msg': 'Selection empty!'})
    else:
        raise Http404


def all(request):
    # pdb.set_trace()
    data = Wanted.get_all_appearance()
    # return JsonResponse(data)
    return render(request, 'onmyoji/all.html', {'data': data})
