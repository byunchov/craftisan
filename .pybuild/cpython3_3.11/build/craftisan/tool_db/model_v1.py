import json
from typing import List, Optional
from numpy import round

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, DeclarativeBase, MappedAsDataclass, relationship, mapped_column


class Base(DeclarativeBase):
    pass

# association_table = sa.Table(
#     'pocket_tool_association',
#     Base.metadata,
#     sa.Column('pocket_id', sa.Integer, sa.ForeignKey('pockets.id')),
#     sa.Column('tool_id', sa.Integer, sa.ForeignKey('tools.id'))
# )

class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    displayTag: Mapped[str] = mapped_column(unique=True)
    fallbackText: Mapped[str] = mapped_column()
    icon: Mapped[bytes] = mapped_column(nullable=True)

    subcategories: Mapped[List["SubCategory"]] = relationship(back_populates='category')

    def __str__(self):
        return self.fallbackText
    
    def __repr__(self):
        return f"[{self.id}] Category {self.fallbackText}"
    

class SubCategory(Base):
    __tablename__ = 'subcategories'

    id: Mapped[int] = mapped_column(primary_key=True)
    displayTag: Mapped[str] = mapped_column(unique=True)
    fallbackText: Mapped[str] = mapped_column()
    categoryId: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('categories.id', onupdate="cascade"), nullable=True)
    icon: Mapped[Optional[bytes]] = mapped_column()
    iconTemplate: Mapped[Optional[bytes]] = mapped_column()

    category: Mapped['Category'] = relationship(back_populates='subcategories')
    tools: Mapped[List['Tool']] = relationship(back_populates='subcategory')

    def __str__(self):
        return self.fallbackText
       
    def __repr__(self):
        return f"[{self.id}] Category {self.fallbackText}"


class ToolChanger(Base):
    __tablename__ = 'tool_changers'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, unique=True)
    displayTag: Mapped[str] = mapped_column()
    fallbackText: Mapped[str] = mapped_column()

    # tools = orm.relationship('ToolModel', backref='tc_tools')
    pockets: Mapped[List['Pocket']] = relationship(back_populates='toolChanger')

    def __str__(self):
        return f"[{self.id}] {self.fallbackText}"
    
    def __repr__(self):
        return self.__str__()


class PocketType(Base):
    __tablename__ = 'pocket_types'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    displayTag: Mapped[str] = mapped_column()
    fallbackText: Mapped[str] = mapped_column()

    def __str__(self):
        return f"({self.id}) {self.fallbackText}"
    
    def __repr__(self):
        return self.__str__()


class Pocket(Base):
    __tablename__ = 'pockets'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    pocketNumber: Mapped[int] = mapped_column(unique=True, nullable=False)
    pocketTypeId: Mapped[int] = mapped_column(sa.ForeignKey('pocket_types.id'))
    toolId: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('tools.id', onupdate="cascade", ondelete='cascade'))
    toolChangerId: Mapped[int] = mapped_column(sa.ForeignKey('tool_changers.id', onupdate="cascade"))

    tool: Mapped['Tool'] = relationship(back_populates='pocket')
    pocketType: Mapped['PocketType'] = relationship()
    toolChanger: Mapped['ToolChanger'] =  relationship(back_populates='pockets')

    def __str__(self):
        return f"({self.pocketNumber}) -> {str(self.tool)}"
    
    def __repr__(self):
        # return self.__str__()
        return f"ToolPocketModel[P#{self.pocketNumber}]"
    
    def toTableRow(self) -> tuple:
        if not self.toolId:
            return (None, 'Add tool...', None, None, None)
    
        return self.tool.toToolTableRow()


class Tool(MappedAsDataclass, Base):
    __tablename__ = 'tools'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, default='1000', server_onupdate='')
    subCategoryId: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('subcategories.id', onupdate="cascade", ondelete='cascade'), default=None)
    nTools: Mapped[int] = mapped_column(default=1, server_default='1')
    description: Mapped[str] = mapped_column(default='Tool {id}')
    diameter: Mapped[str] = mapped_column(default=str([0]*4), server_default=str([0]*4))
    angleC: Mapped[str] = mapped_column(default=str([0]*4), server_default=str([0]*4))
    offsetX: Mapped[float] = mapped_column(default=0, server_default='0')
    offsetY: Mapped[float] = mapped_column(default=0, server_default='0')
    offsetZ: Mapped[float] = mapped_column(default=0, server_default='0')
    correctorX: Mapped[str] = mapped_column(default=str([0]*4), server_default=str([0]*4))
    correctorY: Mapped[str] = mapped_column(default=str([0]*4), server_default=str([0]*4))
    correctorZ: Mapped[str] = mapped_column(default=str([0]*4), server_default=str([0]*4))
    correctorZAria: Mapped[float] = mapped_column(default=0, server_default='0')
    toolLength: Mapped[str] = mapped_column(default=str([0]*4), server_default=str([0]*4))
    minRPM: Mapped[int] = mapped_column(default=1500, server_default='1500')
    maxRPM: Mapped[int] = mapped_column(default=24000, server_default='24000')
    defaultRPM: Mapped[int] = mapped_column(default=14000, server_default='14000')
    rotationDirection: Mapped[str] = mapped_column(default=str([0]*4), server_default=str([0]*4))
    defaultWorkFeed: Mapped[int] = mapped_column(default=1000, server_default='1000')
    defaultPenetrationFeed: Mapped[int] = mapped_column(default=1000, server_default='1000')
    waitTime: Mapped[int] = mapped_column(default=0, server_default='0')
    accTime: Mapped[int] = mapped_column(default=4, server_default='4')
    decTime: Mapped[int] = mapped_column(default=4, server_default='4')
    AriaTool: Mapped[float] = mapped_column(default='30')
    maxCuttingDepth: Mapped[str] = mapped_column(default=str([0]*4), server_default=str([0]*4))
    magdiameter: Mapped[float] = mapped_column(default=0, server_default='0')
    maglength: Mapped[float] = mapped_column(default=0, server_default='0')
    ticknessSaw: Mapped[float] = mapped_column(default=0, server_default='0')
    icon: Mapped[Optional[bytes]] = mapped_column(default=None)

    subcategory: Mapped['SubCategory'] = relationship(back_populates='tools', default=None)
    pocket: Mapped['Pocket'] = relationship(back_populates='tool', default=None)

    def __str__(self):
        return f"[{self.id}] {self.description}"
        
    def __repr__(self):
        return f"ToolModel[{self.id}]"
    
    def __contains__(self, item):
        return self.id == item
    
    def __export_tool(self) -> tuple:
        angleC = json.loads(self.angleC, parse_int=float)
        diameters = json.loads(self.diameter, parse_int=float)

        offsetC = angleC
        if isinstance(angleC, list):
            offsetC = angleC[0]

        diameter = diameters
        if isinstance(diameters, list):
            diameter = diameters[0]

        tool_data = (self.id,
                self.pocket.pocketNumber,
                round(diameter, 2),
                round(self.offsetX, 4),
                round(self.offsetY, 4),
                round(self.offsetZ, 4),
                round(offsetC, 4),
                self.description,
                )
        
        return tool_data
    
    def toToolString(self) -> str:        
        columns = 'TPDXYZC'
        tool_data = self.__export_tool()
        tokens = [f"{kv[0]}{kv[1]}" for kv in zip(columns, tool_data)]

        return " ".join(tokens)
    
    def toTableDict(self) -> dict:
        columns = 'TPDXYZCR'
        tool_data = self.__export_tool()

        return dict(zip(columns, tool_data))
    
    def toToolTableRow(self) -> tuple:
        diameter = json.loads(self.diameter, parse_int=float)

        if isinstance(diameter, list):
            tool_dia = ', '.join([f"{td:.2f} mm" for td in diameter if td > 0])
        else:
            tool_dia = f"{diameter:.2f} mm"

        tool_lt = f"{self.offsetZ:.3f} mm"
    
        return (self.id, (self.icon, self.description), tool_dia, tool_lt)
    
    def updateFromDict(self, tool_data: dict) -> None:
        if not tool_data:
            return
        
        self.offsetX = float(tool_data.get('X', 0.0))
        self.offsetY = float(tool_data.get('Y', 0.0))
        self.offsetZ = float(tool_data.get('Z', 0.0))
        self.angleC = float(tool_data.get('C', 0.0))
