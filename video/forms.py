from django.forms import ModelForm, ValidationError
from .models import Video, Comment
from django import forms


class CreateVideoForm(ModelForm):
    class Meta:
        model = Video
        exclude = ('user', 'created_at', 'updated_at', 'slug')


    def clean(self):
        slug = self.cleaned_data.get('title').lower().replace(" ", '-')
        if Video.objects.filter(slug=slug).exists():
            raise ValidationError('Slug with such name already exists!')
        return self.cleaned_data


class UpdateVideoForm(ModelForm):
    class Meta:
        model = Video
        exclude = ('user', 'created_at', 'updated_at', 'slug')


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)