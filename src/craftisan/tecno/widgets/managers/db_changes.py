from PyQt5.QtCore import pyqtSignal, QObject
from craftisan.tool_db.base import Session
from craftisan.tool_db.model import Tool, SubCategory
from craftisan.tool_db.queries import getToolById

class DBChangeManager(QObject):
    listChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.to_save: dict[int, Tool] = dict()
        self.to_remove = set()
        self.session = Session()

        self.listChanged.emit(False)
        # self.listChanged.connect(lambda x: print(f"DBChangeManager.listChanged: {x}"))

    def isNotEmpty(self):
        return (bool(self.to_save) or bool(self.to_remove))

    def saveItem(self, item: Tool):
        if item.id in self.to_remove:
            self.to_remove.pop()
            try:
                self.to_remove.remove(item.id)
            except Exception as e:
                print(e)
        
        self.to_save[item.id] = item
        self.listChanged.emit(self.isNotEmpty())
    
    def removeItem(self, item: int):
        if item in self.to_save:
            try:
                self.to_save.pop(item)
            except Exception as e:
                print(e)
        
        self.to_remove.add(item)
        self.listChanged.emit(self.isNotEmpty())
    
    def clearState(self):
        self.to_save.clear()
        self.to_remove.clear()
        self.listChanged.emit(self.isNotEmpty())

    def commitChanges(self):
        with Session() as session:
            subcat_dict = {sub.id: sub for sub in session.query(SubCategory).all()}

            if self.to_remove:
                session.query(Tool).filter(Tool.id.in_(self.to_remove)).delete()

            if self.to_save:
                for tool in self.to_save.values():
                    tool.subcategory = subcat_dict[tool.subCategoryId]
                    session.add(tool)

            if self.to_save or self.to_remove:
                session.commit()
                self.clearState()

    def discardChanges(self):
        self.clearState()

    def validateToolId(self, toolId: int):
        with Session() as session:
            ids = session.query(Tool.id).all()
            tool_ids = set(id[0] for id in ids)

        existing_ids = (self.to_save.keys() | tool_ids) - self.to_remove

        next_id = toolId
        while next_id in existing_ids:
            next_id += 1
        return next_id

    def generateToolId(self, subcatId=None, toolId=None):
        if toolId is not None:
            startId = toolId
        elif subcatId is not None:
            startId = 1 if subcatId in (1, 2) else subcatId*1000
        else:
            startId = 1000
        return self.validateToolId(startId)

    def getToolById(self, toolId):
        if toolId in self.to_save:
            return self.to_save.get(toolId)
        
        return getToolById(toolId)

    def __repr__(self) -> str:
        return f"{self.to_save=}\n{self.to_remove=}"