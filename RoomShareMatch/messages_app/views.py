from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Chat, Message
from main_app.models import UserProfile
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse


def create_or_get_chat(user1, user2):
    """
    ユーザー1とユーザー2のチャットオブジェクトを作成または取得します。
    
    :param user1: Userオブジェクト
    :param user2: Userオブジェクト
    :return: Chatオブジェクト
    """
    is_chat = Chat.objects.filter(participants=user1).filter(participants=user2).exists()
    if is_chat:
        chat = Chat.objects.filter(participants=user1).filter(participants=user2).first()
    else:
        chat = Chat.objects.create()
        chat.participants.set([user1, user2])
        chat.save()
    return chat


@login_required
def view_chat(request, receiver_id):
    """
    ユーザーが指定したチャット相手とのチャット画面を表示します。
    
    :param request: HttpRequestオブジェクト
    :param receiver_id: 整数（受信者のユーザーID）
    :return: HttpResponseオブジェクト
    """
    receiver = get_object_or_404(User, pk=receiver_id)
    if receiver:
        # chat,messages取得
        chat = create_or_get_chat(request.user, receiver)
        messages = Message.objects.filter(chat=chat).order_by('timestamp')
        
        # 相手のメッセージを既読にする
        Message.objects.filter(chat=chat, sender=receiver).update(is_read=True)
        
        receiver_profile_image = UserProfile.objects.get(user=receiver).profile_image.url
        
        content = {
            'chat_id': chat.id,
            'messages': messages,
            'receiver': receiver,
            'receiver_profile_image': receiver_profile_image
        }
        return render(request, 'messages_app/chat_view.html', content)



def send_message(sender, chat, content, image=None):
    """
    送信者からチャットにメッセージを送信します。
    
    :param sender: Userオブジェクト（メッセージの送信者）
    :param chat: Chatオブジェクト
    :param content: 文字列（メッセージの内容）
    :param image: Fileオブジェクト（アップロードされた画像ファイル、任意）
    :return: Messageオブジェクト
    """
    message = Message(sender=sender, chat=chat, content=content, image=image)
    message.save()
    return message


@login_required
@require_POST
def send_message_view(request, receiver_id, chat_id):
    """
    ユーザーが指定したチャット相手にメッセージを送信します。
    
    :param request: HttpRequestオブジェクト
    :param receiver_id: 整数（受信者のユーザーID）
    :return: HttpResponseRedirectオブジェクト
    """
    receiver = get_object_or_404(User, pk=receiver_id)
    chat = get_object_or_404(Chat, pk=chat_id)
    if receiver and chat:
        content = request.POST['content']
        image = request.FILES.get('image', None)
        send_message(request.user, chat, content, image)
        # Message.objects.create(sender=request.user, chat=chat, content=content)
        messages = Message.objects.filter(chat=chat).order_by('timestamp')
        content = {
            'chat_id': chat.id,
            'receiver': receiver,
            'messages': messages,            
        }
        return HttpResponseRedirect(reverse('messages_app:view_chat', args=[receiver_id]))  



@login_required
def message_list(request):
    user = request.user
    chats = Chat.objects.filter(participants=user)
    
    chat_data = []
    for chat in chats:
        last_message = Message.objects.filter(chat=chat).order_by('-timestamp').first()
        chat_partner = next(participant for participant in chat.participants.all() if participant != user)
        chat_partner_user_name = UserProfile.objects.get(user=chat_partner).user_name
        print(chat_partner_user_name)
        chat_partner_profile_image = UserProfile.objects.get(user=chat_partner).profile_image.url
        chat_data.append({
            'id': chat.id,
            'partner': chat_partner,
            'partner_user_name': chat_partner_user_name,
            'last_message': last_message,
            'timestamp': last_message.timestamp if last_message else None,
            'partner_profile_image': chat_partner_profile_image
        })
    
    context = {'chats': chat_data}
    return render(request, 'messages_app/message_list.html', context)
