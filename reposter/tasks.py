import os
import yt_dlp
import requests
import time
from celery import shared_task
from django.conf import settings
from django.utils.crypto import get_random_string

@shared_task(bind=True)
def run_repost(self, link):
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    file_id = get_random_string(8)
    file_path = None

    try:
        # 1. Download
        self.update_state(state='PROGRESS', meta={'status': 'Downloading...'})
        ydl_opts = {'outtmpl': f'{temp_dir}/{file_id}.%(ext)s', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_path = f"{temp_dir}/{file_id}.{info['ext']}"
            is_video = info.get('vcodec') != 'none'

        # 2. Container
        self.update_state(state='PROGRESS', meta={'status': 'Uploading to Meta...'})
        public_url = f"https://www.loudsurrey.online/media/temp/{file_id}.{info['ext']}"
        hashtags = "\n\n#surrey #loudsurrey #surreybc #repost"
        
        container_url = f"https://graph.facebook.com/{settings.GRAPH_VERSION}/{settings.IG_BUSINESS_ID}/media"
        payload = {'caption': f"{info.get('description', '')}{hashtags}", 'access_token': settings.ACCESS_TOKEN}
        payload['video_url' if is_video else 'image_url'] = public_url
        if is_video: payload['media_type'] = 'VIDEO'

        resp = requests.post(container_url, data=payload).json()
        container_id = resp.get('id')
        if not container_id: raise Exception(f"Container Error: {resp}")

        # 3. Poll
        for _ in range(20):
            check = requests.get(f"https://graph.facebook.com/{settings.GRAPH_VERSION}/{container_id}", 
                                 params={'fields': 'status_code', 'access_token': settings.ACCESS_TOKEN}).json()
            if check.get('status_code') == 'FINISHED': break
            time.sleep(5)

        # 4. Publish
        publish_url = f"https://graph.facebook.com/{settings.GRAPH_VERSION}/{settings.IG_BUSINESS_ID}/media_publish"
        final = requests.post(publish_url, data={'creation_id': container_id, 'access_token': settings.ACCESS_TOKEN}).json()
        
        if 'id' not in final: raise Exception(f"Publish Error: {final}")
        return {'status': 'Done', 'media_id': final['id']}

    except Exception as e:
        self.update_state(state='FAILURE', meta={'status': str(e)})
        raise e
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)