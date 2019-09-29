from os.path import basename, join
from datetime import datetime

from slidenotes import celery, admin_db
from slidenotes.models_admin import Conversion, ConversionOptions
from slidenotes.gs.slide_convert import SlideConvert

class TaskUpdateProgress:

    def __init__(self, task):
        self.task = task

    def progress(self, percentage):
        self.task.update_state(state="PROCESSING", meta={"progress": percentage})

@celery.task(bind=True)
def generate_pdf(self, filename, original_layout, options, client_ua, client_ip):
    options_id = ConversionOptions.get_option_id(original_layout=original_layout, options=options)
    conversion = Conversion(task_id=self.request.id, file_id=filename, client_ua=client_ua, client_ip=client_ip, options_id=options_id)
    admin_db.session.add(conversion)
    admin_db.session.commit()

    filename = basename(SlideConvert(TaskUpdateProgress(self)).convert(join(celery.upload_folder, filename), original_layout, options))

    conversion = Conversion.query.get(self.request.id)
    conversion.duration = (datetime.utcnow() - conversion.timestamp_uploaded).total_seconds()
    admin_db.session.commit()

    return {'filename': filename, 'progress': 100}
