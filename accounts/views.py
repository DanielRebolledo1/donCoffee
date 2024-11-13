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
from django.shortcuts import get_object_or_404

import requests

from .forms import RegistrationForm, UserForm, UserProfileForm
from carts.models import Cart, CartItem
from .models import Account, UserProfile
from carts.views import _cart_id
from orders.models import Pedido


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
            
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()
            
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
            
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart = cart).exists()
                
                if is_cart_item_exist:
                    cart_item = CartItem.objects.filter(cart = cart)
                    
                    #getting the product variation by cart id
                    producto_variation = []
                    for item in cart_item:
                        variation = item.variantes.all()
                        producto_variation.append(list(variation))
                        
                    # get the cart items from the user to access his product variation
                    cart_item = CartItem.objects.filter(user = user)
                    ex_var_list = []
                    id = []
                    
                    for item in cart_item:
                        existing_variation = item.variantes.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                        
                    for pr in producto_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id  = id[index]
                            item = CartItem.objects.get(id = item_id)
                            item.cantidad += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart = cart)
                            
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            
            auth.login(request, user)
            messages.success(request, 'Ha iniciado sesión correctamente')
            url = request.META.get('HTTP_REFERER')
            
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
                
            except:
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
    orders = Pedido.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered = True)
    orders_count = orders.count()
    
    context ={
        'orders_count': orders_count,
    }
    
    return render(request, 'accounts/dashboard.html', context)


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


def my_orders(request):
    orders = Pedido.objects.filter(user=request.user, is_ordered = True).order_by('-created_at')
    
    context = {
        'orders': orders
    }
    return render(request, 'accounts/my_orders.html', context)

def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user = request.user)
    if request.method == 'POST':
        user_form =UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Su perfil se ha modificado')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)