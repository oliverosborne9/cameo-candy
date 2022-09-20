import base64
from io import BytesIO
from os.path import join

from loguru import logger
from PIL import Image


class Drawing:
    """
    Object used to handle and save the image
    sent from the JavaScript Canvas front-end.

    :param image: The Pillow Image instance to save
    """

    # Save images in static folder
    # where they can be served by Flask app
    save_dir = join("candy", "static", "art")

    def __init__(self, image: Image):
        self.image = image

    def save(self, name: str):
        """
        Save image to PNG file.

        :param name: Filename to save image as
        """
        img_path = join(self.save_dir, name)
        self.image.save(img_path, "PNG")
        logger.info(f"IMAGE SAVED: {img_path}")

    @classmethod
    def from_post_request(cls, img_base_64) -> "Drawing":
        """
        Parse posted data from HTTP request into Image object
        and therefore create instance of this Drawing class
        to write the image to file.

        :param img_base_64: imageBase64 component of the request values
            as specified by AJAX request in JavaScript front-end
        """
        # Remove data from before first comma
        offset = img_base_64.index(",") + 1
        base64_decoded = base64.b64decode(img_base_64[offset:])
        image = Image.open(BytesIO(base64_decoded))
        return cls(image)
