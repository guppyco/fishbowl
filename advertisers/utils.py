from typing import Union


def get_adsterra_key(width: int, height: int) -> Union[str, None]:
    """
    Get Adsterra key from the size
    """
    adsterra_list = {
        "300x250": "48e6c00c4f6d1487ce256f45fb4c634b",
        "160x300": "f112ed4e140c527981961429de103f25",
    }

    resolution = str(width) + "x" + str(height)
    if resolution in adsterra_list:
        return adsterra_list[resolution]

    return None
