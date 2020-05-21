import os
import sys

default = '0'
font_bold = '1'
font_underline = '4'

fg_black = '30'
fg_red = '31'
fg_green = '32'
fg_yellow = '33'
fg_blue = '34'
fg_magenta = '35'
fg_cyan = '36'
fg_white = '37'
fg_gray = fg_bright_black = '90'
fg_pink = fg_bright_red = '91'
fg_bright_green = '92'
fg_bright_yellow = '93'
fg_bright_blue = '94'
fg_bright_magenta = '95'
fg_bright_cyan = '96'
fg_bright_white = '97'

bg_black = '40'
bg_red = '41'
bg_green = '42'
bg_yellow = '43'
bg_blue = '44'
bg_magenta = '45'
bg_cyan = '46'
bg_white = '47'
bg_gray = bg_bright_black = '100'
bg_pink = bg_bright_red = '101'
bg_bright_green = '102'
bg_bright_yellow = '103'
bg_bright_blue = '104'
bg_bright_magenta = '105'
bg_bright_cyan = '106'
bg_bright_white = '107'

CLEAR_NAME = 'cls' if os.name == 'nt' else 'clear'

styles = {}
active_style = 'default'

def cls():
    """Clears the screen, depending on the OS level call, this is merely a small utility function"""
    global CLEAR_NAME
    temp = os.system(CLEAR_NAME)

def _create_style(parameter_list):
    """Formats and translated the provided parameters to an ANSI escape sequence"""
    return "\033[%sm" % ";".join(parameter_list)

def save_style(name, *params):
    """Saves and compiles the provided style parameters under the provided name into a cache"""
    global styles
    styles[name] = _create_style(params)

def reset_style():
    """Resets all styles back to default"""
    set_style("default")

def set_immediate_style(*params):
    """Sets the terminal layout style using comma separated styling arguments"""
    global active_style
    active_style = 'force overwrite'
    save_style("__internal__", *params)
    set_style("__internal__")

def set_style(name):
    """Tries to find the style associated with the name and if it is found tries to apply it immediately"""
    global styles, active_style
    if name in styles:
        if name == active_style: return
        sys.stdout.write(styles[name])
        active_style = name
    else:
        raise KeyError("Style %s was not found to be predefined" % name)

def get_24_bit_fg_color(r, g, b):
    """"Returns the 24 bit color value for the provided RGB values. Note: not all terminals support this"""
    return '38;2;%d;%d;%d' % (r, g, b)

def get_24_bit_bg_color(r, g, b):
    """"Returns the 24 bit color value for the provided RGB values. Note: not all terminals support this"""
    return '48;2;%d;%d;%d' % (r, g, b)

def get_8_bit_fg_color(r, g, b):
    """Returns the color value in the 6x6x6 color space. The other color values are reserved for backwards compatibility"""
    return '38;5;%d' % (16 + 36 * r + 16 * g + b)

def get_8_bit_fg_color(r, g, b):
    """Returns the color value in the 6x6x6 color space. The other color values are reserved for backwards compatibility"""
    return '48;5;%d' % (16 + 36 * r + 16 * g + b)

def get_fg_tone(value):
    """Returns a foreground black-white color in the range 0-24"""
    return '38;5;%d' % (232 + int(value))

def get_bg_tone(value):
    """Returns a foreground black-white color in the range 0-24"""
    return '48;5;%d' % (232 + int(value))

save_style("danger", fg_red, font_bold)
save_style("warning", fg_yellow, font_bold)
save_style("success", fg_green, font_bold)
save_style("default", default)

clear_screen = cls