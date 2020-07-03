from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {
            'group': _('Сообщество'),
            'text': _('Текст поста'),
            'image': _('Изображение')
        }
        help_texts = {
            'group': _('Выберите сообщество из списка'),
            'text': _('Введите текст поста'),
            'image': _('Добавьте изображение (необязательно)')
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text', ]
        labels = {
            'text': _('Текст комментария')
        }
        help_texts = {
            'text': _('Введите текст комментария')
        }
