"""Common utility functions."""
from io import BytesIO
import os
import time

import exifread
from google.cloud import storage
from PIL import Image
import requests
from werkzeug.utils import secure_filename

from pymoji.constants import ALLOWED_EXTENSIONS, PROJECT_ID


def shell(cmd):
    """Convenience wrapper function."""
    print(cmd)
    res = os.system(cmd)
    if res:
        raise Exception("Error in script:\n{0}".format(cmd))


def allowed_file(filename):
    """Checks if the given filename matches the allowed extensions.

    http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

    Args:
        filename: a string.

    Result:
        True iff the filename is allowed.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_to_cloud(binary_file, filename, content_type):
    """Saves a binary file to the Google Storage Cloud and returns the new
    public URL.

    https://cloud.google.com/appengine/docs/flexible/python/using-cloud-storage

    Args:
        binary_file: a binary file object with read access
        filename: the desired destination filename
        content_type: MIME content type

    Returns:
        a publicly accessible URL string
    """
    print('Uploading to Google Cloud: {} ...'.format(filename))
    # Create a Cloud Storage client.
    gcs = storage.Client(project=PROJECT_ID)

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(PROJECT_ID)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(filename)

    blob.upload_from_string(
        binary_file.read(),
        content_type=content_type
    )

    print('...upload completed.')
    # The public URL can be used to directly access the uploaded file via HTTP.
    return blob.public_url


def download_image(image_uri):
    """Downloads the image at the given URI and returns it as a PIL.Image.
    Only call this on trusted URIs.

    http://pillow.readthedocs.io/en/4.2.x/reference/Image.html

    Args:
        image_uri: an image uri, e.g. 'http://cdn/path/to/image.jpg'

    Returns:
        a PIL.Image
    """
    print('Downloading source image: {} ...'.format(image_uri))
    response = requests.get(image_uri)
    print('...download completed.')
    return Image.open(BytesIO(response.content))


def orient_image(input_fp, output_fp):
    """Rotates the given image file based on EXIF orientation metadata and
    exports the result to the given destination file.

    https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image

    Args:
        input_fp: an image file-object with EXIF metadata
        output_fp: a file-object to save the result to
    """
    tags = []
    tags = exifread.process_file(input_fp)
    input_fp.seek(0) # Reset the file pointer, so we can read the file again

    image = Image.open(input_fp)
    orientation_key = 'Image Orientation'
    if tags and orientation_key in tags:
        orientation_tag = tags[orientation_key]
        if orientation_tag.values:
            tag_value = orientation_tag.values[0] # assume this for now???
            if tag_value == 3:
                image = image.rotate(180, expand=True)
                print('rotated image 180 degrees')
            elif tag_value == 6:
                image = image.rotate(270, expand=True)
                print('rotated image 270 degrees')
            elif tag_value == 8:
                image = image.rotate(90, expand=True)
                print('rotated image 90 degrees')

    image.save(output_fp)
    image.close()


def get_id_name(filename):
    """Makes a safe, unique-ish filename based on the given input filename.

    Args:
        input_filename: a filname string, e.g. "face-input.jpg"

    Returns:
        a unique-ish filename string, e.g. "1503280514351_face-input.jpg"
    """
    timestamp = int(round(time.time() * 1000))
    return str(timestamp) + '_' + secure_filename(filename)


def get_output_name(input_filename):
    """Makes an output filename based on the given input filename.

    Args:
        input_filename: a filname string, e.g. "face-input.jpg"

    Returns:
        a filename string, e.g. "face-input-output.jpg"
    """
    filename = input_filename.split('.')[-2]
    extension = input_filename.split('.')[-1]
    return filename + "-output." + extension


def process_folder(path, file_processor):
    """Runs the given file processing operation on each image in
    the given directory.

    Args:
        path: a directory path string
        file_processor: a function(input_path) to run on each image
    """
    print('processing directory {} ...'.format(path))
    for file_name in os.listdir(path):
        print('processing file {} ...'.format(file_name))
        file_path = os.path.join(path, file_name)

        if os.path.isfile(file_path) and allowed_file(file_name):
            try:
                file_processor(file_path)
            except IOError as error:
                print('bad image: %s' % error)
        else:
            print('skipped non-image file')
