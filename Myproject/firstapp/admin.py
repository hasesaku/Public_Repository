from django.contrib import admin
from .models import User, Chat, Like  # モデルのインポート

# Userモデルの管理用クラス
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'nickname', 'is_active', 'is_staff', 'created_at', 'updated_at')  # 管理画面のリストに表示するフィールド
    search_fields = ('email', 'username')  # 検索フィールド

# Chatモデルの管理用クラス
class ChatAdmin(admin.ModelAdmin):
    list_display = ('chat_room', 'user', 'post', 'edit', 'created_at', 'updated_at')
    list_filter = ('edit', 'created_at')  # フィルタリングに使用するフィールド
    search_fields = ('chat_room', 'post')

# Likeモデルの管理用クラス
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat', 'created_at', 'updated_at')
    search_fields = ('user__email', 'chat__chat_room')  # ForeignKeyのフィールドを検索する場合の記法

# モデルを管理サイトに登録
admin.site.register(User, UserAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(Like, LikeAdmin)
