import re

from django.core.validators import RegexValidator

HEX_COLOR_CODE_RE = re.compile('^#[0-9A-F]{6}$')
color_hex_validator = RegexValidator(
    regex=HEX_COLOR_CODE_RE,
    message='Enter a valid hex color code',
)
