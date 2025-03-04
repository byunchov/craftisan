import json
from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, DeclarativeBase, relationship, mapped_column


class Base(DeclarativeBase):
    pass

association_table = sa.Table(
    'pocket_tool_association',
    Base.metadata,
    sa.Column('pocket_id', sa.Integer, sa.ForeignKey('pockets.id')),
    sa.Column('tool_id', sa.Integer, sa.ForeignKey('tools.id'))
)

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
    categoryId: Mapped[int] = mapped_column(sa.ForeignKey('categories.id', onupdate="cascade"))
    icon: Mapped[bytes] = mapped_column(nullable=True)
    iconTemplate: Mapped[bytes] = mapped_column(nullable=True)

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
    # __table_args__ = (
    #     sa.ForeignKeyConstraint(
    #         ["id", "toolId"],
    #         ["tools.pocketId", "tools.id"],
    #         name="fk_pocket",
    #     ),
    # )

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    pocketNumber: Mapped[int] = mapped_column(unique=True)
    pocketTypeId: Mapped[int] = mapped_column(sa.ForeignKey('pocket_types.id'))
    toolId: Mapped[int] = mapped_column(sa.ForeignKey('tools.id', onupdate="cascade", ondelete='cascade'), nullable=True, unique=True)
    toolChangerId: Mapped[int] = mapped_column(sa.ForeignKey('tool_changers.id', onupdate="cascade"))

    tool: Mapped['Tool'] = relationship(back_populates='pocket', uselist=False)
    pocketType: Mapped['PocketType'] = relationship()
    toolChanger: Mapped['ToolChanger'] =  relationship(back_populates='pockets')

    def __str__(self):
        return f"({self.pocketNumber}) -> {str(self.tool)}"
    
    def __repr__(self):
        # return self.__str__()
        return f"ToolPocketModel[P#{self.pocketNumber}]"


class Tool(Base):
    __tablename__ = 'tools'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    subCategoryId: Mapped[int] = mapped_column(sa.ForeignKey('subcategories.id', onupdate="cascade", ondelete='cascade'), nullable=True)
    pocketId: Mapped[int] = mapped_column(sa.ForeignKey('pockets.id', onupdate="cascade", ondelete='cascade'), nullable=True, unique=True)
    nTools: Mapped[int] = mapped_column(default=1)
    description: Mapped[str] = mapped_column(default='Tool {id}')
    diameter: Mapped[str] = mapped_column(default=str([0]*4))
    angleC: Mapped[str] = mapped_column(default=str([0]*4))
    offsetX: Mapped[float] = mapped_column(default=0)
    offsetY: Mapped[float] = mapped_column(default=0)
    offsetZ: Mapped[float] = mapped_column(default=0)
    correctorX: Mapped[str] = mapped_column(default=str([0]*4))
    correctorY: Mapped[str] = mapped_column(default=str([0]*4))
    correctorZ: Mapped[str] = mapped_column(default=str([0]*4))
    correctorZAria: Mapped[float] = mapped_column(default=0)
    toolLength: Mapped[str] = mapped_column(default=str([0]*4))
    minRPM: Mapped[int] = mapped_column(default=1500)
    maxRPM: Mapped[int] = mapped_column(default=24000)
    defaultRPM: Mapped[int] = mapped_column(default=14000)
    rotationDirection: Mapped[str] = mapped_column()
    defaultWorkFeed: Mapped[int] = mapped_column()
    defaultPenetrationFeed: Mapped[int] = mapped_column()
    waitTime: Mapped[int] = mapped_column(default=0)
    accTime: Mapped[int] = mapped_column(default=4)
    decTime: Mapped[int] = mapped_column(default=4)
    AriaTool: Mapped[float] = mapped_column(default=30)
    maxCuttingDepth: Mapped[str] = mapped_column(default=str([0.0]*6))
    magdiameter: Mapped[float] = mapped_column(default=0)
    maglength: Mapped[float] = mapped_column(default=0)
    ticknessSaw: Mapped[float] = mapped_column(default=0)
    icon: Mapped[bytes] = mapped_column(nullable=True)

    subcategory: Mapped['SubCategory'] = relationship(back_populates='tools')
    pocket: Mapped['Pocket'] = relationship(back_populates='tool', uselist=False, primaryjoin=pocketId == 'Pocket.id')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.id = 1000
        self.description = "Tool"
        self.nTools = 1
        self.diameter = str([0]*4)
        self.angleC = str([0]*4)
        self.offsetX = 0
        self.offsetY = 0
        self.offsetZ = 0
        self.correctorX = str([0]*4)
        self.correctorY = str([0]*4)
        self.correctorZ = str([0]*4)
        self.correctorZAria = 0
        self.toolLength = str([0]*4)
        self.minRPM = 1500
        self.maxRPM = 24000
        self.defaultRPM = 14000
        self.rotationDirection = str([0]*4)
        self.defaultWorkFeed = 2
        self.defaultPenetrationFeed = 2
        self.waitTime = 0
        self.accTime = 4
        self.decTime = 4
        self.AriaTool = 30
        self.maxCuttingDepth = str([0]*4)
        self.magdiameter = 0
        self.maglength = 0
        self.ticknessSaw = 0

    def __str__(self):
        return f"[{self.id}] {self.description}"
        
    def __repr__(self):
        return f"ToolModel[{self.id}]"
    
    def __contains__(self, item):
        return self.id == item
    
    def toToolString(self):
        angleC = json.loads(self.angleC, parse_int=float)
        diameters = json.loads(self.diameter, parse_int=float)

        offsetC = angleC
        if isinstance(angleC, list):
            offsetC = angleC[0]

        diameter = diameters
        if isinstance(diameters, list):
            diameter = diameters[0]

        tool_data = [f"T{self.id}",
                f"P{self.pocket.pocketNumber}",
                f"D{diameter}",
                f"X{self.offsetX}",
                f"Y{self.offsetY}",
                f"Z{self.offsetZ}",
                f"C{offsetC}"
                ]

        return " ".join(tool_data)
