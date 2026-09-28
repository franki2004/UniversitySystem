from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()
FORM_INPUT_CLASS = (
    "w-full border border-gray-300 bg-white px-4 py-3 "
    "text-sm outline-none focus:border-black"
)
def style_form_fields(form):
    css_class = (
        "w-full border border-gray-300 bg-white px-4 py-3 "
        "text-sm outline-none focus:border-black"
    )

    for field in form.fields.values():
        field.widget.attrs["class"] = css_class

class UserCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)

    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        label="Парола",
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Потвърди паролата",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
        ]

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Паролите не съвпадат.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class UserUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)
            
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        min_length=8,
        label="Нова парола",
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Потвърди новата парола",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
        ]

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Паролите не съвпадат.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get("password")

        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user