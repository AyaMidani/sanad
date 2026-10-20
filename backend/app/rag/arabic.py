import re

# PDF extraction writes "الإجارة" as "اإلجارة":
# the lam and alef after the article "ا" come out swapped.
_SWAPPED_LAM_ALEF = re.compile(r"ا([اأإآ])ل")


def fix_lam_alef(text: str) -> str:
    return _SWAPPED_LAM_ALEF.sub(r"ال\1", text)
