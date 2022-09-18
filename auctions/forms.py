from django import forms


class ImageUploadForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()


class ImageUploadForm1(forms.Form):
    image_main = forms.ImageField()


class ImageUploadForm2(forms.Form):
    image_1 = forms.ImageField()


class ImageUploadForm3(forms.Form):
    image_2 = forms.ImageField()


class ImageUploadForm4(forms.Form):
    image_3 = forms.ImageField()
