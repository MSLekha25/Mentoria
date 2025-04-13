from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
import random
import string
from .models import User, Student, Professional, OTP
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

def index(request):
    return render(request, 'index.html')

def programs(request):
    return render(request, 'programs.html')

def courses(request):
    return render(request, 'courses.html')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'message': 'Login successful!'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid email or password.'})
        else:
            # Traditional form submission
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login.html')

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            # Get form data - handle both AJAX and regular form submissions
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    print("Received JSON data:", data)  # Debug log
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {str(e)}, Body: {request.body}")
                    return JsonResponse({'success': False, 'message': f'Invalid JSON format: {str(e)}'})
            else:
                data = request.POST
                print("Received POST data:", data)  # Debug log
            
            # Extract common user data
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            mobile = data.get('mobile')
            gender = data.get('gender')
            location = data.get('location')
            password = data.get('password')
            user_type = data.get('user_type')  # 'student' or 'professional'
            newsletter_subscribed = data.get('newsletter', False)  # Match the form field name

            print(f"Extracted data: email={email}, user_type={user_type}")  # Debug log
            
            # Validate required fields
            if not (first_name and last_name and email and password and user_type):
                return JsonResponse({'success': False, 'message': 'Required fields missing: name, email, password, and user type are required'})
            
            # Additional field validation can be more flexible
            if not (mobile and gender and location):
                print(f"Warning: Some fields missing - mobile={mobile}, gender={gender}, location={location}")
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Email already registered'})
            
            # Create user with default values for any missing fields
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name or "",
                last_name=last_name or "",
                mobile=mobile or "",
                gender=gender or "other",
                location=location or "",
                user_type=user_type,
                newsletter_subscribed=newsletter_subscribed
            )
            
            # Create specific profile based on user type
            if user_type == 'student':
                college_name = data.get('college_name')
                year = data.get('year')
                branch = data.get('branch')
                
                if not (college_name and year and branch):
                    print(f"Missing student fields: college_name={college_name}, year={year}, branch={branch}")
                    # We'll create with empty values instead of failing
                
                Student.objects.create(
                    user=user,
                    college_name=college_name or "",
                    year=year or "1",
                    branch=branch or ""
                )
            elif user_type == 'professional':
                organization = data.get('organization')
                designation = data.get('designation')
                
                if not (organization and designation):
                    print(f"Missing professional fields: organization={organization}, designation={designation}")
                    # We'll create with empty values instead of failing
                
                Professional.objects.create(
                    user=user,
                    organization=organization or "",
                    designation=designation or ""
                )
            
        
            # Return successful response
            response_data = {
                'success': True, 
                'message': 'Registration successful!',
                'user_id': user.id,
            }
            print(f"Successful registration for {email}")
            return JsonResponse(response_data)
                
        except Exception as e:
            import traceback
            print(f"Registration error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return render(request, 'register.html')

def logout_view(request):
    """
    Logs out the user and redirects to the home page.
    """
    logout(request)
    return redirect('index')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def forgot_password(request):
    return render(request, 'contact.html')

def reset_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate token and UID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL using request's build_absolute_uri
            reset_path = f'/reset_password/{uid}/{token}/'
            reset_url = f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}{reset_path}"
            
            try:
                # Prepare email content
                context = {
                    'user': user,
                    'reset_url': reset_url,
                    'site_name': 'Mentoria'
                }
                
                email_html = render_to_string('emails/password_reset_email.html', context)
                
                # Send email
                send_mail(
                    subject='Reset your Mentoria password',
                    message=str(reset_url),  # Simple text fallback
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=email_html,
                    fail_silently=False,
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Password reset link has been sent to your email.'
                    })
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('login')
                
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Failed to send reset email. Please try again.'
                    }, status=500)
                messages.error(request, 'Failed to send reset email. Please try again.')
                return redirect('login')
            
        except User.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'No account found with this email address.'
                })
            messages.error(request, 'No account found with this email address.')
            return redirect('login')
    
    # Handle GET request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method.'
        }, status=400)
    return render(request, 'reset_password.html')

def reset_password_confirm(request, uidb64, token):
    try:
        # Decode the UID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        # Verify token
        if not default_token_generator.check_token(user, token):
            messages.error(request, 'Password reset link is invalid or has expired.')
            return redirect('login')
        
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'reset_password_confirm.html')
            
            # Set new password
            user.set_password(password)
            user.save()
            
            messages.success(request, 'Your password has been reset successfully. You can now login with your new password.')
            return redirect('login')
        
        return render(request, 'reset_password_confirm.html')
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Password reset link is invalid or has expired.')
        return redirect('login')

def reset_password_done(request):
    return render(request, 'reset_password_done.html')
