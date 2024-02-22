# Error Handlers for the site
# Author: Indrajit Ghosh
# Created On: Feb 22, 2024

from flask import render_template


##########################################
#        Page not found!
##########################################
def page_not_found(error):
    return render_template('errors/404.html'), 404


##########################################
#        Internal Server Error!
##########################################
def internal_server_error(error):
    return render_template('errors/500.html', error=error), 500


##########################################
#        Unauthorize!
##########################################
def unauthorized(error):
    """
    Handle cases where users attempt to access a resource that 
    requires authentication but are not authorized to do so.
    """
    return render_template('errors/401.html'), 401


##########################################
#        Bad request!
##########################################
def bad_request(error):
    """
    Handle cases where the user's request is malformed or incorrect.
    """
    return render_template('errors/400.html'), 400


##########################################
#        Forbidden!
##########################################
def forbidden(error):
    """
    Handle cases where users attempt to access a resource they 
    don't have permission to access
    """
    return render_template('errors/403.html'), 403


##########################################
#        Too many requests!
##########################################
def too_many_requests(error):
    """
    Handle cases where a user has exceeded a rate limit for making requests.
    """
    return render_template('errors/429.html'), 429
