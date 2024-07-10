
import json
import uuid
from django.shortcuts import render, redirect 
from pytube import *
from moviepy.editor import *
from moviepy.editor import VideoFileClip
from django.conf import settings
from django.urls import reverse

from asgiref.sync import async_to_sync ,sync_to_async
from channels.generic.websocket import WebsocketConsumer ,AsyncWebsocketConsumer




class AdaptiveDownloadConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # Join room group
        async_to_sync( self.channel_layer.group_add)(
            self.room_name, self.channel_name
        )
     
        self.accept()
        
        # we call downlaod function after self.accept()
        # event = {
        #     'type': 'download',
        # }
        # async_to_sync( self.channel_layer.group_send)(self.room_name, event)


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync( self.channel_layer.group_discard)(
            self.room_name, self.channel_name
        )
        print('disconnecting...',close_code)

    def receive(self, text_data):
        data = json.loads(text_data)
        video_id = data['video_id']
        resolution = data['resolution']
        progress_id=data['progress_id']
        event = {
            'type': 'download',
            'video_id' : video_id,
            'resolution' :resolution,
            'progress_id':progress_id
        }
        async_to_sync( self.channel_layer.group_send)(self.room_name, event)
        
        
    def download(self, event):
        video_id=event['video_id']
        resolution=event['resolution']
        progress_id=event['progress_id']
        def progress_func(stream, chunk, bytes_remaining):
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            # percentage_completed is between 0 and 1
            percentage_completed=round(bytes_downloaded / total_size ,2)
            if stream.includes_audio_track :
                
                self.send_msg('audio','audio downloading',percentage_completed,progress_id)
                
            else:
                self.send_msg('video','video downloading',percentage_completed,progress_id)
        try:
            yt=YouTube("https://www.youtube.com/watch?v="+video_id,on_progress_callback=progress_func)
            video=yt.streams.filter(type='video',resolution=resolution).first()
            print('start download')
            # create temp folder path
            temp_dir_path=os.path.join(settings.BASE_DIR, 'temp')
            # download video and audio to temp folder
            video_filename=f"v-{video.default_filename}"
            video.download(temp_dir_path,filename=video_filename)
            print('download video finished')
            audio=yt.streams.filter(type='audio').first()
            audio_filename=f"a-{audio.default_filename}"
            audio.download(temp_dir_path,filename=audio_filename)
            print('download audio finished')
            # create video , audio and merged video pathes
            video_path=os.path.join(temp_dir_path,video_filename)
            audio_path=os.path.join(temp_dir_path,audio_filename)
            id=uuid.uuid4()
            
            merged_file_path=os.path.join(temp_dir_path,f"{id}_{video.default_filename}")
            
            clip = VideoFileClip(video_path)
            clip = clip.subclip(0, 5)
            audio_clip = AudioFileClip(audio_path)
            audio_clip=audio_clip.subclip(0, 5)
            # send start-merge message
            self.send(
                text_data=json.dumps(
                    {
                        "type": "merging....",
                        'progress_id':progress_id
                    }
                )
            )
            video_with_audio = clip.set_audio(audio_clip)
            # write merged video to merged_file_path
            video_with_audio.write_videofile(merged_file_path)
            video_with_audio.close()
            # send merge-finished message
            self.send(
                text_data=json.dumps(
                    {
                        "type": "merge-finished",
                        'progress_id':progress_id,
                        'filename':f"{id}_{video.default_filename}"
                    }
                )
            )
            print("File write finished!")
            # remove video and audio files from temp folder
            os.remove(video_path)
            os.remove(audio_path)
            # # close connection
            # self.disconnect(1000)
        # handling pytube exceptions
        except Exception as e:
            print(f'Exception: {e}')
            exception=f' Exception : {e}'
            self.send(text_data=json.dumps(
                {
                    "type": 'redirect',
                    "url": reverse('exception',kwargs={'exception':exception}),
                    
                }
            ))
       
    
    def send_msg(self,type, msg, progress,progress_id):
        self.send(
            text_data=json.dumps(
                {
                    "type": type,
                    "message": msg,
                    "progress": progress,
                    'progress_id':progress_id
                }
            )
        )

    





