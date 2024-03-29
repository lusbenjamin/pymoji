"""Initializes and configures the Emojivision web app."""
import logging

from flask import Flask
import google.cloud.logging

import config


# initialize Flask app singleton
APP = Flask(__name__)

# load default configuration settings
APP.config.from_object(config)

# Note: avoid instance_relative_config if possible, it breaks non-Flask packages
# NOT RECOMMENDED http://flask.pocoo.org/docs/0.12/config/#instance-folders

# override with custom instance settings if available
APP.config.from_envvar('PYMOJI_SETTINGS', silent=True)

# convenience references for other modules to import
FACE_PAD = APP.config.get('FACE_PAD', 0.05)
MAX_RESULTS = APP.config.get('MAX_RESULTS', 20)
USE_GVA_LABELS = APP.config.get('USE_GVA_LABELS', False)
PROJECT_ID = APP.config['PROJECT_ID']

# Configure logging
if not APP.testing:
    LOGGER = google.cloud.logging.Client(project=PROJECT_ID)
    # Attaches a Google Stackdriver logging handler to the root logger
    LOGGER.setup_logging(logging.INFO)
