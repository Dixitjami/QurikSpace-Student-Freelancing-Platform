from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .forms import MessageForm

User = get_user_model()


@login_required
def start_conversation(request, freelancer_id):
    freelancer = get_object_or_404(User, id=freelancer_id, user_type='student')

    if request.user.user_type != 'client':
        return HttpResponseForbidden("Only clients can start conversation.")

    conversation, created = Conversation.objects.get_or_create(
        client=request.user,
        freelancer=freelancer
    )

    return redirect('chat_view', conversation_id=conversation.id)


@login_required
def chat_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Permission check
    if request.user != conversation.client and request.user != conversation.freelancer:
        return HttpResponseForbidden("Not allowed.")

    messages = conversation.messages.all().order_by('timestamp')

    # 🟢 STEP 3 — Mark messages as seen
    messages.filter(is_seen=False).exclude(sender=request.user).update(is_seen=True)


    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return redirect('chat_view', conversation_id=conversation.id)
    else:
        form = MessageForm()

    return render(request, 'messaging/chat.html', {
        'conversation': conversation,
        'messages': messages,
        'form': form
    })


@login_required

def my_conversations(request, conversation_id=None):

    if request.user.user_type == 'client':
        conversations = request.user.client_conversations.all()
    else:
        conversations = request.user.freelancer_conversations.all()

    active_conversation = None
    messages = None
    form = MessageForm()

    if conversation_id:
        active_conversation = get_object_or_404(
            Conversation,
            id=conversation_id
        )

        if request.user != active_conversation.client and request.user != active_conversation.freelancer:
            return HttpResponseForbidden("Not allowed.")

        messages = active_conversation.messages.all().order_by('timestamp')
        messages.filter(is_seen=False).exclude(sender=request.user).update(is_seen=True)

        if request.method == 'POST':
            form = MessageForm(request.POST, request.FILES)
            if form.is_valid():
                message = form.save(commit=False)
                message.conversation = active_conversation
                message.sender = request.user
                message.save()
                return redirect('chat_view', conversation_id=active_conversation.id)

    return render(request, 'messaging/messages.html', {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'messages': messages,
        'form': form
    })
