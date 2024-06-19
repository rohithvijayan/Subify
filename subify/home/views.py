from django.shortcuts import render,redirect,HttpResponse
from .models import upload_video
# Create your views here.
def home(request):
    return render(request,"home/index.html")

def vidUpload(request):
    if request.method=="POST" and "vid" in request.FILES:
        title=request.POST['title']
        videos=request.FILES
        videofile=videos["vid"]
        new_vid=upload_video(title=title,video=videofile)
        new_vid.save()
        return HttpResponse("SUCCESS") 
       
    return render(request,"home/upload.html")