from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'avatar', 'phone', 'role', 'section', 'description']

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'avatar', 'phone', 'role', 'description']
