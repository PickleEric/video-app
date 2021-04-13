from urllib import parse
from django.core.exceptions import ValidationError
from django.db import models



class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=40, unique=True)
    
    def save(self, *arg, **kwargs):
        #extract video ID from URL
        #if not self.url.startswith('https://www.youtube.com/watch'):
            #raise ValidationError(f'Not a YouTube URL {self.video_id}')

        url_components =  parse.urlparse(self.url)

        if url_components.scheme != 'https':
            raise ValidationError(f'Not a YouTube URL {self.url}')

        if url_components.netloc != 'www.youtube.com':
            raise ValidationError(f'Not a YouTube URL {self.url}')
            
        if url_components.path != '/watch':
            raise ValidationError(f'Not a YouTibe URL {self.url}')

        query_string = url_components.query # 'v=13442234'
        if not query_string:
            raise ValidationError(f'Invalid YouTube URL {self.url}')
        parameters = parse.parse_qs(query_string, strict_parsing=True) # dictionary
        v_parameters_list = parameters.get('v') # return None if no key found, e.g abc=1234
        if not v_parameters_list: # true if None or empty list
            raise ValidationError('Invalid YouTube URL, missing parameters {self.url}')
        self.video_id = v_parameters_list[0] # string

        super().save(*arg, **kwargs)


    def __str__(self):
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url}, Video ID:{self.video_id} Notes: {self.notes[:200]}'