from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import RegTb, ComplaintTb, InvestigationTb
import os
from django.conf import settings
import uuid
from django.urls import reverse
import cv2
import numpy as np
from django.core.files.storage import default_storage
from django.db import transaction
from django.core.exceptions import ValidationError


def home(request):
    return render(request, 'index.html')

def admin_login(request):
    if request.method == 'POST':
        uname = request.POST.get('uname')
        password = request.POST.get('password')
        if uname == 'admin' and password == 'admin':
            data = RegTb.objects.all()
            # messages.success(request, "You have successfully logged in!")
            return render(request, 'AdminHome.html', {'data': data})
        # else:
        #     # messages.error(request, "Username or Password Incorrect!")
    return render(request, 'AdminLogin.html')

def admin_home(request):
    return render(request, 'AdminHome.html')


def user_list(request):
    users = RegTb.objects.all()
    return render(request, 'UsersList.html', {'users': users})

def complaint_list(request):
    complaints = ComplaintTb.objects.all()
    return render(request, 'ComplaintList.html', {'complaints': complaints})

def user_login(request):
    if request.method == 'POST':
        uname = request.POST.get('uname')
        password = request.POST.get('password')
        try:
            user = RegTb.objects.get(username=uname, password=password)
            request.session['uname'] = uname
            # messages.success(request, "You have successfully logged in!")
            return render(request, 'UserHome.html', {'data': user})
        except RegTb.DoesNotExist:
            # messages.error(request, 'Username or Password is incorrect.')
            return render(request, 'UserLogin.html')
    return render(request, 'UserLogin.html')

def user_home(request):
    uname = request.session.get('uname')
    if not uname:
        return redirect('user_login')  # Redirect to login if not authenticated
    user = get_object_or_404(RegTb, username=uname)
    return render(request, 'UserHome.html', {'data': user})

def new_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        address = request.POST.get('address')
        uname = request.POST.get('uname')
        password = request.POST.get('password')
        RegTb.objects.create(name=name, mobile=mobile, email=email, address=address, username=uname, password=password)
        # messages.success(request, "Record Saved!")
        return redirect('user_login')
    return render(request, 'NewUser.html')

def new_complaint(request):
    if request.method == 'POST':
        uname = request.session.get('uname')  # Get the username from the session
        name = request.POST.get('name')
        umobile = request.POST.get('mobile')
        email = request.POST.get('email')
        address = request.POST.get('address')
        file = request.FILES['file']

        # Generate a unique complaint number
        complaint_no = f"CMP-{uuid.uuid4().hex[:8].upper()}"
        
        try:
            # Fetch the user instance based on the session username
            user_instance = RegTb.objects.get(username=uname)

            # Save complaint data to the database
            complaint = ComplaintTb.objects.create(
                complaint_no=complaint_no,
                username=user_instance,
                name=name,
                mobile=umobile,
                email=email,
                address=address,
                filename=file,  # Save the uploaded file directly
                status='New Complaint'
            )
            # messages.success(request, f"Complaint {complaint_no} Posted Successfully!")
            return redirect(reverse('u_complaint_info', kwargs={'complaint_no': complaint.complaint_no}))

        except RegTb.DoesNotExist:
            # messages.error(request, f"User with username {uname} does not exist.")
            return redirect('new_complaint')

    return render(request, 'NewComplaint.html')

def user_complaints(request):
    uname = request.session.get('uname')  # Use 'uname' instead of 'username'
    if uname:
        complaints = ComplaintTb.objects.filter(username__username=uname)  # Filter complaints by username
        return render(request, 'user_complaints.html', {'complaints': complaints})
    else:
        # messages.error(request, "You are not logged in!")
        return redirect('user_login')

def complaint_detail(request, complaint_no):
    complaint = get_object_or_404(ComplaintTb, complaint_no=complaint_no)
    return render(request, 'ComplaintDetail.html', {'complaint': complaint})


def u_complaint_info(request, complaint_no):
    complaint = get_object_or_404(ComplaintTb, complaint_no=complaint_no)
    return render(request, 'UComplaintInfo.html', {'complaint': complaint})


def upload_video(request, complaint_no):
    complaint = get_object_or_404(ComplaintTb, complaint_no=complaint_no)

    investigation, created = InvestigationTb.objects.get_or_create(
        complaint=complaint,
        defaults={'status': 'Video Loaded'}
    )

    allowed_video_formats = ['video/mp4', 'video/avi', 'video/mkv', 'video/webm', 'video/mov']

    if request.method == 'POST':
        # Check if the file is uploaded
        if 'video_file' in request.FILES:
            video_file = request.FILES['video_file']

            # Check if the file type is valid
            if video_file.content_type not in allowed_video_formats:
                # messages.error(request, "Invalid file format. Please upload a valid video file (MP4, AVI, MKV, etc.).")
                return render(request, 'UploadVideo.html', {'investigation': investigation})
            
            # If file format is valid, save it
            investigation.video_file = video_file
            investigation.status = 'Video Loaded'
            investigation.save()

            # Update complaint status to "Investigation in Progress"
            complaint.status = "Investigation in Progress"
            complaint.save()

            # messages.success(request, "Video uploaded successfully and investigation started.")
            return redirect('complaint_list')

        # If no file uploaded
        # else:
        #     # messages.error(request, "Please provide a valid video file.")
    
    # Handle the cancel button if clicked (can redirect to complaint list or another page)
    if request.POST.get('cancel'):
        # messages.info(request, "Video upload cancelled.")
        return redirect('complaint_list')  # Or any other page as needed

    return render(request, 'UploadVideo.html', {'investigation': investigation})
	
def face_match(request, complaint_no):
    complaint = get_object_or_404(ComplaintTb, complaint_no=complaint_no)
    investigation = InvestigationTb.objects.filter(complaint=complaint).last()

    if not investigation or not investigation.video_file:
        # messages.error(request, "No video uploaded for investigation!")
        return redirect('complaint_list')

    if request.method == 'POST':
        video_path = default_storage.path(investigation.video_file.name)
        video_capture = cv2.VideoCapture(video_path)
        ret, frame = video_capture.read()
        video_capture.release()

        if not ret:
            # messages.error(request, "Error reading video file!")
            return redirect('complaint_list')

        complaint_image_path = complaint.filename.path
        if not os.path.exists(complaint_image_path):
            # messages.error(request, "Complaint image not found!")
            return redirect('complaint_list')

        complaint_image = cv2.imread(complaint_image_path)

        def get_face_features(image):
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            for (x, y, w, h) in faces:
                face = image[y:y + h, x:x + w]
                return cv2.resize(face, (100, 100))
            return None

        def compare_faces(face1, face2):
            face1 = cv2.cvtColor(face1, cv2.COLOR_BGR2GRAY) / 255.0
            face2 = cv2.cvtColor(face2, cv2.COLOR_BGR2GRAY) / 255.0
            face1_flat = face1.flatten()
            face2_flat = face2.flatten()
            similarity = np.dot(face1_flat, face2_flat) / (np.linalg.norm(face1_flat) * np.linalg.norm(face2_flat))
            return similarity

        complaint_face = get_face_features(complaint_image)
        frame_face = get_face_features(frame)

        if complaint_face is None or frame_face is None:
            # messages.error(request, "No faces detected in one or both images!")
            investigation.status = "Match Failed"
            complaint.status = "Match Failed"
            investigation.save()
            complaint.save()

            return redirect('complaint_list')

        similarity_score = compare_faces(complaint_face, frame_face)
        match_found = similarity_score > 0.6

        with transaction.atomic():
            if match_found:
                investigation.status = "Face Matched"
                complaint.status = "Face Matched"
                # messages.success(request, "Face match found!")
            else:
                investigation.status = "Match Failed"
                complaint.status = "Match Failed"
                # messages.error(request, "Face match not found!")

            investigation.save()
            complaint.save()

        return redirect('complaint_list')

    return render(request, 'FaceMatch.html', {'complaint': complaint, 'investigation': investigation})
	
def investigation_list(request):
    investigations = InvestigationTb.objects.select_related('complaint').all()
    return render(request, 'InvestigationList.html', {'investigations': investigations})