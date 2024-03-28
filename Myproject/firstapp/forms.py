from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth import get_user_model, authenticate
from .models import Chat, ChatRoom
from django.core.exceptions import ValidationError

User = get_user_model()

class UserCreationForm(BaseUserCreationForm):
    email = forms.EmailField(required=True, label="メールアドレス",
                             error_messages={'invalid': 'メールアドレスの形式で入力してください。例: user@example.com'})
    nickname = forms.CharField(required=True, label="ニックネーム")
    # ユーザーネームフィールドを追加
    username = forms.CharField(required=True, label="ユーザーネーム")
    class Meta:
        model = User
        fields = ('email', 'username', 'nickname', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "パスワードが一致しません。")
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

class LoginForm(forms.Form):
    email = forms.EmailField(label="メールアドレス",
                             error_messages={'invalid': 'メールアドレスの形式で入力してください。例: user@example.com'})
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput())

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("メールアドレスを入力してください。")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("パスワードを入力してください。")
        return password

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise ValidationError("メールアドレスかパスワードが間違っています。")

        return cleaned_data
            
class UserEditForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '現在のパスワード'}), required=False, label='現在のパスワード')
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '新しいパスワード'}), required=False, label='新しいパスワード')
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '新しいパスワード（確認）'}), required=False, label='新しいパスワード（確認）')

    class Meta:
        model = User
        fields = ('email', 'username', 'nickname')  # 編集可能なフィールドを指定

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'placeholder': 'メールアドレス'})
        self.fields['username'].widget.attrs.update({'placeholder': 'ユーザー名'})
        self.fields['nickname'].widget.attrs.update({'placeholder': 'ニックネーム'})

    def clean_current_password(self):
        current_password = self.cleaned_data.get("current_password")
        if current_password and not self.instance.check_password(current_password):
            # ここでのエラー追加はやめて、cleanメソッドに任せる。
            pass  
        return current_password
        
    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        
        # 新しいパスワードとパスワード確認が両方とも空でない場合にチェックする
        if new_password or confirm_password:
            if new_password != confirm_password:
                self.add_error('confirm_password', '新しいパスワードが一致しません。')
            if not self.instance.check_password(current_password):
                self.add_error('current_password', '現在のパスワードが正しくありません。')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user

class ChatPostForm(forms.ModelForm):
    # フォームにchat_roomフィールドを追加するための隠しフィールドを追加
    chat_room = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        model = Chat
        fields = ['submission']
        widgets = {
            'submission': forms.TextInput(attrs={'placeholder': 'メッセージを入力', 'maxlength': '120'}),  # placeholderとmaxlengthを追加
        }

class ChatRoomJoinForm(forms.Form):
    chat_room = forms.CharField(
        max_length=255, 
        label='チャットルームID',
        widget=forms.TextInput(attrs={'placeholder': 'チャットルームIDを入力', 'class': 'form-control'})
    )   

# チャットルーム作成フォームを更新
class ChatRoomCreationForm(forms.ModelForm):
    class Meta:
        model = ChatRoom  
        fields = ['name']
         # labels ディクショナリを追加してフィールドのラベルを指定
        labels = {
            'name': 'チャットルームID',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'お好きな数字を入力してください', 'class': 'form-control', 'autocomplete': 'off'}),
        }
    def clean_name(self):
        name = self.cleaned_data['name']
        # チャットルーム名が数字のみで構成されているかチェック
        if not name.isdigit():
            raise ValidationError("チャットルームIDは数字のみ作成してください。")
        # チャットルーム名が既に存在するかどうかをチェック
        if ChatRoom.objects.filter(name=name).exists():
            raise ValidationError("このチャットルームIDは既に存在します。")
        return name

