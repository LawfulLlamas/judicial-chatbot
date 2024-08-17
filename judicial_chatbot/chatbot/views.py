from django.shortcuts import render
from django.http import JsonResponse
from .ai_model import chatbot

def home(request):
    return render(request, 'home.html')

def get_response(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        response = chatbot.generate_response(user_input)
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)