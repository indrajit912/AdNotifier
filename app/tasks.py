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
from scripts.utils import count_query_occurance, send_telegram_message_by_BOT, get_webpage_sha256, count_query_occurrences_and_hash, get_webpage_sha256_selenium
from config import INDRA_ADNOTIFIER_TELEGRAM_BOT_TOKEN
from scripts.email_message import EmailMessage
from config import EmailConfig
from flask import render_template
from apscheduler.triggers.cron import CronTrigger
from pprint import pprint
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def notify_user(dic:dict):
    """
    Sends email and telegram notification to user!
    Author: Indrajit Ghosh
    Created On: Feb 06, 2024

    Accepts: `dict`
    --------
       dic = {
            'user_email@somewhere.com': {
                'name': "Indrajit Ghosh",
                'telegram': 228394822,
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

            logger.info(f"EMAIL_SENT: An email sent to '{user_email}'!")

        except Exception as e:
            # Handle email sending error
            logger.error(f"TASK_ERR: Error occured while sending emails.\t {e}")

        
        # Send telegram message.
        telegram_user_id = val['telegram']
        if telegram_user_id:
            tel_msg = f"Hello {val['name']}, greetings from AdNotifier!\nThe following ads has some new notifications. Check the corresponding websites!.\n\n Best wishes,\nIndrajit Ghosh\n\n"
            for i, ad in enumerate(val['ads']):
                tel_msg += f"Ad # {i}" + "-" * 15 + "\n"
                tel_msg += f"Adv title: {ad['adv_title']}\n"
                tel_msg += f"Adv number: {ad['adv_num']}\n"
                tel_msg += f"Adv url: {ad['adv_url']}\n"
                tel_msg += "-"*20 + "\n"

            # Send telegram msg
            send_telegram_message_by_BOT(
                bot_token=INDRA_ADNOTIFIER_TELEGRAM_BOT_TOKEN,
                user_id=telegram_user_id,
                message=tel_msg
            )   


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
            ad_prev_hash = ad.page_content_hash
            telegram = (
                ad_user.telegram
                if ad_user.telegram
                else ''
            )

            # Count the occurances
            new_count, current_page_hash = count_query_occurrences_and_hash(url=ad_url, query_str=ad_num)
            logger.debug(f"MonitoredAd id '{ad.id}': `occurance_count` and `webpage_hash` has been calculated.")

            if new_count != ad_prev_count:
                # uncomment - Update the db
                ad.occurrence_count = new_count
                ad.page_content_hash = current_page_hash
                logger.debug(f"MonitoredAd id '{ad.id}': `occurance_count` has been changed from `{ad_prev_count}` to `{new_count}` on the website!")
                
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
                            'telegram': telegram,
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
            else:
                logger.debug(f"MonitoredAd id '{ad.id}': `occurance_count` didn't change so checking the current website hash ...")

                if current_page_hash != ad_prev_hash:
                    # Update the db
                    ad.page_content_hash = current_page_hash
                    ad.last_updated = datetime.utcnow()
                    logger.debug(f"MonitoredAd id '{ad.id}': `occurance_count` didn't change. Current hash has changed from `{ad_prev_hash}` to `{current_page_hash}`.")
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
                                'telegram': telegram,
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

            # Email the user.
            notify_user(email_listing)
            logger.info("TASK_DONE: User(s) notified!")
            
        else:
            logger.warning("TASK_DONE: No new updates for users found. Hence no email was sent!")

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
            

def main():
    check_adv_count()

if __name__ == '__main__':
    main()
    