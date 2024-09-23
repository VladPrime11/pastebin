import shortuuid
from .models import TextBlock


def generate_unique_hash():
    while True:
        hash = shortuuid.ShortUUID().random(length=6)
        if not TextBlock.objects.filter(hash=hash).exists():
            return hash
