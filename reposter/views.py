"""
Views for the InstaReposter application.
Synchronous processing - no Celery required.
"""
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import process_instagram_repost


def index(request):
    """Render the main page with the Instagram URL submission form."""
    return render(request, 'reposter/index.html')


@csrf_exempt
def submit_url(request):
    """
    Accept an Instagram URL and process it synchronously.
    Returns result directly after completion.
    """
    if request.method != 'POST':
        return redirect('reposter:index')
    
    try:
        data = json.loads(request.body)
        instagram_url = data.get('url', '').strip()
    except json.JSONDecodeError:
        instagram_url = request.POST.get('url', '').strip()
    
    if not instagram_url:
        return JsonResponse({
            'success': False,
            'error': 'Please provide an Instagram URL'
        }, status=400)
    
    # Validate URL (basic check)
    if 'instagram.com' not in instagram_url and 'instagr.am' not in instagram_url:
        return JsonResponse({
            'success': False,
            'error': 'Please provide a valid Instagram URL'
        }, status=400)
    
    # Process synchronously - this will take a while
    try:
        result = process_instagram_repost(instagram_url)
        return JsonResponse({
            'success': True,
            'status': 'Published',
            'media_id': result.get('media_id'),
            'message': 'Successfully published to Instagram!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)