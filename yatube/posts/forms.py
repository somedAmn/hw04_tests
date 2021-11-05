from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа'
        }
        help_texts = {
            'text': 'Текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
