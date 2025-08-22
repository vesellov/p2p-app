import os
from kivy.utils import platform

# https://icofont.com/icons
# https://fontawesome.com/v5/search?o=r&m=free
# https://pictogrammers.com/library/mdi/

def font_path(ttf_filename):
    if platform == 'android':
        return os.path.join(os.environ['ANDROID_ARGUMENT'], 'fonts', ttf_filename)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), ttf_filename)
