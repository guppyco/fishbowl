import random
from typing import Optional, Union

from advertisers.models import Ad, AdSize


def get_ad_from_size(width: int, height: int) -> Optional[Ad]:
    """
    Get ad from the size
    """

    ad_size = None
    try:
        # TODO: only get the size that has ads
        ad_size = AdSize.objects.get(width=width, height=height)
    except AdSize.DoesNotExist:
        ad_size = get_closest_ad_size(width=width, height=height)
    ads = Ad.objects.filter(size=ad_size, is_enabled=True)
    if ads.count():
        # Get random item with correct size
        return random.choice(list(ads))

    return None


def get_closest_ad_size(width: int, height: int) -> Optional[AdSize]:
    """
    Get closest ad size
    """

    ad_sizes = AdSize.objects.filter(
        is_enabled=True,
        ads__is_enabled=True,
    )

    for percent in range(5, 31, 5):
        for ad_size in ad_sizes:
            # Return size if width and height are matched
            if width == ad_size.width and height == ad_size.height:
                return ad_size

            width_deviation_rate = (
                abs(width - ad_size.width) * 100 / max(width, ad_size.width)
            )
            height_deviation_rate = (
                abs(height - ad_size.height) * 100 / max(height, ad_size.height)
            )
            # Return size if the deviations are less than 30 percent
            if (
                width_deviation_rate <= percent
                and height_deviation_rate <= percent
            ):
                return ad_size

    # If can not find the size, return the size has the min deviation rate
    min_deviation_rate = 0.0
    matched_image = None
    for ad_size in ad_sizes:
        width_deviation_rate = (
            abs(width - ad_size.width) * 100 / max(width, ad_size.width)
        )
        height_deviation_rate = (
            abs(height - ad_size.height) * 100 / max(height, ad_size.height)
        )
        ratio_deviation_rate = abs(
            (width / height) - (ad_size.width / ad_size.height)
        )
        # Calculate the total
        # with the most important parameter being ratio_deviation_rate
        total_rate = (
            width_deviation_rate
            + height_deviation_rate
            + (ratio_deviation_rate * 150)
        )

        # Return size which have total deviation is minimum
        if min_deviation_rate == 0 or min_deviation_rate > total_rate:
            min_deviation_rate = total_rate
            matched_image = ad_size

    return matched_image


def get_popup_ad() -> Union[Ad, None]:
    """
    Get random popup ad
    """

    ads = Ad.objects.filter(size__isnull=True, is_enabled=True)
    if ads.count():
        # Get random item with correct size
        return random.choice(list(ads))

    return None
