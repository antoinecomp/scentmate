from django.forms import ModelForm, Form
from .models import Todo
from .models import Keyword


class TodoForm(ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'memo', 'important']


class QuizForm(Form):
    class Meta:
        model = Keyword
        fields = ['title', 'image']
