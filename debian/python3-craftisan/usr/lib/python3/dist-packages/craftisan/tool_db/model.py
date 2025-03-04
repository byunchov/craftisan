import json
from typing import List, Optional
# from numpy import round

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
    icon: Mapped[str] = mapped_column(nullable=True)

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
    icon: Mapped[Optional[str]] = mapped_column()
    iconTemplate: Mapped[Optional[str]] = mapped_column()

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
        if not self.toolId or self.tool is None:
            return (None, 'Add tool...', None, None, None)
    
        return self.tool.toToolTableRow()


class Tool(MappedAsDataclass, Base):
    __tablename__ = 'tools'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, default='1000', server_onupdate='')
    # subCategoryId: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('subcategories.id', onupdate="cascade", ondelete='cascade'), default=None)
    subCategoryId: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('subcategories.id', onupdate="cascade", ondelete='cascade'), default=1)
    nTools: Mapped[int] = mapped_column(default=1, server_default='1')
    description: Mapped[str] = mapped_column(default='Tool {id} D{td}')
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
    AriaTool: Mapped[float] = mapped_column(default=30, server_default='30')
    maxCuttingDepth: Mapped[str] = mapped_column(default=str([0]*4), server_default=str([0]*4))
    magdiameter: Mapped[float] = mapped_column(default=0, server_default='0')
    maglength: Mapped[float] = mapped_column(default=0, server_default='0')
    ticknessSaw: Mapped[float] = mapped_column(default=0, server_default='0')
    icon: Mapped[Optional[str]] = mapped_column(default=None)

    subcategory: Mapped['SubCategory'] = relationship(back_populates='tools', default=None)
    pocket: Mapped['Pocket'] = relationship(back_populates='tool', default=None)

    def __str__(self):
        return f"[{self.id}] {self.formatedDescription()}"
        
    def __repr__(self):
        return f"ToolModel[{self.id}]"
    
    def __contains__(self, item):
        return self.id == item
    
    def formatedDescription(self):
        """
<h3>Tool description input formatters:</h3>
<span style="">Tool ID:</span> <i style="color: gold">id, t</i> <br>
<span style="">Tool diameter:</span> <i style="color: gold">td, d(n)</i> <br>
<span style="">Tool Lenght:</span> <i style="color: gold">lt, l(n)</i> <br>
<span style="">Tool Work Depth:</span> <i style="color: gold">i, li(n)</i> <br>
<span style="">Offset Z:</span> <i style="color: gold">ofz</i> <br>
<span style="">Spindle Direction:</span> <i style="color: gold">r, dir(n)</i> <br>
<span style="">Default RPM:</span> <i style="color: gold">rpm</i> <br>
<span style="">Saw Thickness:</span> <i style="color: gold">tk</i> <br>
<span style="">Aggregate LA:</span> <i style="color: gold">la, lax(n)</i>
        """
        try:
            tool_params = {
                'id': self.id,
                't': self.id,
                'td': self.getTipDiameter(),
                'd': self.getDiameters(),
                'lt': self.getTipLT(),
                'l': self.getLengths(),
                'i': self.getTipWorkDepth(),
                'li': self.getWorkDepths(),
                'ofz': self.offsetZ,
                'r': 'L' if self.getTipSpindleDir() else 'R',
                'dir': self.getSpindleDirs(),
                'rpm': self.defaultRPM,
                'tk': self.ticknessSaw,
                'la': self.getTipLA(),
                'lax': self.getTipLA,
            }
            # return self.description.format(**tool_params)
            description = f"f'{self.description}'"
            return eval(description, {}, tool_params)
        except:
            return self.description
    
    def __export_tool(self) -> tuple:
        offsetC = self.getTipCOffset()
        diameter = self.getTipDiameter()

        if self.subCategoryId in (6, 7):
            offsetZ = self.offsetZ
        else:
            offsetZ = self.getTipLT()

        tool_data = (self.id,
                self.pocket.pocketNumber,
                round(diameter, 2),
                round(self.offsetX, 4),
                round(self.offsetY, 4),
                round(offsetZ, 4),
                round(offsetC, 4),
                self.formatedDescription(),
                )        
        return tool_data
     
    def getDiameters(self):
        diameters = json.loads(self.diameter, parse_int=float)
        return diameters
    
    def getLengths(self):
        lengths = json.loads(self.toolLength, parse_int=float)
        return lengths
    
    def getSpindleDirs(self):
        directions = json.loads(self.rotationDirection, parse_int=int)
        return directions
    
    def getXOffsets(self):
        offsets = json.loads(self.correctorX, parse_int=float)
        return offsets
    
    def getYOffsets(self):
        offsets = json.loads(self.correctorY, parse_int=float)
        return offsets
    
    def getCOffsets(self):
        offsets = json.loads(self.angleC, parse_int=float)
        return offsets
    
    def getWorkDepths(self):
        return json.loads(self.maxCuttingDepth, parse_int=float)
    
    def getFulcrumData(self):
        return json.loads(self.correctorZ, parse_int=float)
    
    def setDiameters(self, array):
        self.diameter = json.dumps(array)
    
    def setLengths(self, array):
        self.toolLength = json.dumps(array)
    
    def setSpindleDirs(self, array):
        self.rotationDirection = json.dumps(array)
    
    def setXOffsets(self, array):
        self.correctorX = json.dumps(array)

    def setYOffsets(self, array):
        self.correctorY = json.dumps(array)

    def setCOffsets(self, array):
        self.angleC = json.dumps(array)

    def setWorkDepths(self, array):
        self.maxCuttingDepth = json.dumps(array)

    def setFulcrumData(self, array):
        self.correctorZ = json.dumps(array)

    def __list_getter(self, callback, tip=0):
        elements = callback()

        if isinstance(elements, list):
            element = elements[tip]
        else:
            element = elements

        return element
    
    def __list_setter(self, prop, value, tip=0):
        getter = getattr(self, f"get{prop}", None)        
        if getter is not None:
            data = getter()

        if isinstance(data, list):
            data[tip] = value
        else:
            data = value

        setter = getattr(self, f"set{prop}", None)
        if setter is not None:
            setter(data)
    
    def getTipDiameter(self, tip=0):
        return self.__list_getter(self.getDiameters, tip)
    
    def getTipLT(self, tip=0):
        return self.__list_getter(self.getLengths, tip)
    
    def getTipSpindleDir(self, tip=0):
        return self.__list_getter(self.getSpindleDirs, tip)
    
    def getTipXOffset(self, tip=0):
        return self.__list_getter(self.getXOffsets, tip)
    
    def getTipYOffset(self, tip=0):
        return self.__list_getter(self.getYOffsets, tip)
    
    def getTipCOffset(self, tip=0):
        return self.__list_getter(self.getCOffsets, tip)
    
    def getTipWorkDepth(self, tip=0):
        return self.__list_getter(self.getWorkDepths, tip)
    
    def getTipLA(self, tip=0):
        return self.__list_getter(self.getFulcrumData, tip)
    
    def setTipDiameter(self, value, tip=0):
        self.__list_setter('Diameters', value, tip)

    def setTipLT(self, value, tip=0):
        self.__list_setter('Lengths', value, tip)

    def setTipSpindleDir(self, value, tip=0):
        self.__list_setter('SpindleDirs', value, tip)

    def setTipXOffset(self, offset, tip=0):
        self.__list_setter('XOffsets', offset, tip)

    def setTipYOffset(self, offset, tip=0):
        self.__list_setter('YOffsets', offset, tip)

    def setTipCOffset(self, offset, tip=0):
        self.__list_setter('COffsets', offset, tip)

    def setTipWorkDepth(self, depth, tip=0):
        self.__list_setter('WorkDepths', depth, tip)

    def setTipLA(self, value, tip=0):
        self.__list_setter('FulcrumData', value, tip)
    
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
        diameter = self.getDiameters()

        tool_dia = ', '.join([f"{td:.2f} mm" for td in diameter if td > 0])

        if self.subCategoryId in (6, 7):
            tool_lt = f"{self.offsetZ:.3f} mm"
        else:
            tool_lt = f"{self.getTipLT():.3f} mm"
    
        return (self.id, (self.icon, self.formatedDescription()), tool_dia, tool_lt)
    
    def updateFromDict(self, tool_data: dict) -> None:
        if not tool_data:
            return
        
        self.offsetX = float(tool_data.get('X', 0.0))
        self.offsetY = float(tool_data.get('Y', 0.0))
        offsetZ = float(tool_data.get('Z', 0.0))

        if self.subCategoryId in (6, 7):
            self.offsetZ = offsetZ
        else:
            self.setTipLT(offsetZ)

        self.setTipCOffset(float(tool_data.get('C', 0.0)))
