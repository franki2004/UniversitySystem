
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


FORM_INPUT_CLASS = (
    "w-full border border-solid border-gray-300 bg-white px-4 py-3 "
    "text-sm text-gray-900 outline-none "
    "focus:border-black focus:ring-1 focus:ring-black"
)


def style_form_fields(form):
    for field in form.fields.values():
        widget = field.widget

        if isinstance(widget, forms.CheckboxInput):
            widget.attrs["class"] = (
                "h-4 w-4 cursor-pointer border border-gray-300 "
                "accent-black"
            )
        else:
            widget.attrs["class"] = FORM_INPUT_CLASS


class UserCreateForm(forms.ModelForm):
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
            "faculty_number",
            "email",
            "role",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)

    def clean_faculty_number(self):
        value = self.cleaned_data.get("faculty_number")

        if not value or not value.strip():
            return None

        value = value.strip()

        if User.objects.filter(faculty_number=value).exists():
            raise forms.ValidationError(
                "Потребител с този факултетен номер вече съществува."
            )

        return value

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                self.add_error(
                    "password_confirm",
                    "Паролите не съвпадат.",
                )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            self.save_m2m()

        return user


class UserUpdateForm(forms.ModelForm):
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
            "faculty_number",
            "email",
            "role",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)

    def clean_faculty_number(self):
        value = self.cleaned_data.get("faculty_number")

        if not value or not value.strip():
            return None

        value = value.strip()

        if User.objects.filter(
            faculty_number=value
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "Този факултетен номер вече се използва."
            )

        return value

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password or password_confirm:
            if not password:
                self.add_error(
                    "password",
                    "Въведете нова парола.",
                )
            elif not password_confirm:
                self.add_error(
                    "password_confirm",
                    "Потвърдете новата парола.",
                )
            elif password != password_confirm:
                self.add_error(
                    "password_confirm",
                    "Паролите не съвпадат.",
                )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get("password")

        if password:
            user.set_password(password)

        if commit:
            user.save()
            self.save_m2m()

        return user
