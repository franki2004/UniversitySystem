from django import forms

from .models import Assignment, Submission

FORM_INPUT_CLASS = (
    "w-full border border-gray-300 bg-white px-4 py-3 "
    "text-sm outline-none focus:border-black"
)

class AssignmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = FORM_INPUT_CLASS
            
    class Meta:
        model = Assignment
        fields = [
            "title",
            "description",
            "deadline",
            "attachment",
        ]

        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 6,
            }),
            "deadline": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["deadline"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["file"]


class GradeForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = [
            "grade",
            "feedback",
        ]

        widgets = {
            "feedback": forms.Textarea(attrs={
                "rows": 6,
            }),
        }