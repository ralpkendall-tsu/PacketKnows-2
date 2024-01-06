from django import forms
from .models import CustomUser, UserCategory
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class CustomUserForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control border-2 border-bottom fs-5',
        'placeholder': 'Password',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control border-2 border-bottom fs-5',
        'placeholder': 'Repeat Password',
    }))

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control border-2 border-bottom fs-5',
        'placeholder': 'Email',
    }))

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control border-2 border-bottom fs-5',
        'placeholder': 'First Name',
    }))

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control border-2 border-bottom fs-5',
        'placeholder': 'Last Name',
    }))

    school_id_instructor = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control border-2 border-bottom fs-5',
        'placeholder': 'Instructor School ID',
    }))

    school_id_student = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control border-2 border-bottom fs-5',
        'placeholder': 'Student School ID',
    }))

    evidences_instructor = forms.FileField(required=False,widget=forms.FileInput(attrs={
        'class': 'form-control border-2 border-bottom',
        'placeholder': 'Evidences',
    }))

    evidences_selfLearner = forms.FileField(required=False,widget=forms.FileInput(attrs={
        'class': 'form-control border-2 border-bottom',
        'placeholder': 'Evidences',
    }))

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2', 'first_name', 'last_name', 'school_id', 'evidences']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def clean_school_id_instructor(self):
        school_id_instructor = self.cleaned_data.get('school_id_instructor')
        if school_id_instructor and CustomUser.objects.filter(school_id=school_id_instructor).exists():
            raise forms.ValidationError('This school ID is already in use.')
        return school_id_instructor

    def clean_school_id_student(self):
        school_id_student = self.cleaned_data.get('school_id_student')
        if school_id_student and CustomUser.objects.filter(school_id=school_id_student).exists():
            raise forms.ValidationError('This school ID is already in use.')
        return school_id_student

    def clean_evidences_instructor(self):
        evidences_instructor = self.cleaned_data.get('evidences_instructor')
        category = self.cleaned_data.get('category')

        if category and category.name.lower() == 'instructor' and not evidences_instructor:
            raise forms.ValidationError('This field is required for self-learners and instructors.')

        return evidences_instructor
    
    def clean_evidences_selfLearner(self):
        evidences_selfLearner = self.cleaned_data.get('evidences_selfLearner')
        category = self.cleaned_data.get('category')

        if category and category.name.lower() == 'selfLearner' and not evidences_selfLearner:
            raise forms.ValidationError('This field is required for self-learners and instructors.')

        return evidences_selfLearner

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.cleaned_data['school_id_instructor']:
            instance.school_id = self.cleaned_data['school_id_instructor']
        elif self.cleaned_data['school_id_student']:
            instance.school_id = self.cleaned_data['school_id_student']

        if self.cleaned_data['evidences_instructor']:
            instance.evidences = self.cleaned_data['evidences_instructor']
        elif self.cleaned_data['evidences_selfLearner']:
            instance.evidences = self.cleaned_data['evidences_selfLearner']

        password = self.cleaned_data.get('password1')
        if password:
            instance.set_password(password)

        if commit:
            instance.save()

        return instance

    



class CustomLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add classes to the username field
        self.fields['username'].widget.attrs.update({
            'class': 'form-control border-2 border-bottom fs-5',
            'placeholder': 'Email',
        })

        # Add classes and placeholder to the password field
        self.fields['password'].widget.attrs.update({
            'class': 'form-control border-2 border-bottom fs-5',
            'placeholder': 'Password',
        })