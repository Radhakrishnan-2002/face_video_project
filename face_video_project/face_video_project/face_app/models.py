from django.db import models

class RegTb(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.username

class ComplaintTb(models.Model):
    STATUS_CHOICES = [
        ('New Complaint', 'New Complaint'),
        ('Investigation in Progress', 'Investigation in Progress'),
        ('Face Matched', 'Face Matched'),
        ('Match Failed', 'Match Failed'),
        ('Closed', 'Closed'),
    ]
    complaint_no = models.CharField(max_length=20, unique=True)
    username = models.ForeignKey('RegTb', on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    umobile = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    filename = models.ImageField(upload_to='uploads/', null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='New Complaint')

    def __str__(self):
        return f"{self.complaint_no} - {self.name}"


class InvestigationTb(models.Model):
    STATUS_CHOICES = [
        ('Video Loaded', 'Video Loaded'),
        ('Face Matched', 'Face Matched'),
        ('Match Failed', 'Match Failed'),
        ('Closed', 'Closed'),
    ]
    complaint = models.ForeignKey(ComplaintTb, on_delete=models.CASCADE, related_name='investigation')
    video_file = models.FileField(upload_to='investigations/', null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Video Loaded')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Investigation for {self.complaint.complaint_no}"