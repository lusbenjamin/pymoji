"""Script manager for running locally. Gunicorn is used to run the
application on Google App Engine. See entrypoint in app.yaml.
"""
from __future__ import absolute_import, print_function, unicode_literals
import os

from flask_script import Manager

from pymoji.app import app, RESOURCES
from pymoji import faces, process_folder


manager = Manager(app)


@manager.command
def runface(input_image=None, output_image=None):
    """Processes faces in the specified image.

    Args:
        input_image: name of image resource file to process faces in.
        output_image: name of output file to write modified image to. (optional)
    """
    input_path = os.path.join(RESOURCES, input_image)

    if output_image:
        output_path = os.path.join(RESOURCES, output_image)
    else:
        output_path = process_folder.generate_output_path(input_image)

    faces.main(input_path, output_path)


@manager.command
def runfolder(directory=None):
    """Processes images in the specified directory.

    Args:
        directory: path to directory to process images in.
    """
    process_folder.process_folder(directory)


if __name__ == "__main__":
    manager.run()
