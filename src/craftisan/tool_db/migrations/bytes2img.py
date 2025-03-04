from tree_icons import Icons
import io
from PIL import Image
from pprint import pprint
from craftisan.utilities.config_manager import ICON_PATH, TEMPLATE_ICON_PATH

export_path = f'{ICON_PATH}/categories'
icon_size = (128,)*2

icons = {}

for icon_name, raw_data in Icons.items():
    image_stream = io.BytesIO(raw_data)
    icon = Image.open(image_stream)
    icon.thumbnail(icon_size)
    if icon_name.endswith('s'):
        file_path = f"{export_path}/{icon_name}.png"
    else:
        file_path = f"{TEMPLATE_ICON_PATH}/{icon_name}.png"

    icon.save(file_path, format='PNG')

    icons[icon_name] = file_path

    print(file_path)

with open('tree_icons_v2.py', 'w+') as f:
    pprint(icons, f, sort_dicts=False)