from django.shortcuts import render
from django.http import JsonResponse
from .ai_model import JudicialChatbot

def home(request):
    return render(request, 'home.html')

chatbot = JudicialChatbot()

def chat_view(request):
    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        response = chatbot.generate_response(user_input)
        return JsonResponse({'response': response})
    return render(request, 'chat.html')
