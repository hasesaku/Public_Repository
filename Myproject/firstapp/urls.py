from django.urls import path
from . import views

app_name = 'firstapp'

urlpatterns = [
    # トップ画面へのURL
    path('', views.index, name='index'),
    # 新規ユーザー登録画面へのURL
    path('register/', views.register, name='register'),
    # ログイン画面へのURL
    path('login/', views.user_login, name='login'),
    # ホーム画面へのURLを追加
    path('home/', views.home, name='home'),
    # マイページへのURL
    path('profile/', views.profile, name='profile'),
    #マイページ編集画面へのURL
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    # ユーザー(アカウント)削除機能へのURL
    path('delete_user/', views.delete_user, name='delete_user'),
    #チャットルーム一覧画面へのURL
    path('chatrooms/', views.chatrooms, name='chatrooms'),
    # ログアウト画面へのURLを追加
    path('logout/', views.user_logout, name='logout'),
    #チャット投稿画面へのURLを追加
    path('chat_post/<str:chat_room>/', views.chat_post, name='chat_post'),
    #チャット投稿を編集するためのURLを追加
    path('edit_chat_post/<int:chat_id>/', views.edit_chat_post, name='edit_chat_post'),
    # チャット投稿を削除するためのURLを追加
    path('delete_chat_post/<int:chat_id>/', views.delete_chat_post, name='delete_chat_post'),
    # いいね機能へのURLを追加
    path('like_chat/<int:chat_id>/', views.like_chat, name='like_chat'),
    # 新しいチャットルーム作成URLの追加
    path('new_chatroom/', views.create_chat_room, name='new_chatroom'),
    # その他のURLパターン...
]