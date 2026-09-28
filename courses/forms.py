from django import forms

from accounts.models import User
from .models import Discipline
FORM_INPUT_CLASS = (
    "w-full border border-gray-300 bg-white px-4 py-3 "
    "text-sm outline-none focus:border-black"
)

class DisciplineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = FORM_INPUT_CLASS
            
    class Meta:
        model = Discipline
        fields = [
            "name",
            "description",
            "teachers",
            "students",
        ]

        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 5,
            }),
            "teachers": forms.SelectMultiple(attrs={
                "size": 6,
            }),
            "students": forms.SelectMultiple(attrs={
                "size": 10,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["teachers"].queryset = User.objects.filter(
            role=User.Role.TEACHER
        ).order_by("first_name", "last_name", "username")

        self.fields["students"].queryset = User.objects.filter(
            role=User.Role.STUDENT
        ).order_by("first_name", "last_name", "username")


class TeacherDisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        fields = [
            "name",
            "description",
            "students",
        ]

        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 5,
            }),
            "students": forms.SelectMultiple(attrs={
                "size": 10,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["students"].queryset = User.objects.filter(
            role=User.Role.STUDENT
        ).order_by("first_name", "last_name", "username")