from app.models.user import MonitoredAd
from app.extensions import db
from scripts.utils import get_webpage_sha256
from sqlalchemy.exc import SQLAlchemyError

def update_page_content_hashes():
    """
    Update the page_content_hash for MonitoredAd records with a None value.
    
    This function iterates through MonitoredAd records with a page_content_hash of None,
    calculates the hash using the get_webpage_sha256 function, and updates the records.
    """
    try:
        ads_without_hashes = MonitoredAd.query.filter_by(page_content_hash=None).all()

        for ad in ads_without_hashes:
            ad.page_content_hash = get_webpage_sha256(ad.website_url)

        db.session.commit()
        print("Page content hashes updated successfully.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error updating page content hashes: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
