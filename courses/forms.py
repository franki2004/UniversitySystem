from django import forms
from django.contrib.auth import get_user_model

from .models import Discipline


User = get_user_model()


INPUT_CLASSES = (
    "block w-full border border-gray-300 bg-white px-3 py-2 "
    "text-sm text-gray-900 shadow-sm "
    "focus:border-black focus:outline-none focus:ring-2 "
    "focus:ring-gray-300"
)

TEXTAREA_CLASSES = (
    INPUT_CLASSES
    + " min-h-32 resize-y"
)

MULTISELECT_CLASSES = (
    INPUT_CLASSES
    + " min-h-48"
)


class PersonMultipleChoiceField(forms.ModelMultipleChoiceField):
    """Показва името на потребителя вместо username."""

    def label_from_instance(self, obj):
        return obj.get_full_name().strip() or obj.username


class StudentMultipleChoiceField(PersonMultipleChoiceField):
    """Показва студентите като Име Фамилия - факултетен номер."""

    def label_from_instance(self, obj):
        full_name = obj.get_full_name().strip() or obj.username
        faculty_number = obj.faculty_number or "без факултетен номер"

        return f"{full_name} - {faculty_number}"


def style_form_fields(form):
    """Добавя еднакъв и видим стил към полетата."""

    for field in form.fields.values():
        widget = field.widget

        if isinstance(widget, forms.CheckboxInput):
            widget.attrs["class"] = (
                "h-4 w-4 border border-gray-400 "
                "accent-black focus:ring-black"
            )

        elif isinstance(widget, forms.SelectMultiple):
            widget.attrs["class"] = MULTISELECT_CLASSES
            widget.attrs.setdefault("size", 8)

        elif isinstance(widget, forms.Textarea):
            widget.attrs["class"] = TEXTAREA_CLASSES

        else:
            widget.attrs["class"] = INPUT_CLASSES


class DisciplineForm(forms.ModelForm):
    teachers = PersonMultipleChoiceField(
        queryset=User.objects.none(),
        label="Преподаватели",
        required=False,
        help_text="Можеш да избереш повече от един преподавател.",
        widget=forms.SelectMultiple(attrs={"size": 6}),
    )

    students = StudentMultipleChoiceField(
        queryset=User.objects.none(),
        label="Студенти",
        required=False,
        help_text=(
            "Избери студенти. Всеки се показва като "
            "Име Фамилия - факултетен номер."
        ),
        widget=forms.SelectMultiple(attrs={"size": 8}),
    )

    class Meta:
        model = Discipline
        fields = [
            "name",
            "description",
            "teachers",
            "students",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Например: Бази данни",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Описание на дисциплината...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].label = "Име на дисциплината"
        self.fields["description"].label = "Описание"

        self.fields["teachers"].queryset = User.objects.filter(
            role=User.Role.TEACHER
        ).order_by("last_name", "first_name", "username")

        self.fields["students"].queryset = User.objects.filter(
            role=User.Role.STUDENT
        ).order_by(
            "last_name",
            "first_name",
            "faculty_number",
            "username",
        )

        style_form_fields(self)


class TeacherDisciplineForm(forms.ModelForm):
    """Форма, с която преподавателят редактира само основните данни."""

    class Meta:
        model = Discipline
        fields = [
            "name",
            "description",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Име на дисциплината",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Описание на дисциплината...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].label = "Име на дисциплината"
        self.fields["description"].label = "Описание"

        style_form_fields(self)


class AddStudentsForm(forms.Form):
    students = StudentMultipleChoiceField(
        queryset=User.objects.none(),
        label="Избери студенти",
        required=True,
        help_text=(
            "Можеш да избереш повече от един студент. "
            "Вече записаните студенти няма да се показват."
        ),
        widget=forms.SelectMultiple(attrs={"size": 8}),
    )

    def __init__(self, *args, discipline=None, **kwargs):
        super().__init__(*args, **kwargs)

        queryset = User.objects.filter(
            role=User.Role.STUDENT
        ).order_by(
            "last_name",
            "first_name",
            "faculty_number",
            "username",
        )

        if discipline is not None:
            enrolled_student_ids = discipline.students.values_list(
                "pk",
                flat=True,
            )
            queryset = queryset.exclude(
                pk__in=enrolled_student_ids
            )

        self.fields["students"].queryset = queryset

        style_form_fields(self)