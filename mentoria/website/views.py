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
                'message': 'Registration successful! Please verify your email.',
                'user_id': user.id,
                'otp': otp_code  # Remove this in production
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
