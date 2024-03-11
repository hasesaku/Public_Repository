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
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    # 日時フィールドは自動で現在時刻を設定
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# チャットルームモデルを追加
class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)  # 各チャットルームは一意の名前を持つ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Chatモデルの追加
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='chats')  # chat_roomはChatRoomモデルを参照するように変更    
    chat_search = models.TextField()  # チャット検索用フィールド
    post = models.TextField()  # 投稿メッセージを保存するためのフィールドを追加
    edit = models.BooleanField(default=False)  # 投稿が編集されたかどうかを示すフィールドを追加
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat {self.id} in {self.chat_room.name}"    

# Likeモデルの追加
class Like(models.Model):
    # Userモデルへの参照
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    # Chatモデルへの参照
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='likes')
    # 登録日時
    created_at = models.DateTimeField(auto_now_add=True)
    # 最終更新日時
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Like by {self.user.email} on Chat {self.chat.id}"