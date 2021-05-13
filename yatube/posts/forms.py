from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': 'Текст публикации',
            'group': 'Сообщество', }
        help_texts = {
            'text': 'Введите текст',
            'group': 'Выберите сообщество (необязательно)', }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Текст комментария'
        }
        help_texts = {
            'text': 'Введите текст'
        }
