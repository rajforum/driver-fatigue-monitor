from flask import redirect, url_for
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers for the app"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error: {error}")
        return redirect(url_for('ui_screen.home'))

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        return redirect(url_for('ui_screen.home'))

    @app.errorhandler(401)
    def unauthorized_error(error):
        logger.warning(f"401 error: {error}")
        return redirect(url_for('google_auth.login'))

    @app.errorhandler(403)
    def forbidden_error(error):
        logger.warning(f"403 error: {error}")
        return redirect(url_for('ui_screen.home')) 