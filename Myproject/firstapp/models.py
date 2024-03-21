from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# ユーザー管理クラス
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        通常のユーザーを作成するメソッド
        """
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        スーパーユーザーを作成するメソッド
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# ユーザーモデル
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('メールアドレス', max_length=255, unique=True)
    username = models.CharField('ユーザー名', max_length=255)
    nickname = models.CharField('ニックネーム', max_length=255, null=True, blank=True)
    is_active = models.BooleanField('アクティブ', default=True)
    is_staff = models.BooleanField('スタッフ', default=True)
    # 日時フィールドは自動で現在時刻を設定
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('最終更新日時', auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# チャットルームモデルを追加
class ChatRoom(models.Model):
    name = models.CharField('チャットルーム名', max_length=255, unique=True)  # 各チャットルームは一意の名前を持つ
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    def __str__(self):
        return self.name

# Chatモデルの追加
class Chat(models.Model):
    user_id = models.IntegerField('ユーザーID')
    chat_room_id = models.IntegerField('チャットルームID')  # chat_roomはChatRoomモデルを参照するように変更    
    submission = models.TextField('メッセージ')  # 投稿メッセージを保存するためのフィールドを追加
    created_at = models.DateTimeField('投稿日時', auto_now_add=True)
    updated_at = models.DateTimeField('最終更新日時', auto_now=True)

    def __str__(self):
        return f"Chat in {self.chat_room_id}"    

# Likeモデルの追加
class Like(models.Model):
    # Userモデルへの参照
    user_id = models.IntegerField('ユーザーID')
    # Chatモデルへの参照
    chat_id = models.IntegerField('チャットID')
    # 登録日時
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    # 最終更新日時
    updated_at = models.DateTimeField('最終更新日時', auto_now=True)

    def __str__(self):
        return f"Like on Chat {self.chat_id}"
        
# 記事モデル
class Article(models.Model):
    title = models.CharField('タイトル', max_length=255)
    text = models.TextField('本文')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    update_at = models.DateTimeField('更新日時', auto_now=True)

    def __str__(self):
        return self.title