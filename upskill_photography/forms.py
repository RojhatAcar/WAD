from django import forms
from upskill_photography.models import Picture, UserProfile


class PictureUploadForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ('title', 'image', 'category')


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)
