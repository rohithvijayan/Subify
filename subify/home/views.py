from django.shortcuts import render,redirect,HttpResponse
from .models import upload_video
import openai

from moviepy.editor import *
import srt
from datetime import timedelta
import os
from openai.types.audio import transcription,translation,Transcription
from django.core.files import File
from django.http import FileResponse
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
        
        return redirect("generate",id=new_vid.id)
       
    return render(request,"home/upload.html")

def features(request):
    return render(request,"home/features.html")
def about(request):
    return render(request,"home/about.html")
def gen_sub(request,id):
    source_vid=upload_video.objects.get(id=id)
    sub_name=source_vid.title+str(source_vid.id)
    file_path=source_vid.video.path
    audioclip=AudioFileClip(file_path)
    audioclip.write_audiofile(f"media/converted_audio/{sub_name}.wav")
    whisper=openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    audio=open(file=f"media/converted_audio/{sub_name}.wav",mode='rb')
    try:
        sub=whisper.audio.transcriptions.create(file=audio,model="whisper-1",response_format='verbose_json',temperature=0,timestamp_granularities=['segment'])
    except openai.APIConnectionError as e:
        return HttpResponse("Unfortunately There Has Been A Connection Error.Please Try Again",e.__cause__)
    except openai.APIStatusError as e:
        return HttpResponse("Unfortunately Beta Version of Subify Supports only Small Files(.wav <25MB)\nTry Again With Smaller Files\nSubify Stable Release v1.0 Will support Larger Files",e.__cause__)
    
    print(sub)
    segments=sub.segments
    content_list=[]
    subtitle_file_path = f"media/subtitles/{sub_name}.srt"
    for item in segments:
        index=item['id']
        start=item['start']
        end=item['end']
        text=item['text']
        subtitle=srt.Subtitle(index=index,start=timedelta(seconds=start),end=timedelta(seconds=end),content=text)
        content_list.append(subtitle)
        
    with open(subtitle_file_path,"w") as srtfile:
        srtfile.write(srt.compose(subtitles=content_list))
    
    with open(subtitle_file_path,"rb") as srtfile:
        source_vid.subfile.save(name=f"{sub_name}.srt", content=File(srtfile))

    response=FileResponse(open(subtitle_file_path, "rb"),as_attachment=True)
    return response
def github(request):
     return redirect("https://github.com/rohithvijayan/Subify")      
def linkedin(request):
    return redirect("https://www.linkedin.com/in/rohith-vijayan-081b34227/")
