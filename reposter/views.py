"""
Views for the InstaReposter application.
Synchronous processing - no Celery required.
"""
import json
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
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


def cookies_page(request):
    """Page to view and update cookies."""
    cookies_file = os.path.join(settings.BASE_DIR, 'cookies.json')
    current_cookies = ''
    
    if os.path.exists(cookies_file):
        with open(cookies_file, 'r') as f:
            current_cookies = f.read()
    
    return render(request, 'reposter/cookies.html', {
        'current_cookies': current_cookies
    })


@csrf_exempt
def save_cookies(request):
    """Save cookies from JSON input."""
    if request.method != 'POST':
        return redirect('reposter:cookies')
    
    try:
        data = json.loads(request.body)
        cookies_json = data.get('cookies', '').strip()
    except json.JSONDecodeError:
        cookies_json = request.POST.get('cookies', '').strip()
    
    if not cookies_json:
        return JsonResponse({
            'success': False,
            'error': 'Please provide cookies JSON'
        }, status=400)
    
    # Validate JSON
    try:
        parsed = json.loads(cookies_json)
        if not isinstance(parsed, list):
            raise ValueError("Cookies must be a JSON array")
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid JSON: {str(e)}'
        }, status=400)
    
    # Save to file
    cookies_file = os.path.join(settings.BASE_DIR, 'cookies.json')
    try:
        with open(cookies_file, 'w') as f:
            f.write(cookies_json)
        return JsonResponse({
            'success': True,
            'message': f'Saved {len(parsed)} cookies successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to save: {str(e)}'
        }, status=500)