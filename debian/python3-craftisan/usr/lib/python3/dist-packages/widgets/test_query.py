from sqlalchemy import or_, select
from sqlalchemy.orm import aliased
from craftisan.tool_db.model import Tool, Category, Pocket, SubCategory
from craftisan.tool_db.base import Session
from pprint import pprint

session = Session()

# Create aliases for Tool table to use in the subquery
tool_alias = aliased(Tool)
pocket_alias = aliased(Pocket)

# Subquery to find all the tools that have a pocket assigned
subquery = (
    select(Tool.id)
    .join(Pocket, Pocket.toolId == Tool.id)
)

# Query to retrieve Category, SubCategory, and Tool
result = (
    session.query(Category, SubCategory, Tool)
    .join(SubCategory, Category.subcategories)
    .join(Tool, SubCategory.tools)
    .filter(
        or_(
            Tool.id.like('%your_search_string%'),
            Tool.description.like('%your_search_string%'),
            Tool.id.not_in(subquery)
        ),
    )
    .all()
)
result_grouped = {}

# Organize the data into the desired structure
for category, subcategory, tool in result:
    if category.id not in result_grouped:
        result_grouped[category.id] = {
            "id": category.id,
            "displayName": category.fallbackText,
            "icon": None,
            "subcategories": []
        }

    subcategory_entry = {
        "id": subcategory.id,
        "displayName": subcategory.fallbackText,
        "icon": None,
        "tools": [
            {
                "id": tool.id,
                "displayName": str(tool),
                "icon": None,
            }
        ]
    }

    result_grouped[category.id]["subcategories"].append(subcategory_entry)

# Convert the dictionary values (category entries) to a list
category_entries_list = list(result_grouped.values())
pprint(result_grouped)

# Print the result
# for category_entry in category_entries_list:
#     print(category_entry)

# Loop through the result and print the tree view
# for category, subcategory, tool in result:
#     print(f"Category: {category}")
#     print(f"SubCategory: {subcategory}")
#     print(f"Tool: {tool}")


session.close()
