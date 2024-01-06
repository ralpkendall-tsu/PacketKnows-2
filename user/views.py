from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm, CustomUserForm
from django.contrib.auth import login, authenticate, logout
from .models import UserCategory, CustomUser
from django.http import HttpResponse

# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'core/landing-page.html'
    form_class = CustomLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['showLoginModal'] = True
        context['loginForm'] = context['form']

        return context
    
def SignupView(request):
    context = {}
    if request.method == 'POST':
        forms = CustomUserForm(request.POST, request.FILES)
        if forms.is_valid():
            user = forms.save(commit=False)
            if(request.POST['category'] == 'student'):
                user.category = UserCategory.objects.get(name="Student")
            elif(request.POST['category'] == 'instructor'):
                user.category = UserCategory.objects.get(name="Instructor")
            elif(request.POST['category'] == 'selfLearner'):
                user.category = UserCategory.objects.get(name="Self Learner")

            user.save()
            login(request, user)
            return redirect('core:dashboard')
        else:
            context['signupForm'] = forms
            context['showSignupModal'] = True
    else:
        context['showSignupModal'] = True

    return render(request, 'core/landing-page.html', context)

