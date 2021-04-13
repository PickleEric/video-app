from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db import IntegrityError
from django.db.models.functions import Lower
from .models import Video
from .forms import SearchForm, VideoForm

def home(request):
    app_name = 'Smart Food Choices'
    return render(request, 'video_collector/home.html', {'app_name': app_name})

def add(request):
    if request.method == 'POST':
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():
            try:
                new_video_form.save()
                return redirect('video_list')
                
            except ValidationError:
                messages.warning(request, 'Invalid YouTube URL')
            except IntegrityError:
                messages.warning(request, 'You already added that video')
        
        messages.warning('Please check the link.')
        return render(request, 'video_collector/add.html', {'new_video_form': new_video_form})
            
    new_video_form = VideoForm()
    return render(request, 'video_collector/add.html', {'new_video_form': new_video_form})

def video_list(request):

    search_form = SearchForm(request.GET)

    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term']   
        videos =Video.objects.filter(name__icontains=search_term).order_by(Lower('name'))

    else:
        search_form = SearchForm()
        videos = Video.objects.order_by('name')

    return render(request, 'video_collector/video_list.html', {'videos': videos, 'search_form': search_form})

