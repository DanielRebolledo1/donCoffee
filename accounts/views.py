from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings

#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .forms import RegistrationForm
from .models import Account


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user( first_name = first_name, last_name = last_name, email= email, username = username, password = password)
            user.phone_number = phone_number
            user.save()
            
            #USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Por favor active su cuenta'
            message = render_to_string('accounts/account_verification_email.html',{
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage( mail_subject, message, settings.EMAIL_HOST_USER, to=[to_email])
            send_email.send()
            # messages.success(request, 'Registro completado con exito. Se ha enviado un correo de verificacion a su email')
            return redirect('/accounts/login/?command=verification&email='+email)
        else:
            # Muestra los errores de cada campo
            for field, errors in form.errors.items():
                if field != '__all__':
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
                else:
                    # Errores generales del formulario
                    for error in errors:
                        messages.error(request, error)
    else:
        form = RegistrationForm()

    context ={
        'form' : form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(email = email, password = password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Ha iniciado sesión correctamente')
            
            return redirect('dashboard')
        
        else:
            messages.error(request, 'Email o contraseña incorrecto')
            return redirect('login')
    
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Ha cerrado sesión correctamente')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
     
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Felicidades, su cuenta ha sido activada correctamente')
        return redirect('login')
    else:
        messages.error(request, 'Error link de activacion')
        return redirect('register')


@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotPassword(request):
    
    if request.method == 'POST':
        email = request.POST['email']
        
        if Account.objects.filter(email = email).exists():
            user = Account.objects.get(email__exact = email)
            
            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Restablecer Contraseña'
            message = render_to_string('accounts/reset_password_email.html',{
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage( mail_subject, message, settings.EMAIL_HOST_USER, to=[to_email])
            send_email.send()            
            
            messages.success(request, 'Se ha enviado un email a su correo para restablecer su contraseña')
            return redirect('login')
            
        else:
            messages.error(request, 'El correo ingresado no esta asociado a una cuenta')
            return redirect('forgotPassword')
        
    return render(request, 'accounts/forgotPassword.html')

def reset_password_validate(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Por favor restablezca su contraseña')
        return redirect('resetPassword')
    else:
        messages.error(request, 'Este link ha caducado')
        return redirect('login')

def resetPassword(request):

    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
   
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Contraseña restablecida con éxito')
            return redirect('login')
        
        else:
            messages.error(request, 'Las contraseñas ingresadas no coinciden')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
