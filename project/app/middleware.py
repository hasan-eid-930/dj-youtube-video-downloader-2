import asyncio
import os
from pathlib import Path
import time

from django.http import HttpRequest
BASE_DIR = Path(__file__).resolve().parent.parent

from threading import Thread
from django.utils.cache import patch_vary_headers



import threading
import time
from django.utils.decorators import async_only_middleware

in_progress_requests = {}

@ async_only_middleware
def cancel_previous_request(get_response):
    if asyncio.iscoroutinefunction(get_response):
         print('coro')
    async def middleware(request:HttpRequest):
        if request.path == '/':
            # Get the client's unique id (e.g., session key, IP address)
            client_id = request.session.session_key or request.META.get('REMOTE_ADDR')
            # Cancel any previous request from the same client
            if client_id in in_progress_requests:
                previous_thread = in_progress_requests[client_id]
                print('exist in progress')
            #     previous_task.cancel()
            
            # Create a new task for the current request
                
            thread =threading.Thread(get_response,args=(request,))
        
            in_progress_requests[client_id] = thread
            thread.start()
            # Wait for the request to complete
            try:
                response=thread.join()
            except asyncio.CancelledError:
                print('rejected from middleware')
                pass



            # # Remove the request from the in_progress_requests dictionary
            # del in_progress_requests[client_id]

            response =await get_response(request)
            return response
        
        # else:
        response =await get_response(request)

        return response

    return middleware

def remove_file_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        print(request.path)

        response = get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        if request.path == '/adaptive-download/':
        # if request.path == '/':
            if response.status_code == 200:

                # # get filename returned using fileResponse
                # filename = response.get('Content-Disposition').split('filename=')[1]
                # # how to remove ' from '"filename"'
                # filename = filename.strip('"')
                # print(filename)
                
                with os.scandir('temp') as entries:
                    for entry in entries:
                        if entry.is_file():
                            # print(entry.name)
                            file_path=os.path.join(os.path.join(BASE_DIR,'temp'),entry.name)
                            # get the last access time of a file
                            file_access_time = os.path.getatime(file_path)
                            if time.time() - file_access_time >7*24*60*60:
                            # if time.time() - file_access_time > 24*60*60:
                                print(time.time() - file_access_time)
                                os.remove(file_path)
       
       
        return response

    return middleware