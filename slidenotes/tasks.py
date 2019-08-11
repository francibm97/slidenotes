from os.path import basename, join

from slidenotes import celery
from slidenotes.gs.slide_convert import SlideConvert

class TaskUpdateProgress:

    def __init__(self, task):
        self.task = task

    def progress(self, percentage):
        self.task.update_state(state="PROCESSING", meta={"progress": percentage})

@celery.task(bind=True)
def generate_pdf(self, filename, original_layout, options):
    return {'filename': basename(SlideConvert(TaskUpdateProgress(self)).convert(join(celery.upload_folder, filename), original_layout, options)), 'progress': 100}
