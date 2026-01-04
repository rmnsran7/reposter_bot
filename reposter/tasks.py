"""
Instagram reposting logic.
Synchronous processing - no Celery required.
"""
import os
import time
import yt_dlp
import requests
from django.conf import settings
from django.utils.crypto import get_random_string


def process_instagram_repost(instagram_url):
    """
    Download Instagram media and repost to Instagram Business Account.
    
    Steps:
    1. Download media using yt-dlp
    2. Create media container via Meta Graph API
    3. Poll container status until ready
    4. Publish the media
    5. Cleanup temporary files
    
    Args:
        instagram_url: The Instagram post/reel/video URL to repost
        
    Returns:
        dict with status and media_id on success
        
    Raises:
        Exception on any failure
    """
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    file_id = get_random_string(12)
    file_path = None
    file_extension = None
    
    try:
        # ========== STEP 1: DOWNLOAD MEDIA ==========
        print(f"[InstaReposter] Downloading from {instagram_url}")
        
        ydl_opts = {
            'outtmpl': f'{temp_dir}/{file_id}.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(instagram_url, download=True)
            file_extension = info.get('ext', 'mp4')
            file_path = f"{temp_dir}/{file_id}.{file_extension}"
            
            # Determine if video or image
            is_video = info.get('vcodec') != 'none' and info.get('vcodec') is not None
            
            # Extract caption
            caption = info.get('description', '') or info.get('title', '')
        
        # Verify file exists
        if not os.path.exists(file_path):
            raise Exception(f"Downloaded file not found at {file_path}")
        
        print(f"[InstaReposter] Downloaded: {file_path} (video={is_video})")
        
        # ========== STEP 2: CREATE MEDIA CONTAINER ==========
        print("[InstaReposter] Creating media container...")
        
        # Build the public URL for Meta to fetch the media
        ngrok_url = settings.NGROK_URL
        if not ngrok_url:
            raise Exception(
                "NGROK_URL not configured. Please set NGROK_URL in your .env file. "
                "Run 'ngrok http 8000' and copy the https URL."
            )
        
        public_url = f"{ngrok_url.rstrip('/')}/media/temp/{file_id}.{file_extension}"
        print(f"[InstaReposter] Public URL: {public_url}")
        
        # Build caption with custom text from settings
        full_caption = f"{caption}{settings.CUSTOM_CAPTION}" if caption else settings.CUSTOM_CAPTION.strip()
        
        # Create container request
        container_url = (
            f"https://graph.facebook.com/{settings.GRAPH_VERSION}/"
            f"{settings.IG_BUSINESS_ID}/media"
        )
        
        payload = {
            'caption': full_caption,
            'access_token': settings.ACCESS_TOKEN,
        }
        
        if is_video:
            payload['video_url'] = public_url
            payload['media_type'] = 'REELS'
        else:
            payload['image_url'] = public_url
        
        response = requests.post(container_url, data=payload)
        container_data = response.json()
        
        container_id = container_data.get('id')
        if not container_id:
            error_msg = container_data.get('error', {}).get('message', str(container_data))
            raise Exception(f"Failed to create media container: {error_msg}")
        
        print(f"[InstaReposter] Container created: {container_id}")
        
        # ========== STEP 3: POLL CONTAINER STATUS ==========
        print("[InstaReposter] Waiting for Meta to process media...")
        
        status_url = f"https://graph.facebook.com/{settings.GRAPH_VERSION}/{container_id}"
        max_attempts = 30  # 30 attempts x 10 seconds = 5 minutes max
        
        for attempt in range(max_attempts):
            status_response = requests.get(status_url, params={
                'fields': 'status_code,status',
                'access_token': settings.ACCESS_TOKEN
            })
            status_data = status_response.json()
            
            status_code = status_data.get('status_code')
            print(f"[InstaReposter] Status: {status_code} (attempt {attempt + 1}/{max_attempts})")
            
            if status_code == 'FINISHED':
                break
            elif status_code == 'ERROR':
                error_status = status_data.get('status', 'Unknown error')
                raise Exception(f"Media processing failed: {error_status}")
            elif status_code == 'EXPIRED':
                raise Exception("Media container expired before publishing")
            
            time.sleep(10)
        else:
            raise Exception("Timeout waiting for media to process")
        
        # ========== STEP 4: PUBLISH MEDIA ==========
        print("[InstaReposter] Publishing to Instagram...")
        
        publish_url = (
            f"https://graph.facebook.com/{settings.GRAPH_VERSION}/"
            f"{settings.IG_BUSINESS_ID}/media_publish"
        )
        
        publish_response = requests.post(publish_url, data={
            'creation_id': container_id,
            'access_token': settings.ACCESS_TOKEN
        })
        publish_data = publish_response.json()
        
        media_id = publish_data.get('id')
        if not media_id:
            error_msg = publish_data.get('error', {}).get('message', str(publish_data))
            raise Exception(f"Failed to publish media: {error_msg}")
        
        print(f"[InstaReposter] SUCCESS! Media ID: {media_id}")
        
        return {
            'status': 'Published',
            'media_id': media_id,
        }
    
    finally:
        # ========== STEP 5: CLEANUP ==========
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[InstaReposter] Cleaned up: {file_path}")
            except OSError:
                pass