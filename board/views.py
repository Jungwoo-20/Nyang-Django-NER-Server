from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from Disease import nyang_doc_search
from django.views import View
import json


def post(request):
    try:
        request = json.loads(request.body)
        print(request)
        body = request['content']
        print(body)
        dummy_data = nyang_doc_search.document_search(body)
        # return HttpResponse(dummy_data)
        return JsonResponse({"pet_disease_search_info": dummy_data}, status=200)
    except Exception as e:
        dummy_data = {
            'error': e
        }
        return JsonResponse(dummy_data)
