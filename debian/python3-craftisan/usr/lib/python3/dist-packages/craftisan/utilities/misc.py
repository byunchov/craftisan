import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json

from craftisan.tool_db.model import Tool, SubCategory
from craftisan.utilities.config_manager import TOOL_ICON_SAVE_PATH, TEMPLATE_ICON_PATH

SUBCAT_TAGS = {
    1: 'blind_drills',
    2: 'through_drills',
    3: 'cutters_routers',
    4: 'profiled_routers',
    5: 'multi_profile_routers',
    6: 'tilting_aggregates',
    7: 'hor12_aggregates',
    8: 'saw_aggregates'
}

TEMPLATE_TAGS = {
    1: 'blind_drill',
    2: 'through_drill',
    3: 'cutters_router',
    4: 'profiled_router',
    5: 'multi_profile_router',
    6: 'tilting_aggregate',
    7: 'hor12_aggregate',
    8: 'saw_aggregate'
}

def generate_icon(tool: Tool = None, icon_size=(128, 128)):
    if tool is None:
        return

    subcategory_tag: str = TEMPLATE_TAGS.get(tool.subCategoryId, 'cutters_router')

    if subcategory_tag is None:
        return
    
    image_path = TEMPLATE_ICON_PATH.format(subcategory_tag)

    if image_path:
        icon = Image.open(image_path)
        icon.thumbnail(icon_size)
    else:
        icon = Image.new('RGB', icon_size, color='white')

    draw = ImageDraw.Draw(icon)

    subcategory: str = SUBCAT_TAGS.get(tool.subCategoryId, 'cutters_routers')

    diameter = tool.getDiameters()

    if isinstance(diameter, list):
        index = np.argmax(diameter)
        radius = int(diameter[index] + 0.5)
    else:
        index = 0
        radius = int(diameter + 0.5)

    rotation_direction = 'L' if bool(tool.getTipSpindleDir(index)) else 'R'
    text = f"{radius}\n{rotation_direction}"
    text_coords = (91, 60)
    font_size = 24
    stroke_width = 1
    
    if subcategory in ('tilting_aggregates', 'hor12_aggregates'):
        text_coords = (91, 44)
        font_size = 22
    elif subcategory == 'saw_aggregates':
        text_coords = (25, 101)
        text = f"ф {radius} {rotation_direction}"
        font_size = 20
        stroke_width = 0

    font = ImageFont.truetype('LiberationSans-Regular.ttf', font_size)
    draw.text(text_coords, text, font=font, align='center', fill='black', stroke_width=stroke_width)

    save_path = TOOL_ICON_SAVE_PATH.format(tid=tool.id)
    icon.save(save_path, format='PNG')
    return save_path


def generate_icon_v1(tool: Tool = None, icon_size=(128, 128)):
    if tool is None:
        return

    subcategory_obj: SubCategory = tool.subcategory

    if subcategory_obj is None:
        return
    
    image_bytes = subcategory_obj.iconTemplate

    if image_bytes:
        image_stream = io.BytesIO(image_bytes)
        icon = Image.open(image_stream)
        icon.thumbnail(icon_size)
    else:
        icon = Image.new('RGB', icon_size, color='white')

    draw = ImageDraw.Draw(icon)

    subcategory: str = subcategory_obj.displayTag

    diameter = json.loads(tool.diameter, parse_int=float)

    if isinstance(diameter, list):
        index = np.argmax(tool.diameter)
        radius = int(diameter[index] + 0.5)
    else:
        radius = int(diameter + 0.5)

    rotation_direction = 'L' if bool(tool.rotationDirection[index]) else 'R'
    text = f"{radius}\n{rotation_direction}"
    text_coords = (92, 60)
    font_size = 24
    stroke_width = 1
    
    if subcategory in ('tilting_aggregates', 'hor12_aggregates'):
        text_coords = (91, 44)
        font_size = 22
    elif subcategory == 'saw_aggregates':
        text_coords = (25, 101)
        lt = json.loads(tool.toolLength, parse_int=float)

        if isinstance(lt, list):
            radius = int(lt[index] + 0.5)
        else:
            radius = int(lt + 0.5)
            
        rotation_direction = 'L' if bool(tool.rotationDirection[0]) else 'R'
        text = f"ф {radius} {rotation_direction}"
        font_size = 20
        stroke_width = 0

    font = ImageFont.truetype('LiberationSans-Regular.ttf', font_size)
    draw.text(text_coords, text, font=font, align='center', fill='black', stroke_width=stroke_width)

    # Convert the image to bytes
    icon_bytes = io.BytesIO()
    icon.save(icon_bytes, format='PNG')
    icon_bytes.seek(0)
    img_bytes = icon_bytes.read()

    return img_bytes
