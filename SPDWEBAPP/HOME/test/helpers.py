"""Small HOME-only real image/HTML fixtures, not a parallel test harness."""
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from HOME.models import BannerImage, RushFormLink, RushSlide


def image_bytes(color="red"):
    output = BytesIO()
    Image.new("RGB", (3, 2), color).save(output, format="PNG")
    return output.getvalue()


def upload(name="fixture.png", color="red"):
    return SimpleUploadedFile(name, image_bytes(color), content_type="image/png")


def slide(caption="Fixture slide", order=0):
    return RushSlide.objects.create(caption=caption, order=order, image=upload())


def content():
    return (
        BannerImage.objects.create(image=upload("banner.png")),
        RushFormLink.objects.create(link="https://example.invalid/rush"),
        slide(),
    )


def file_path(field):
    return Path(settings.MEDIA_ROOT) / field.name


class HTML(HTMLParser):
    def __init__(self, response):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.text = []
        self.feed(response.content.decode())

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)

    def attrs(self, tag):
        return [attrs for found, attrs in self.tags if found == tag]
