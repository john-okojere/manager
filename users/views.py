import base64
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import  UserUpdateForm

# User login view
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role == "Manager":
                login(request, user)
                return redirect('face-auth')  # Redirect to the dashboard
            else:
                logout(request, user)
                return render(request, 'users/signin-2.html', {'error': 'You are not a Manager'})
        else:
            return render(request, 'users/signin-2.html', {'error': 'Invalid credentials'})
    return render(request, 'users/signin-2.html')

# User logout view
def logout_user(request):
    logout(request)
    return redirect('login')  # Redirect to the login page

# User profile view
@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Reload the profile page
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'profile.html', {'form': form})

import cv2
import numpy as np
import face_recognition
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import base64

@login_required
def face_auth(request):
    request.session['face_authenticated'] = True
    return redirect('choose_section')
    # if request.method == "POST":
    #     try:
    #         # Load the user's profile picture
    #         user = request.user
    #         if not user.avatar:
    #             return JsonResponse({'status': 'error', 'message': 'No profile picture found for the user.'})

    #         profile_picture_path = user.avatar.path

    #         # Load and preprocess the reference image
    #         reference_image = face_recognition.load_image_file(profile_picture_path)
    #         reference_encoding = face_recognition.face_encodings(reference_image)[0]

    #         # Decode the base64 image sent from the frontend
    #         data = request.POST.get('image')
    #         if not data:
    #             return JsonResponse({'status': 'error', 'message': 'No image provided.'})

    #         # Decode the base64 image to a numpy array
    #         image_data = base64.b64decode(data.split(',')[1])
    #         nparr = np.frombuffer(image_data, np.uint8)
    #         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    #         # Convert the frame to RGB
    #         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #         # Get encodings of the captured frame
    #         live_encodings = face_recognition.face_encodings(rgb_frame)
    #         if not live_encodings:
    #             return JsonResponse({'status': 'error', 'message': 'No face detected in the video frame.'})

    #         # Compare the reference encoding with the live encoding
    #         threshold = 0.4  # Stricter threshold
    #         match = face_recognition.compare_faces([reference_encoding], live_encodings[0], tolerance=threshold)
    #         distance = face_recognition.face_distance([reference_encoding], live_encodings[0])[0]

    #         if match[0] and distance < threshold:
    #             request.session['face_authenticated'] = True
    #             return JsonResponse({'status': 'success', 'message': 'Face verified successfully!'})
    #         else:
    #             return JsonResponse({'status': 'error', 'message': 'Face verification failed!', 'distance': distance})

    #     except Exception as e:
    #         return JsonResponse({'status': 'error', 'message': str(e)})

    # return render(request, 'users/face-authentication.html')


def choose_section(request):
    user = request.user
    if user.role == 'Cashier':
        if user.section == 'arcade':
            return redirect('arcade_cashier')
        elif user.section.title() == 'Restaurant':
            return redirect('resturant_cashier')
        elif user.section.lower() == 'cosmetic_store':
            return redirect('beauty_cashier')
        elif user.section.lower() == 'salon':
            return redirect('salon_cashier')
        elif user.section.lower() == 'fashion':
            return redirect('fashion_cashier')
        elif user.section.lower() == 'lounge':
            return redirect('lounge_cashier')
        elif user.section.lower() == 'spa':
            return redirect('spa_cashier')
    elif user.role == "Manager":
        if user.section == 'arcade':
            return redirect('arcade_manager')
        elif user.section.title() == 'Restaurant':
            return redirect('resturant_dashboard')
        elif user.section.lower() == 'cosmetic_store':
            return redirect('beauty_manager')
        # elif user.section.lower() == 'salon':
        #     return redirect('salon_manager')
        # elif user.section.lower() == 'fashion':
        #     return redirect('fashion_manager')
        # elif user.section.lower() == 'lounge':
        #     return redirect('lounge_manager')
        # elif user.section.lower() == 'spa':
        #     return redirect('spa_manager')
    elif user.role == 'Waiter':
        if user.section.title() == 'Restaurant':
            return redirect('resturant_waiter')

    return redirect('/')