import os

from PIL import Image

from pymoji.faces import main
from pymoji.app import RESOURCES, OUTPUT_DIR


def test_main(tmpdir):
    out_file = os.path.join(OUTPUT_DIR, 'face-output.jpg')
    in_file = os.path.join(RESOURCES, 'face-input.jpg')

    # Make sure there isn't already a green box
    im = Image.open(in_file)
    pixels = im.getdata()
    unnatural_face_yellow = sum(1 for (r, g, b) in pixels if r == 251 and g == 200 and b == 83)
    assert unnatural_face_yellow < 1

    main(in_file, out_file)

    # Make sure there now is some green drawn
    im = Image.open(out_file)
    pixels = im.getdata()
    unnatural_face_yellow = sum(1 for (r, g, b) in pixels if r == 251 and g == 200 and b == 83)
    assert unnatural_face_yellow > 10
