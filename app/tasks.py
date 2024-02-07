# app/tasks.py
# 
# Author: Indrajit Ghosh
# Created On: Feb 03, 2024
#

"""
This scripts contains the tasks to be performed while the app is running!
"""

from .extensions import scheduler, db
from app.models.user import MonitoredAd, User
from scripts.utils import count_query_occurance
from scripts.email_message import EmailMessage
from config import EmailConfig
from flask import render_template
from apscheduler.triggers.cron import CronTrigger
from pprint import pprint
from datetime import datetime


def send_email(dic:dict):
    """
       dic = {
            'user_email@somewhere.com': {
                'name': "Indrajit Ghosh",
                'ads': [
                    {
                        'adv_url': 'https://wbcsconline.com',
                        'adv_num': 'ADV-83-2020',
                        'adv_title': ad_title,
                        'adv_count': 37 
                    }
                ]
            }
        }
    """
    for user_email, val in dic.items():
        msg_html_str = render_template(
            'all_user_email.html',
            name = val['name'],
            ads = val['ads']
        )

        # Create the email message
        msg = EmailMessage(
            sender_email_id=EmailConfig.INDRAJITS_BOT_EMAIL_ID,
            to=user_email,
            subject="Message from AdNotifier website!",
            email_html_text=msg_html_str,
        )

        try:
            # Send the email to Indrajit
            msg.send(
                sender_email_password=EmailConfig.INDRAJITS_BOT_EMAIL_PASSWD,
                server_info=EmailConfig.GMAIL_SERVER,
                print_success_status=False
            )

            print(f"Email sent to '{user_email}'!")

        except Exception as e:
            # Handle email sending error
            print(f"Error occured during email!\n{e}")

test_dic = {
            'rs_math1902@isibang.ac.in': {
                'name': "Indrajit Office",
                'ads': [
                    {
                        'adv_url': 'https://wbcsconline.com',
                        'adv_num': 'ADV-83-2020',
                        'adv_title': "SOme title",
                        'adv_count': 37 
                    },
                    {
                        'adv_url': 'https://fb.com',
                        'adv_num': 'ADV-8e-2020',
                        'adv_title': "SOme title 2",
                        'adv_count': 0 
                    },
                    {
                        'adv_url': 'https://yobae.com',
                        'adv_num': 'ADV-ew-2020',
                        'adv_title': "SOme title aother",
                        'adv_count': 3 
                    },
                    {
                        'adv_url': 'https://hell.com',
                        'adv_num': 'ADV-83-df',
                        'adv_title': "SOme title aother",
                        'adv_count': -1
                    }
                ]
            },
            'indrajitghosh2014@gmail.com': {
                'name': "Indrajit Office",
                'ads': [
                    {
                        'adv_url': 'https://wbcsconline.com',
                        'adv_num': 'ADV-83-2020',
                        'adv_title': "SOme title",
                        'adv_count': 37 
                    },
                    {
                        'adv_url': 'https://fb.com',
                        'adv_num': 'ADV-8e-2020',
                        'adv_title': "SOme title 2",
                        'adv_count': 0 
                    },
                    {
                        'adv_url': 'https://hell.com',
                        'adv_num': 'ADV-83-df',
                        'adv_title': "SOme title aother",
                        'adv_count': 36
                    }
                ]
            }
        }

def check_adv_count():
    """
    This function counts the occurances of all advertisements in the database
    and if the count changes email the respective user. 
    """
    with scheduler.app.app_context():
        ads = MonitoredAd.query.all()

        email_listing = {}
        
        for ad in ads:
            ad_title = ad.title
            ad_num = ad.advertisement_number
            ad_url = ad.website_url
            ad_user = ad.user
            ad_prev_count = ad.occurrence_count

            # Count the occurances
            new_count = count_query_occurance(url=ad_url, query_str=ad_num)

            if new_count != ad_prev_count:
                # uncomment - Update the db
                ad.occurrence_count = new_count
                ad.last_updated = datetime.utcnow()

                db.session.commit()


                # Add to the dict
                if ad_user.email in email_listing.keys():
                    email_listing[ad_user.email]['ads'].append(
                        {
                            'adv_url': ad_url,
                            'adv_num': ad_num,
                            'adv_title': ad_title,
                            'adv_count': new_count
                        }
                    )
                else:
                    email_listing.setdefault(
                        ad_user.email, {
                            'name': ad_user.fullname,
                            'ads': [
                                {
                                    'adv_url': ad_url,
                                    'adv_num': ad_num,
                                    'adv_title': ad_title,
                                    'adv_count': new_count
                                }
                            ]
                        }
                    )
            
        
        
        if email_listing:
            # Email users
            pprint(email_listing)
            send_email(email_listing)   # Uncomment it!
        else:
            print("\n\nBot: Greetings, Indrajit! I've reviewed all ads, but no alterations were detected in their respective URLs. I'll attempt again in the future.\n\n")



# @scheduler.task(
#     "interval",
#     id="job_sync",
#     seconds=10,
#     max_instances=1,
#     start_date="2000-01-01 12:19:00",
# )
# def task2():
#     """Sample task 2.

#     Added when /add url is visited.
#     """
#     print("running task 2!")  # noqa: T001

# @scheduler.task(id="test", trigger=CronTrigger.from_crontab("12 15 * * *"))
# def test():
#     print("job 1")
            

