from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . import chatbot

@csrf_exempt
def chat(request):
    return chatbot.chat(request)

def home(request):
    return chatbot.home(request)
