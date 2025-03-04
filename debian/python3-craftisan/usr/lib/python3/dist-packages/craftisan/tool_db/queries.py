from craftisan.tool_db.base import Session
from craftisan.tool_db.model import Tool, Category, SubCategory, Pocket
from sqlalchemy import or_, select
from sqlalchemy.orm import make_transient


def getToolById(toolId: int) -> Tool:
    with Session() as session:
        tool = session.get(Tool, toolId)
        # make_transient(tool)
        # session.expunge(tool)
        return tool

def getUnassignedTools_old(search_query: str = '', assigned_tools: list=None) -> dict:
    with Session() as session:
        assigned_tool_ids = assigned_tools or (
            select(Tool.id)
            .join(Pocket, Pocket.toolId == Tool.id)
        )

        result = (
            session.query(Category, SubCategory, Tool)
            .join(SubCategory, Category.subcategories)
            .join(Tool, SubCategory.tools)
            .filter(
                or_(
                    Tool.id.like(f'%{search_query}%'),
                    Tool.description.like(f'%{search_query}%'),
                ),
                # Tool.id.notin_(subquery),
                Tool.id.notin_(assigned_tool_ids),
            )
            .all()
        )
        result_grouped = {}

        for category, subcategory, tool in result:
            if category.id not in result_grouped:
                result_grouped[category.id] = {
                    "id": category.id,
                    "nodeType": "category",
                    "displayName": category.fallbackText,
                    "icon": category.icon,
                    "subcategories": []
                }

            subcategory_entry = {
                "id": subcategory.id,
                "nodeType": "subcategory",
                "displayName": subcategory.fallbackText,
                "icon": subcategory.icon,
                "tools": [
                    {
                        "id": tool.id,
                        "nodeType": "tool",
                        "displayName": str(tool),
                        "icon": tool.icon,
                    }
                ]
            }

            result_grouped[category.id]["subcategories"].append(subcategory_entry)

        return result_grouped
    
    tool_tree = {}

def getUnassignedTools(search_query: str = '', assigned_tools: list=None) -> dict:
    with Session() as session:
        assigned_tool_ids = assigned_tools or (
            select(Tool.id)
            .join(Pocket, Pocket.toolId == Tool.id)
        )

        result = (
            session.query(Tool)
            .filter(
                or_(
                    Tool.id.like(f'%{search_query}%'),
                    Tool.description.like(f'%{search_query}%'),
                ),
                Tool.id.notin_(assigned_tool_ids),
            )
            .all()
        )

        tool_tree = dict()

        for tool in result:
            subcategory = tool.subcategory
            category = subcategory.category

            if category.id not in tool_tree:
                tool_tree[category.id] = {
                    "id": category.id,
                    "nodeType": "category",
                    "displayName": category.fallbackText,
                    "icon": category.icon,
                    "subcategories": [],
                    "subcat": {},
                }

            if subcategory.id not in tool_tree[category.id]['subcat']:
                tool_tree[category.id]['subcat'][subcategory.id] = {
                    "id": subcategory.id,
                    "nodeType": "subcategory",
                    "displayName": subcategory.fallbackText,
                    "icon": subcategory.icon,
                    "tools": [],
                }

            # Add the tool to the subcategory
            tool_tree[category.id]['subcat'][subcategory.id]["tools"].append({
                "id": tool.id,
                "nodeType": "tool",
                "displayName": str(tool),
                "icon": tool.icon,
            })

        for cat in tool_tree.values():
            try:
                subcat_dict = cat.get('subcat', {})
                cat["subcategories"] = tuple(subcat_dict.values())
                del cat["subcat"]
            except Exception as e:
                print(e)

        return tool_tree

def getToolTree() -> dict:
    with Session() as session:
        categories = session.query(Category).all()

        return {
            cat.id: {
                    "id": cat.id,
                    "nodeType": "category",
                    "displayName": cat.fallbackText,
                    "icon": cat.icon,
                    "subcategories": tuple({
                        "id": subcat.id,
                        "nodeType": "subcategory",
                        "displayName": subcat.fallbackText,
                        "icon": subcat.icon,
                        "tools": tuple({
                            "id": tool.id,
                            "nodeType": "tool",
                            "displayName": str(tool),
                            "icon": tool.icon,
                        } for tool in subcat.tools),
                    } for subcat in cat.subcategories)
                } for cat in categories
            }
