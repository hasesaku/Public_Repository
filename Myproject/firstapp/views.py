from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .forms import UserCreationForm, LoginForm, UserEditForm, ChatPostForm, ChatRoomJoinForm, ChatRoomCreationForm
from .models import Chat, Like, User, Article, ChatRoom
from django.urls import reverse

from django.http import JsonResponse

# トップ画面のビュー関数を追加
def index(request):
    if request.user.is_authenticated:
        return redirect('firstapp:home')  # ホーム画面へリダイレクト
    else:
        return render(request, 'firstapp/index.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # login(request, user)# この行を削除
            return redirect('firstapp:home')  # ホーム画面へリダイレクトするためのURL名
        else:
            # フォームが無効な場合、エラーメッセージと共に同じページを表示
            return render(request, 'firstapp/register.html', {'form': form})
    else:
        form = UserCreationForm()
    return render(request, 'firstapp/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('firstapp:home')  # ホーム画面へリダイレクトするためのURL名
        else:
            # フォームが無効な場合は、フォームを再度表示しエラーメッセージを含める
            return render(request, 'firstapp/login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'firstapp/login.html', {'form': form})

# ログアウトのビュー関数を追加
@login_required
def user_logout(request):
    logout(request)
    return redirect('firstapp:index')  # ログアウト後はトップページにリダイレクト

# ホーム画面のビュー関数を追加
@login_required  # ログインしているユーザーのみアクセス可能にします
def home(request):
    return render(request, 'firstapp/home.html')  # ホーム画面のテンプレートを表示

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            # パスワードが変更された場合、ユーザーを再認証する
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                user = authenticate(email=user.email, password=new_password)
                if user:
                    login(request, user)
            return redirect('firstapp:profile')  # 更新後はプロフィールにリダイレクト
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'firstapp/profile.html', {'form': form})

# ユーザーアカウント削除機能
@login_required
def delete_user(request):
    user = request.user
    user.delete()
    logout(request) # ユーザーをログアウトさせる
    return redirect('firstapp:index')  # アカウント削除後はトップページにリダイレクト

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            # '現在のパスワード'があるかを確認し、あればインスタンスを保存
            if form.cleaned_data.get('current_password'):
                user = form.save(commit=False)
                new_password = form.cleaned_data.get('new_password')
                # パスワードフィールドが空でないことを確認する
                if new_password:
                    user.set_password(new_password)
                user.save()
                # 新しいパスワードでユーザーを再認証する
                if new_password:
                    user = authenticate(email=user.email, password=new_password)
                    if user:
                        login(request, user)
                return redirect('firstapp:profile')  # 更新後はプロフィールにリダイレクト
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'firstapp/edit_profile.html', {'form': form})           

@login_required
def chatrooms(request):
    join_form = ChatRoomJoinForm()  # チャットルーム参加フォームのインスタンスを作成
    chat_rooms = ChatRoom.objects.all()  # ChatRoomモデルからチャットルームのリストを取得
    # chat_rooms = Chat.objects.values_list('chat_room_id', flat=True).distinct()

    if request.method == 'POST':
        join_form = ChatRoomJoinForm(request.POST)
        if join_form.is_valid():
            chat_room_name = join_form.cleaned_data['chat_room']
            # チャットルーム名が存在するかどうかをチェック
            if ChatRoom.objects.filter(name=chat_room_name).exists():
                # チャットルーム名で取得し、IDを渡すように修正
                chat_room = ChatRoom.objects.get(name=chat_room_name)
                # 存在する場合は、チャット投稿ビューにリダイレクト
                return redirect(reverse('firstapp:chat_post', kwargs={'chat_room': chat_room}))
            else:
                # 存在しない場合は、エラーメッセージをフォームに追加
                join_form.add_error('chat_room', '指定されたチャットルームは存在しません。')

    return render(request, 'firstapp/chatrooms.html', {'chat_rooms': chat_rooms, 'join_form': join_form})

# 新しいチャットルームを作成するビュー
@login_required
def create_chat_room(request):
    form = ChatRoomCreationForm()
    if request.method == 'POST':
        form = ChatRoomCreationForm(request.POST)
        if form.is_valid():
            form.save()  # new_chat_room変数を削除して、form.save()を直接使用
            # 作成後にチャットルーム参加画面にリダイレクト
            return redirect('firstapp:chatrooms')
    return render(request, 'firstapp/new_chatroom.html', {'form': form})

@login_required
def chat_post(request, chat_room):
    if request.method == 'POST':
        form = ChatPostForm(request.POST)
        if form.is_valid():
            chat_post = form.save(commit=False)
            chat_post.user_id = request.user.id  # ユーザーIDをChatインスタンスのuser_idフィールドに設定
            chat_post.chat_room_id = chat_room  # チャットルームIDも適切に設定
            chat_post.save()
            return redirect(reverse('firstapp:chat_post', kwargs={'chat_room': chat_room}))
    else:
        form = ChatPostForm(initial={'chat_room': chat_room})
    # チャットを作成日時順に取得してテンプレートに渡す
    chats = Chat.objects.filter(chat_room_id=chat_room).order_by('created_at')
    # チャットごとにユーザー情報を取得
    chats_with_user_info = []
    for chat in chats:
        # user_idを使ってUserオブジェクトを取得
        user = User.objects.get(id=chat.user_id)
        # いいねの数を取得
        likes_count = Like.objects.filter(chat_id=chat.id).count()
        # このユーザーがいいねしているかどうか
        user_liked = Like.objects.filter(chat_id=chat.id, user_id=request.user.id).exists()
        # チャット情報とユーザー情報を組み合わせた辞書を作成
        chat_info = {
            'id': chat.id,
            'submission': chat.submission,
            'created_at': chat.created_at,
            'nickname': user.nickname,  # ニックネームを辞書に追加
            'user_id': chat.user_id,
            'likes_count': likes_count,  # いいねの数を辞書に追加
            'user_liked': user_liked,  # いいねしている状態を辞書に追加
        }
        chats_with_user_info.append(chat_info)

    return render(request, 'firstapp/chat_post.html', {
        'form': form,
        'chats': chats_with_user_info,  # 変更: chats_with_user_infoをテンプレートに渡す
        'room_name': chat_room  # チャットルーム名をテンプレートに渡す
    })

@login_required
def edit_chat_post(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user_id=request.user.id)  # 編集権限の確認
    if request.method == 'POST':
        form = ChatPostForm(request.POST, instance=chat)
        if form.is_valid():
            form.save()
            return redirect(reverse('firstapp:chat_post', kwargs={'chat_room': chat.chat_room_id}))
    else:
        form = ChatPostForm(instance=chat, initial={'chat_room': chat.chat_room_id})
    return render(request, 'firstapp/edit_chat_post.html', {'form': form, 'chat': chat})

@login_required
def delete_chat_post(request, chat_id):
    chat_post = get_object_or_404(Chat, id=chat_id, user_id=request.user.id)  # 投稿が存在し、リクエストユーザーが投稿者であることを確認
    chat_room_id = chat_post.chat_room_id  # chat_room_id を取得
    user = get_object_or_404(User, id=chat_post.user_id)  # user_idからUserオブジェクトを取得
    nickname = user.nickname

    if request.method == 'POST':
        chat_post.delete()
        return redirect('firstapp:chat_post', chat_room=chat_room_id)  # 削除後はチャット投稿画面にリダイレクト
    else:
        # GETリクエスト時は確認画面を表示
        return render(request, 'firstapp/delete_post.html', {
            'chat': chat_post,
            'nickname': nickname,  # ニックネームをテンプレートに渡す
            'chat_room_id': chat_room_id  # chat_room_id をテンプレートに渡す
        })

@login_required
def like_chat(request, chat_id):
    if request.method == 'POST':
        user_id = request.user.id
        # いいねが存在するか確認
        like = Like.objects.filter(user_id=user_id, chat_id=chat_id).first()

        if like:
            # 既にいいねが存在する場合は削除
            like.delete()
            liked = False
        else:
            # いいねが存在しない場合は作成
            Like.objects.create(user_id=user_id, chat_id=chat_id)
            liked = True

        likes_count = Like.objects.filter(chat_id=chat_id).count()
        return JsonResponse({'liked': liked, 'likes_count': likes_count})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
@login_required
def article_list(request):
    articles = Article.objects.all().order_by('-created_at')  # 作成日時の降順で記事を取得
    return render(request, 'firstapp/article_list.html', {'articles': articles})