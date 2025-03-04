import sqlalchemy as sa
import sqlalchemy.orm as orm
from tree_icons import Icons
from craftisan.utilities.misc import generate_icon
from craftisan.tool_db.base import *
import json
import random

# engine = sa.create_engine('sqlite:////home/cnc/linuxcnc/configs/craftisan_h200/tool_db/tools.db')
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

PARSED_TT_FILE = '/home/cnc/linuxcnc/configs/craftisan_sim/db/export_migration.json'

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

    pockets = dict()

    for p in range(301, 319):
        # tp = ToolPocketModel(pocketNumber=p, pocketType=pocket_types[0], toolId=None, toolChanger=changers[0])
        tp = Pocket(pocketNumber=p, pocketType=pocket_types[0], toolId=None, toolChanger=changers[0])
        pockets[p] = tp
        session.add(tp)
   
    for p in range(401, 411):
        tp = Pocket(pocketNumber=p, pocketType=pocket_types[0 if p==404 else 1], toolId=None, toolChanger=changers[1])
        # tp = ToolPocketModel(pocketNumber=p, pocketType=pocket_types[0 if p==404 else 1], toolId=None, toolChanger=changers[1])
        pockets[p] = tp
        session.add(tp)

    with open(PARSED_TT_FILE, 'r') as f:
        tool_data: dict = json.load(f)

    tools: list[Tool] = []

    for tool in tool_data.values():
        if tool['S'] == 7:
            t = Tool(id=tool['T'], subcategory=subcategories[tool['S']-1], description=tool[';'], offsetZ=tool['Z'])
            t.subCategoryId = tool['S']
        else:
            t = Tool(id=tool['T'], subcategory=subcategories[tool['S']-1], description=tool[';'])
            t.subCategoryId = tool['S']
            t.setTipLT(tool['Z'])
        t.setTipDiameter(tool['D'])
        t.icon = generate_icon(t)

        if tool['P'] > 0:
            pockets[tool['P']].tool = t

        tools.append(t)
    
    session.add_all(tools)

    session.commit()

    ts = session.query(Tool).all()
    for tool in ts:
        print(tool.id, tool.description, tool.diameter, tool.offsetZ)
    # print(tool2.id, tool2.description, tool2.diameter)

