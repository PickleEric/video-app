from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import Video

class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Smart Food Choices')

class TestAddVideos(TestCase):

    def test_add_video(self):
        valid_video = {
            'name': 'simple recipies',
            'url': 'https://www.youtube.com/watch?v=vmdITEguAnE',
            'notes': '',
        }
        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)

        self.assertTemplateUsed('video_collector/video_list.html')

        # does the video list show a new video?
        self.assertContains(response, 'simple recipies')
        self.assertContains(response, '')
        self.assertContains(response, 'https://www.youtube.com/watch?v=vmdITEguAnE')

        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        video = Video.objects.first()
        
        self.assertEqual('simple recipies', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=vmdITEguAnE', video.url)
        self.assertEqual('', video.notes)
        self.assertEqual('vmdITEguAnE', video.video_id)

    def test_add_video_invalid_url_not_added(self):

        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch!',
            'https://www.youtube.com/watchabc=525',
            'https://www.youtube.com/watchv='
            'https://www.github.com'
            'https://www.reddit.com'
        ]

        for invalid_video_url in invalid_video_urls:
            new_video = {
                'name': 'example',
                'url': invalid_video_url,
                'notes': 'example notes'
            }

            url = reverse('add_video')
            response = self.client.post(url, new_video)

            self.assertTemplateNotUsed('video_collector/add.html')

            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]

            self.assertIn('Invalid YouTube URL', message_texts)
            self.assertIn('Please check the data entered', message_texts)

            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):
    
    def test_all_videos_displayed_in_correct_order(self):

        v1 = Video.objects.create(name='abc', notes="example", url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='dEf', notes="example", url='https://www.youtube.com/watch?v=129')
        v3 = Video.objects.create(name='AAA', notes="example", url='https://www.youtube.com/watch?v=128')
        v4 = Video.objects.create(name='ZXY', notes="example", url='https://www.youtube.com/watch?v=127')

        expected_video_order = [ v3, v1, v2, v4 ]

        url = reverse('video_list')
        response = self.client.get(url)

        videos_in_templates = list(response.context[ 'videos' ])

        self.assertEqual(videos_in_templates, expected_video_order)
    def test_no_video_message(self):
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No videos')
        self.assertEqual(0, len(response.context['videos']))

    def test_video_number_message_two_videos(self):
        v1 = Video.objects.create(name='abc', notes="example", url='https://www.youtube.com/watch?v=123')
        v1 = Video.objects.create(name='abc', notes="example", url='https://www.youtube.com/watch?v=124')
        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '2 videos')
        

class TestVideoSearch(TestCase):
    pass

class TestVideoModel(TestCase):

    def test_invalid_url_raises_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse'
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watchabc=525',
            'https://www.youtube.com/watchv='
            'https://www.github.com'
            'https://www.reddit.com'
        ]
        for invalid_video_url in invalid_video_urls:

            with self.assertRaises(ValidationError):

                Video.objects.create(name='example', url=invalid_video_url, notes='example notes')
                
        self.assertEqual(0, Video.objects.count())

    

    def test_dublicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='abc', notes="example", url='https://www.youtube.com/watch?v=123')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='abc', notes="example", url='https://www.youtube.com/watch?v=123')
