from __future__ import absolute_import, unicode_literals
from celery import shared_task
from recording.models import Session
from datetime import datetime, timedelta
import os
import glob

@shared_task
def checkForSessionEnd():
    print "Polling sessions"
    last25seconds = datetime.now() - timedelta(seconds=25)
    sessions = Session.objects.filter(isActive=True).exclude(pages__actionEvents__timestamp__gte=last25seconds)
    for session in sessions:
        session.isActive = False
        session.save()
        process.delay(session.generatePythonFileContents(), session.id)


@shared_task
def process(instructions, id):
    eval(instructions)
    session = Session.objects.get(id=id)
    session.isProcessed = True
    session.filename = max(glob.iglob('*.[Mm][Pp]4'), key=os.path.getctime)
    session.save()