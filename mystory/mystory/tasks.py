from __future__ import absolute_import, unicode_literals
from celery import shared_task
from recording.models import Session
from datetime import datetime, timedelta
import os
import glob
import subprocess
from mystory.settings import BASE_DIR
import pytz

@shared_task
def pollSession():
    print "Polling sessions"
    last25seconds = (datetime.utcnow() - timedelta(seconds=25)).replace(tzinfo=pytz.utc)
    sessions = Session.objects.filter(isActive=True).exclude(pages__actionEvents__timestamp__gte=last25seconds)
    for session in sessions:
        session.isActive = False
        session.save()
        process.delay(session.generatePythonFileContents(), session.id)


@shared_task
def process(instructions, sessionId):
    subprocess.call(['docker', 'run', '-d', '--name=grid', '-p', '4444:24444', '-p' '5900:25900', '-e', 'TZ="US/Pacific"',
                        '-v', '/dev/shm:/dev/shm', '-v', '/Users/nfahrenr/Documents/takeout/MyStory/mystory/static/videos/:/videos',
                        '-v', '/Users/nfahrenr/Documents/takeout/MyStory/mystory/static/sites/:/sites', '-e', 'VIDEO=true', '-e', 'VNC_PASSWORD=no',
                        '--privileged', 'elgalu/selenium'])
    subprocess.call(['docker', 'exec', 'grid', 'wait_all_done', '30s'])
    subprocess.call(['docker', 'exec', 'grid', 'start-video'])
    try:
        path = os.path.join(BASE_DIR, 'static', 'videos', sessionId + '.py')
        with open(path, 'w') as f:
            f.write(instructions)        
        subprocess.call(['python', path])
        os.remove(path)
    except:
        pass
    subprocess.call(['docker', 'exec', 'grid', 'stop-video'])
    subprocess.call(['docker', 'cp', 'grid:/videos/.', os.path.join(BASE_DIR, 'static', 'videos')])
    subprocess.call(['docker', 'exec', 'grid', 'stop'])
    subprocess.call(['docker', 'stop', 'grid'])
    subprocess.call(['docker', 'rm', '-v', 'grid'])
    session = Session.objects.get(id=sessionId)
    session.isProcessed = True
    try:
        session.filename = max(glob.iglob('*.[Mm][Pp]4'), key=os.path.getctime)
    except:
        pass
    session.save()