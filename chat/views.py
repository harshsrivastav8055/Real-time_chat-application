from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Chat, Message

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('chat_home')
    else:
        form = UserCreationForm()
    return render(request, 'chat/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            next_url = request.GET.get('next', 'chat_home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')

    return render(request, "login.html")


@login_required
def chat_home(request, user_id=None):
    current_user = request.user
    messages = []
    selected_user = None

    if user_id:
        selected_user = get_object_or_404(User, id=user_id)
        # Fetch messages between the current user and the selected user
        messages = Message.objects.filter(
            sender__in=[current_user, selected_user],
            receiver__in=[current_user, selected_user]
        ).order_by('timestamp')

    users = User.objects.exclude(id=current_user.id)

    context = {
        "users": users,
        "messages": messages,
        "selected_user": selected_user,
    }
    return render(request, "chat/chat_home.html", context)

def logout_view(request):
    logout(request)
    return redirect('login')

def get_chat(request, user_id):
    current_user = request.user
    selected_user = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(
        sender__in=[current_user, selected_user],
        receiver__in=[current_user, selected_user]
    ).order_by('timestamp')

    # Prepare messages in JSON format
    message_data = [
        {"sender": message.sender.username, "content": message.content}
        for message in messages
    ]

    return JsonResponse({
        "messages": message_data,
        "selected_user": selected_user.username,
    })