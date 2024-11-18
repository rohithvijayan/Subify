from django.shortcuts import render, redirect, HttpResponse
import openai.error
from .models import upload_video
import openai
from moviepy.editor import AudioFileClip
import srt
from datetime import timedelta
import os
import re
from django.core.files import File
from django.http import FileResponse
import requests

def home(request):
    return render(request, "home/index.html")

def vidUpload(request):
    if request.method == "POST" and "vid" in request.FILES:
        title = request.POST['title']
        videos = request.FILES
        videofile = videos["vid"]
        new_vid = upload_video(title=title, video=videofile)
        new_vid.save()
        
        return redirect("generate", id=new_vid.id)
       
    return render(request, "home/upload.html")

def features(request):
    return render(request, "home/features.html")

def about(request):
    return render(request, "home/about.html")

def gen_sub(request, id):
    source_vid = upload_video.objects.get(id=id)
    sub_name = source_vid.title + str(source_vid.id)
    file_path = source_vid.video.path
    audioclip = AudioFileClip(file_path)
    audioclip.write_audiofile(f"media/converted_audio/{sub_name}.wav")
    
    openai. api_key=os.environ.get("OPENAI_API_KEY")
    audio = open(f"media/converted_audio/{sub_name}.wav", mode='rb')

    try:
        sub = openai.Audio.transcribe(
            model="whisper-1",
            file=audio,
            response_format="verbose_json",
            temperature=0
        )
    except openai.error.OpenAIError as e: 
        return HttpResponse(f"OpenAI API error occurred: {str(e)}")
    except requests.exceptions.RequestException as e: 
        return HttpResponse(f"Network error occurred: {str(e)}")
    except Exception as e:  
        return HttpResponse(f"An unexpected error occurred: {str(e)}")

    print(sub)
    
    
    DEFAULT_TIME_GAP = 1.4 
    dynamic_gap = DEFAULT_TIME_GAP
    segments = sub["segments"]

  
    def split_into_sentences(text):
        
        return re.split(r'(?<=[.!?]) +', text.strip())

   
    content_list = []
    index = 1  
    last_end_time = 0

   
    for segment in segments:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"].strip()

       
        sentences = split_into_sentences(text)

        
        sentence_start_time = start_time
        for sentence in sentences:
            
            sentence_duration = len(sentence) / len(text) * (end_time - start_time)
            sentence_end_time = sentence_start_time + sentence_duration

           
            subtitle = srt.Subtitle(
                index=index,
                start=srt.timedelta(seconds=sentence_start_time),
                end=srt.timedelta(seconds=sentence_end_time),
                content=sentence
            )
            content_list.append(subtitle)
            
            
            sentence_start_time = sentence_end_time
            index += 1

       
        last_end_time = end_time

    subtitle_file_path = f"media/subtitles/{sub_name}.srt"
    with open(subtitle_file_path, "w") as srtfile:
        srtfile.write(srt.compose(content_list))
    

    with open(subtitle_file_path, "rb") as srtfile:
        source_vid.subfile.save(name=f"{sub_name}.srt", content=File(srtfile))

   
    response = FileResponse(open(subtitle_file_path, "rb"), as_attachment=True)
    return response

def github(request):
    return redirect("https://github.com/rohithvijayan/Subify")      

def linkedin(request):
    return redirect("https://www.linkedin.com/in/rohith-vijayan-081b34227/")