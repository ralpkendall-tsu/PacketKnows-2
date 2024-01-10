import datetime, jwt
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm, CustomUserForm
from django.contrib.auth import login, authenticate, logout
from .models import UserCategory, CustomUser
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.core.mail import send_mail

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

            user.is_active = False
            user.save()
            
            # send email of jwt token link
            payload = {
                'id': user.email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
                'iat': datetime.datetime.utcnow()
            }
            token = jwt.encode(payload, 'signin', algorithm='HS256')
            sendVerificationMail(token, user.email)
            
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('core:landingPage')
        else:
            context['signupForm'] = forms
            context['showSignupModal'] = True
    else:
        context['showSignupModal'] = True

    return render(request, 'core/landing-page.html', context)

def VerifyView(request, token):
    try:
        # Decode the JWT token
        payload = jwt.decode(token, 'signin', algorithms=['HS256'])
        
        # Check if 'id' is present in the payload
        if 'id' in payload:
            user = CustomUser.objects.get(email=payload['id'])

            # Check if the user exists
            if user:
                # Check if the user is not already active
                if not user.is_active:
                    # Activate the user and save
                    user.is_active = True
                    user.save()

                    messages.success(request, 'Verification successful! You can now log in to your account.')
                    return redirect('core:landingPage')
                else:
                    messages.warning(request, 'Account is already verified. You can log in.')
            else:
                messages.error(request, 'User not found.')
        else:
            messages.error(request, 'Invalid token format. Missing "id" in payload.')

    except jwt.ExpiredSignatureError:
        messages.error(request, 'Verification link has expired. Please request a new one.')
    except jwt.InvalidTokenError:
        messages.error(request, 'Invalid token. Please request a new verification link.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        # Log the exception for further investigation
        print(f'Error in VerifyView: {str(e)}')
        return HttpResponseServerError()

    return redirect('core:landingPage')

def UpdateProfileView(request):
    if request.method == "POST":
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        icon = request.FILES.get('icon') 
        print(icon)
        print(firstName)
        print(lastName)
        if firstName and lastName:
            user = CustomUser.objects.get(email=request.user.email)
            print(user.icon)
            user.first_name = firstName
            user.last_name = lastName
            user.save()
            if icon:
                file_name = default_storage.save(icon.name, ContentFile(icon.read()))
                user.icon = file_name 
                user.save()

            return JsonResponse({'success': True, 'message': 'Profile updated successfully!'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid data provided'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def sendVerificationMail(token, email):
    user = CustomUser.objects.get(email=email)
    subject = "Account Verification: Please Confirm Your Packet Knows Registration"
    verification_link = f"{settings.SITE_DOMAIN}/user/verify/{token}/"
    full_name = f"{user.first_name} {user.last_name}"
    message = (
        f"Dear {full_name},\n\n"
        "Thank you for registering with Packet Knows. To complete the registration process, "
        "please click on the following link to verify your account:\n\n"
        f"{verification_link}\n\n"
        "If you did not sign up for Packet Knows, please ignore this email.\n\n"
        "Best regards,\n"
        "Packet Knows Team"
    )

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

