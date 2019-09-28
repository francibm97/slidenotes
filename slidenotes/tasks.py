from os.path import basename, join
from datetime import datetime

from slidenotes import celery, admin_db
from slidenotes.models_admin import Conversion
from slidenotes.gs.slide_convert import SlideConvert

class TaskUpdateProgress:

    def __init__(self, task):
        self.task = task

    def progress(self, percentage):
        self.task.update_state(state="PROCESSING", meta={"progress": percentage})

@celery.task(bind=True)
def generate_pdf(self, filename, original_layout, options):
    filename = basename(SlideConvert(TaskUpdateProgress(self)).convert(join(celery.upload_folder, filename), original_layout, options))
    conversion = Conversion.query.get(self.request.id)
    conversion.timestamp_processed = datetime.utcnow()
    admin_db.session.commit()
    return {'filename': filename, 'progress': 100}
