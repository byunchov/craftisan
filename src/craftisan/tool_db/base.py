from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from craftisan.tool_db.model import Base, Tool, Pocket, PocketType, ToolChanger, Category, SubCategory
from craftisan.utilities.config_manager import DB_FILE_PATH

# file_path = r'/home/cnc/Public/craftisan/src/tools.db'
engine = create_engine(f"sqlite:///{DB_FILE_PATH}")
Session = sessionmaker(bind=engine)

# Base = declarative_base()