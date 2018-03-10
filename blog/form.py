from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from collections import OrderedDict

from .models import Category, Topic, Post


class NewCategoryForm(forms.ModelForm):
    name = forms.CharField(label="Category:")
    description = forms.CharField(label="Description:")

    class Meta:
        model = Category
        fields = ['name', 'description', 'image', ]


class EditCategory(NewCategoryForm):
    class Meta(NewCategoryForm.Meta):
        fields = ['name', 'description', ]


class NewTopicForm(forms.ModelForm):
    subject = forms.CharField(label="Topic:")
    message = forms.CharField(label="Message:",
                              widget=forms.Textarea(attrs={'width': "100%", 'cols': 10, 'rows': 8}),
                              max_length=4000)

    class Meta:
        model = Topic
        fields = ['subject', 'message', ]


class EditTopicForm(forms.ModelForm):
    subject = forms.CharField(label="Topic:")

    class Meta:
        model = Topic
        fields = ['subject', ]


class PostForm(forms.ModelForm):
    created_by = forms.CharField(label="Username", required=False)
    email = forms.EmailField(label="Email", required=False)
    site = forms.CharField(label="Site", required=False)
    message = forms.CharField(label="Message:",
                              widget=forms.Textarea(attrs={'width': "100%", 'cols': 10, 'rows': 8}),
                              max_length=4000)

    class Meta:
        model = Post
        fields = ['email', 'site', 'message', ]

    def clean_created_by(self):
        created_by = self.cleaned_data['created_by'].strip()
        q = User.objects.filter(username=created_by)
        if q.count():
            raise ValidationError(_("You can't use this username"), code='invalid')
        elif not created_by:
            guest = User.objects.get(username="Guest")
            created_by = guest
        return created_by


# Order PostForm's fields
PostForm.base_fields = OrderedDict(
    (k, PostForm.base_fields[k])
    for k in ['created_by', 'email', 'site', 'message']
)
