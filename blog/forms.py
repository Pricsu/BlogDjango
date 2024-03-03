from django import forms
from .models import PostComments


class PostCommentsForm(forms.ModelForm):
    class Meta:
        model = PostComments
        fields = ['content']


class PostSearchForm(forms.Form):
    searched = forms.CharField(label='Search', max_length=100)