import base64
from io import BytesIO
from os.path import join

from loguru import logger
from PIL import Image


class Drawing:
    save_dir = join("candy", "static", "art")

    def __init__(self, image: Image):
        self.image = image

    def save(self, name: str):
        img_path = join(self.save_dir, name)
        self.image.save(img_path, "PNG")
        logger.info(f"IMAGE SAVED: {img_path}")

    @classmethod
    def from_post_request(cls, img_base_64) -> "Drawing":
        offset = img_base_64.index(",") + 1
        base64_decoded = base64.b64decode(img_base_64[offset:])
        image = Image.open(BytesIO(base64_decoded))
        return cls(image)

    @classmethod
    def load_local(cls, name) -> "Drawing":
        with open(join(cls.save_dir, name), "rb") as f:
            im = Image.open(f)
            return cls(im)
