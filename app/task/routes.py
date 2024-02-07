# app/tasks/routes.py
# 
# Author: Indrajit Ghosh
# Created On: Feb 03, 2024
#

from . import task_bp
from app.extensions import scheduler
from app.utils.decorators import admin_required
from app.tasks import check_adv_count
from flask import render_template
import time


@task_bp.route("/schedule")
@admin_required
def schedule():
    """Add a task to the app.

    :url: /task/schedule
    :returns: job
    """
    # Check if the job already exists
    existing_job = scheduler.get_job("check_adv_count_job")

    if existing_job:
        # Job already exists, you can handle this case if needed
        return render_template('schedule_count.html', job=existing_job, formatted_next_run_time=existing_job.next_run_time.strftime("%b %d, %Y %I:%M:%S %p"))

    # Job doesn't exist, so add a new one
    job = scheduler.add_job(
        func=check_adv_count,
        trigger="interval",
        days=2,
        id="check_adv_count_job",
        name="Checking users job notifications ...",
        replace_existing=True,
    )

    # Format next_run_time_ist
    formatted_next_run_time = job.next_run_time.strftime("%b %d, %Y %I:%M:%S %p")

    return render_template('schedule_count.html', job=job, formatted_next_run_time=formatted_next_run_time)


@task_bp.route('/stop')
@admin_required
def stop():
    # Check if the job already exists
    existing_job = scheduler.get_job("check_adv_count_job")
    job_name = existing_job.name
    job_trigger = existing_job.trigger

    time.sleep(1)
    scheduler.remove_job("check_adv_count_job")

    return render_template('job_stopped.html', job_name=job_name, job_trigger=job_trigger)

    
