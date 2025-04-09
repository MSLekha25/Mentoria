from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
import random
import string
from .models import User, Student, Professional, OTP

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if user.is_email_verified:
                    login(request, user)
                    return JsonResponse({'success': True, 'message': 'Login successful!'})
                else:
                    return JsonResponse({'success': False, 'message': 'Please verify your email address first.'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid email or password.'})
        else:
            # Traditional form submission
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if user.is_email_verified:
                    login(request, user)
                    return redirect('index')
                else:
                    messages.error(request, 'Please verify your email address first.')
            else:
                messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login.html')

def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    
    return render(request, 'register.html')

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Common fields for both user types
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            mobile = data.get('mobile')
            gender = data.get('gender')
            location = data.get('location')
            user_type = data.get('user_type')
            newsletter = data.get('newsletter', False)
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Email already exists'})
            
            # Create user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                mobile=mobile,
                gender=gender,
                location=location,
                user_type=user_type,
                newsletter_subscribed=newsletter
            )
            
            # Create profile based on user type
            if user_type == 'student':
                college_name = data.get('college_name')
                year = data.get('year')
                branch = data.get('branch')
                
                Student.objects.create(
                    user=user,
                    college_name=college_name,
                    year=year,
                    branch=branch
                )
            elif user_type == 'professional':
                organization = data.get('organization')
                designation = data.get('designation')
                
                Professional.objects.create(
                    user=user,
                    organization=organization,
                    designation=designation
                )
            
            # Generate and send OTP
            otp_code = ''.join(random.choices(string.digits, k=6))
            expiry_time = timezone.now() + timedelta(minutes=10)
            
            OTP.objects.create(
                user=user,
                otp_code=otp_code,
                expires_at=expiry_time
            )
            
            # In a real implementation, send an email with the OTP
            # For now, just return success with the OTP (in production, don't send OTP in response)
            return JsonResponse({
                'success': True, 
                'message': 'Registration successful! Please verify your email.',
                'user_id': user.id,
                'otp': otp_code  # Remove this in production
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            otp_code = data.get('otp_code')
            
            # Get the latest unused OTP for this user
            try:
                user = User.objects.get(id=user_id)
                otp = OTP.objects.filter(
                    user=user,
                    otp_code=otp_code,
                    is_used=False,
                    expires_at__gt=timezone.now()
                ).latest('created_at')
                
                # Mark OTP as used
                otp.is_used = True
                otp.save()
                
                # Mark user as verified
                user.is_email_verified = True
                user.save()
                
                return JsonResponse({'success': True, 'message': 'Email verified successfully!'})
                
            except (User.DoesNotExist, OTP.DoesNotExist):
                return JsonResponse({'success': False, 'message': 'Invalid or expired OTP'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@csrf_exempt
def resend_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            try:
                user = User.objects.get(id=user_id)
                
                # Generate new OTP
                otp_code = ''.join(random.choices(string.digits, k=6))
                expiry_time = timezone.now() + timedelta(minutes=10)
                
                OTP.objects.create(
                    user=user,
                    otp_code=otp_code,
                    expires_at=expiry_time
                )
                
                # In a real implementation, send an email with the OTP
                # For now, just return success with the OTP (in production, don't send OTP in response)
                return JsonResponse({
                    'success': True, 
                    'message': 'OTP resent successfully!',
                    'otp': otp_code  # Remove this in production
                })
                
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def forgot_password(request):
    return render(request, 'contact.html')
