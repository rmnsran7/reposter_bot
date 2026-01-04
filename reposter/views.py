from django.shortcuts import render
from django.http import JsonResponse
from celery.result import AsyncResult
from .tasks import run_repost

def start_repost(request):
    link = request.GET.get('link')
    if not link: return render(request, 'reposter/process.html', {'error': 'No link'})
    task = run_repost.delay(link)
    return render(request, 'reposter/process.html', {'task_id': task.id, 'link': link})

def get_status(request, task_id):
    res = AsyncResult(task_id)
    return JsonResponse({'state': res.state, 'info': res.info})