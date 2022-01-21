import random
from typing import Union

from advertisers.models import Ad, AdSize


def get_ad_from_size(width: int, height: int) -> Union[Ad, None]:
    """
    Get ad from the size
    """

    try:
        ad_size = AdSize.objects.get(width=width, height=height)
    except AdSize.DoesNotExist:
        return None
    ads = Ad.objects.filter(size=ad_size, is_enabled=True)
    if ads.count():
        # Get random item with correct size
        return random.choice(list(ads))

    return None
