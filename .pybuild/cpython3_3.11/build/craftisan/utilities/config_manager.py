from configparser import ConfigParser
import os

config = ConfigParser()

config_file_path = os.path.expanduser('~/.craftisan.ini')
config.read(config_file_path)

DB_FILE_PATH = config['DB']['file_path']
ICON_PATH = config['DB']['icon_path']
TEMPLATE_ICON_PATH = os.path.join(ICON_PATH, config['DB']['template_icon_path'], '{}.png')
TOOL_ICON_PATH = os.path.join(ICON_PATH, config['DB']['tool_icon_path'])
TOOL_ICON_SAVE_PATH = os.path.join(ICON_PATH, config['DB']['tool_icon_path'], config['DB']['tool_icon_name'])