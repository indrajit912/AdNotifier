# app/tasks/routes.py
# 
# Author: Indrajit Ghosh
# Created On: Feb 03, 2024
#

from . import task_bp
from app.extensions import scheduler
from app.tasks import check_adv_count


@task_bp.route("/add")
def add():
    """Add a task to the app.

    :url: /add/
    :returns: job
    """
    job = scheduler.add_job(
        func=check_adv_count,
        trigger="interval",
        seconds=10,
        id="check_adv_count job",
        name="check_adv_count job",
        replace_existing=True,
    )
    return "%s added!" % job.name