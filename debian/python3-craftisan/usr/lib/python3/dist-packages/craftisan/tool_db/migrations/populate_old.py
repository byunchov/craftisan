import sqlalchemy as sa
import sqlalchemy.orm as orm
from tree_icons import Icons
from craftisan.utilities.misc import generate_icon
from craftisan.tool_db.base import *
import json
import random

engine = sa.create_engine('sqlite:///tools.db')
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

cat_tags = (
    ('drills', ('blind_drills', 'through_drills')), 
    ('routers', ('cutters_routers', 'profiled_routers', 'multi_profile_routers')), 
    ('aggregates', ('tilting_aggregates', 'hor12_aggregates', 'saw_aggregates'))
)

cat_display_text = (
    ('Бургии', ('Глухо пробиване', 'Проходно пробиване')), 
    ('Фрези', ('Фрезери', 'Профилни', 'Многопрофилни')), 
    ('Агрегати', ('Наклоняеми', 'Хоризонтални с 1/2 извода', 'Триони'))
)

tc_tags = ('rotary', 'linear')
tc_display_text = ('Ротационен магазин', 'Линеен магазин')

pt_tags = ('univerasl', 'router')
pt_display_text = ('Универсален', 'Фрези')

with orm.Session(engine) as session:

    categories = []
    subcategories = []

    for ct, cd in zip(cat_tags, cat_display_text):
        category = Category(displayTag=ct[0], fallbackText=cd[0], icon=Icons[ct[0]])
        categories.append(category)

        for ind, val in enumerate(ct[1]):
            subcat = SubCategory(displayTag=val, fallbackText=cd[1][ind], icon=Icons[val], iconTemplate=Icons[val[:-1]], category=category)
            subcategories.append(subcat)

    session.add_all(categories)
    session.add_all(subcategories)

    changers = []
    for tct, tcd in zip(tc_tags, tc_display_text):
        tcm = ToolChanger(displayTag=f"{tct}_tc", fallbackText=tcd)
        changers.append(tcm)

    session.add_all(changers)

    pocket_types = []
    for ptt, ptd in zip(pt_tags, pt_display_text):
        ptm = PocketType(displayTag=f"{ptt}_tc", fallbackText=ptd)
        pocket_types.append(ptm)

    session.add_all(pocket_types)

    for p in range(301, 319):
        # tp = ToolPocketModel(pocketNumber=p, pocketType=pocket_types[0], toolId=None, toolChanger=changers[0])
        tp = Pocket(pocketNumber=p, pocketType=pocket_types[0], toolId=None, toolChanger=changers[0])

        session.add(tp)
   
    for p in range(401, 411):
        tp = Pocket(pocketNumber=p, pocketType=pocket_types[0 if p==404 else 1], toolId=None, toolChanger=changers[1])
        # tp = ToolPocketModel(pocketNumber=p, pocketType=pocket_types[0 if p==404 else 1], toolId=None, toolChanger=changers[1])
        session.add(tp)

    tools: list[Tool] = []

    tools.append(Tool(id=1, subcategory = subcategories[1], description = "Through Drill D6 mm"))
    tools.append(Tool(id=2, subcategory = subcategories[0], description = "Blind Drill D4 mm"))
    tools.append(Tool(id=2201, subcategory = subcategories[2], description = "Спирален фрезер Z4 D20 mm"))
    tools.append(Tool(id=4001, subcategory = subcategories[3], description = "Фрезова глава за табли"))
    tools.append(Tool(id=5002, subcategory = subcategories[4], description = "Двоен радиус R3/R2"))
    tools.append(Tool(id=6001, subcategory = subcategories[5], description = "Агрегат 45* Z3 D16 mm"))
    tools.append(Tool(id=7005, subcategory = subcategories[6], description = "Агрегат за брави D16/D8 mm"))
    tools.append(Tool(id=8007, subcategory = subcategories[7], description = "Агрегат с трион 45* D180 mm"))

    tl = [0]*4

    for tool in tools:
        n = tool.id / 1000
        if n == 8:
            tl[0] = random.randint(120, 180)
            tool.toolLength = json.dumps(tl)
        else:
            tl[0] = random.randint(6, 50)
            tool.diameter = json.dumps(tl)

        tool.offsetZ = round(random.uniform(125, 215), 3)
        tool.icon = generate_icon(tool)

    session.add_all(tools)

    session.commit()

    ts = session.query(Tool).all()
    for tool in ts:
        print(tool.id, tool.description, tool.diameter, tool.offsetZ)
    # print(tool2.id, tool2.description, tool2.diameter)

