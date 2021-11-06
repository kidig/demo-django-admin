from django import forms

from content.models import Blog


class BlogAdminForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].required = False