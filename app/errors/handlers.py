# Error Handlers for the site
# Author: Indrajit Ghosh
# Created On: Feb 22, 2024

from . import errors_bp
from flask import render_template, abort
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, Unauthorized, Forbidden, \
    TooManyRequests


@errors_bp.route('/<error_code>')
def simulate_error(error_code):
    # Convert the error code to an integer
    error_code = int(error_code)

    # Raise an exception with the desired status code
    if error_code == 404:
        raise NotFound("Simulated 404 error")
    elif error_code == 500:
        raise InternalServerError("Simulated 500 error")
    elif error_code == 400:
        raise BadRequest("Simulated 400 error")
    elif error_code == 401:
        raise Unauthorized("Simulated 401 error")
    elif error_code == 403:
        raise Forbidden("Simulated 403 error")
    elif error_code == 429:
        raise TooManyRequests("Simulated 429 error")
    else:
        # You might want to handle other error codes accordingly
        raise Exception(f"Simulated error with code {error_code}")


##########################################
#        Page not found!
##########################################
@errors_bp.app_errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


##########################################
#        Internal Server Error!
##########################################
@errors_bp.app_errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 500


##########################################
#        Unauthorize!
##########################################
@errors_bp.app_errorhandler(401)
def unauthorized(error):
    """
    Handle cases where users attempt to access a resource that 
    requires authentication but are not authorized to do so.
    """
    return render_template('errors/401.html'), 401


##########################################
#        Bad request!
##########################################
@errors_bp.app_errorhandler(400)
def bad_request(error):
    """
    Handle cases where the user's request is malformed or incorrect.
    """
    return render_template('errors/400.html'), 400


##########################################
#        Forbidden!
##########################################
@errors_bp.app_errorhandler(403)
def forbidden(error):
    """
    Handle cases where users attempt to access a resource they 
    don't have permission to access
    """
    return render_template('errors/403.html'), 403


##########################################
#        Too many requests!
##########################################
@errors_bp.app_errorhandler(429)
def too_many_requests(error):
    """
    Handle cases where a user has exceeded a rate limit for making requests.
    """
    return render_template('errors/429.html'), 429