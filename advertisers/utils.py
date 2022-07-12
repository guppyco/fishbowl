import random
from typing import Dict, Optional, Union

from advertisers.models import Ad, AdSize


def get_ad_from_size(
    width: int, height: int, brand: str = "all"
) -> Optional[Ad]:
    """
    Get ad from the size
    """

    ad_size = None
    filters = {
        "width": width,
        "height": height,
        "is_enabled": True,
        "ads__is_enabled": True,
        "ads__brand__is_enabled": True,
    }  # type: Dict[str, Union[str, int, bool]]
    if brand != "all":
        filters["ads__brand__name"] = brand
    ad_sizes = AdSize.objects.filter(**filters)
    if ad_sizes.count():
        ad_size = ad_sizes.first()
    else:
        ad_size = get_closest_ad_size(width=width, height=height, brand=brand)
    ads_filters = {
        "size": ad_size,
        "is_enabled": True,
        "brand__is_enabled": True,
    }  # type: Dict[str, Union[str, Optional[AdSize], bool]]
    if brand != "all":
        ads_filters["brand__name"] = brand
    ads = Ad.objects.filter(**ads_filters)
    if ads.count():
        # Get random item with correct size
        return random.choice(list(ads))

    return None


def get_closest_ad_size(
    width: int, height: int, brand: str = "all"
) -> Optional[AdSize]:
    """
    Get closest ad size
    """

    filters = {
        "is_enabled": True,
        "ads__is_enabled": True,
        "ads__brand__is_enabled": True,
    }  # type: Dict[str, Union[str, bool]]
    if brand != "all":
        filters["ads__brand__name"] = brand
    ad_sizes = AdSize.objects.filter(**filters)

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
