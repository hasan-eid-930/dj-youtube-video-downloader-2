
# importing all the required modules 
import time
from django.shortcuts import render, redirect 
from pytube import *
from django.http import FileResponse, HttpRequest, HttpResponse, JsonResponse, StreamingHttpResponse
import requests
import urllib.parse

from pytube.exceptions import *

from moviepy.editor import *
from django.conf import settings
# from .middleware import cancel_previous_request

from django.contrib.sessions.models import Session

def test(request:HttpRequest):
	sessions = Session.objects.all()
	for s in sessions:
		print(s)
	print(sessions.count())
	return render(request, "test.html")

# @cancel_previous_request
def youtube(request): 
	# checking whether request.method is post or not 
	if request.method == 'POST':
		# getting link from frontend 
		link = request.POST['link']
		try :
			video = YouTube(link)
			print('befor')
			video_info={
                'thumbnail_url':video.thumbnail_url,
                'title':video.title,
                'duration':time.strftime("%H:%M:%S",time.gmtime(video.length)),
                
            }
			if video.age_restricted:
				print("age restricted")
				return render(request, 'age_restricted.html')
			else:
				print("not age restricted")
				streams =video.streams
				print('after')
				audio_streams=[]
				video_streams=[]
				for s in streams.filter(type='audio'):
					if not any(d['subtype'] == s.subtype for d in audio_streams):
						audio_streams.append({'subtype':s.subtype,'size':s.filesize_mb,'url':s.url,'filename':s.default_filename,'mime_type':s.mime_type})
                    # if s.subtype == 'mp4' and (not any(d['resolution'] == s.resolution for d in video_streams)):
				for s in streams.filter(type='video').order_by('resolution').desc():
					if s.subtype == 'mp4' :
						if s.is_adaptive and (s.resolution not in ['720p','480p','360p','240p','144p']) :
							video_streams.append({'subtype':s.subtype,'size':s.filesize_mb,'resolution':s.resolution,'video_id':video.video_id,'mime_type':s.mime_type})
						elif s.is_progressive :
							video_streams.append({'subtype':s.subtype,'size':s.filesize_mb,'resolution':s.resolution,'url':s.url,'filename':s.default_filename,'mime_type':s.mime_type})		
			return JsonResponse({'video':video_info,'audio_streams':audio_streams,'video_streams':video_streams})
		except PytubeError as e:
			if isinstance(e, AgeRestrictedError):
				exception_message='this video is age restricted'
			elif isinstance(e, VideoUnavailable):
				exception_message='this video is unavailabe'
			else :
				exception_message='Youtube Error'

			print(f'youtube view pytube error : {e}')
			return redirect('exception',exception=exception_message)
		except Exception as e:
			print(f'Exception :{e}')
			return redirect('exception',exception='Server Error')
			# return render(request, 'exception.html',{'exception':e})

	return render(request, 'youtube.html')

# defining function 
def download(request): 
	# checking whether request.method is post or not 
	if request.method == 'POST':
		mime_type = request.POST['mime_type'] 
		streaming_url = request.POST['url']
		filename = request.POST['filename'] 
		print(mime_type)
		# if mime_type.startswith('audio'):
		# 	pass
		try:
			stream_generator=requests.get(streaming_url, stream=True)
			# this will raise HttpError if satus code isnt 2xx
			stream_generator.raise_for_status()
			# processing response here
			response = StreamingHttpResponse(stream_generator, content_type=mime_type)
			# # filename = f"{uuid.uuid4()}_{filename}"

			quoted_name = urllib.parse.quote(filename)
			
			response['Content-Disposition'] =f"attachment; filename*=utf-8''{quoted_name};"
			# response['Content-Disposition'] = 'attachment; filename="audio.mp3"'
			return response	
		
		except Exception as e:
			if isinstance(e,requests.exceptions.HTTPError):
				exception='Requests Http Error'
			elif isinstance(e,requests.exceptions.RequestException):
				exception='connection or timeout error'
			else:
				exception=f'{e}'
			
			print(f'Exception : {e}')
			return render(request,'exception.html',{'exception':exception})
		
	return redirect('youtube')

# download adaptive videos
def adaptive_download(request): 
	# checking whether request.method is post or not 
	if request.method == 'POST':
		
		try :
			filename=request.POST['filename']
			# create temp folder path
			temp_dir_path=os.path.join(settings.BASE_DIR, 'temp')
			
			merged_file_path=os.path.join(temp_dir_path,filename)
			filename=filename[37:]
			quoted_name = urllib.parse.quote(filename)
			print('ok')
			response= FileResponse(open(merged_file_path, 'rb'))
			response['Content-Disposition'] =f"attachment; filename*=utf-8''{quoted_name};"
			# response['Content-Disposition'] = 'attachment; filename="video.mp4"'
			# return response
			print('ok2')
			return response
		except Exception as e:
			print(e)
			return render(request, 'exception.html',{'exception':f'{e}'})

	
	return redirect('youtube')


# @receiver(request_finished)
# def remove_file(sender, **kwargs):
# 	print('request finished')
#   request = kwargs['request']
#   response = kwargs['response']
#   print(f'Request to {request.path} took {response.time} seconds')
#   os.remove('out.mp4')

def exception(request,exception):
	return render(request,'exception.html',{'exception':exception})

def progress_func(stream, chunk, bytes_remaining):
    print(f'{round(100 - (bytes_remaining / stream.filesize * 100),2)}% downloaded')

def stream_data():
    # Generate data in chunks
    for i in range(10):
        yield f"Data chunk {i}\n"
        # Simulate delay between chunks
        time.sleep(1)



