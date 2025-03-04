#!/usr/bin/env python3

import os
import sys
import re

from tooldb import tooldb_callbacks # functions (g,p,l,u)
from tooldb import tooldb_tools     # list of tool numbers
from tooldb import tooldb_loop      # main loop

from qtpyvcp.lib.db_tool.base import Session, Base, engine
from qtpyvcp.lib.db_tool.tool_table import ToolTable, Tool

# Catch unhandled exceptions
def excepthook(exc_type, exc_msg, exc_tb):
    print(exc_type, file=sys.stderr)
    print(exc_msg, file=sys.stderr)
    print(exc_tb, file=sys.stderr)


sys.excepthook = excepthook


class DataBaseManager():
    def __init__(self):
        super(DataBaseManager, self).__init__()
        self.session = None
        
        Base.metadata.create_all(engine)
        
        self.session = Session()
        
        tools = self.session.query(Tool).all()
        tool_list = list()

        for tool in tools:
            tool_list.append(tool.tool_no)
    
        tooldb_tools(tool_list)
        tooldb_callbacks(self.user_get_tool,
                         self.user_put_tool,
                         self.user_load_spindle,
                         self.user_unload_spindle)
            
        
        self.tool_list = tool_list
        
        self.tools = dict()

  
    def close(self):
        self.session.close()

    def user_get_tool(self, tool_no):
        print(f"GET tool {tool_no}", file = sys.stderr)

        tool = self.session.query(Tool).filter(Tool.tool_no == tool_no).one()
        
        data = [f"T{tool.tool_no}",
                f"P{tool.pocket}",
                f"D{tool.diameter}",
                f"X{tool.x_offset}",
                f"Y{tool.y_offset}",
                f"Z{tool.z_offset}",
                f"A{tool.a_offset}",
                f"B{tool.b_offset}",
                f"C{tool.c_offset}",
                f"U{tool.u_offset}",
                f"V{tool.v_offset}",
                f"W{tool.w_offset}"]

        return " ".join(data)


    def user_put_tool(self, toolno, params):
        print(f"PUT tool {toolno} {params}", file=sys.stderr)
        
        tool = self.session.query(Tool).filter(Tool.tool_no==toolno).one()
        params_list = re.split(r'   | |;', params)
        
        tool_dict = dict()
        
        for param in params_list:
            column = param[0]
            value = param[1::]
            tool_dict[column] = value

        tool.tool_no = tool_dict.get("T")
        tool.pocket = tool_dict.get("P")
        tool.x_offset = tool_dict.get("X")
        tool.y_offset = tool_dict.get("Y")
        tool.z_offset = tool_dict.get("Z")
        tool.a_offset = tool_dict.get("A")
        tool.b_offset = tool_dict.get("B")
        tool.c_offset = tool_dict.get("C")
        tool.i_offset = tool_dict.get("I")
        tool.j_offset = tool_dict.get("J")
        tool.q_offset = tool_dict.get("Q")
        tool.u_offset = tool_dict.get("U")
        tool.v_offset = tool_dict.get("V")
        tool.w_offset = tool_dict.get("W")
        tool.diameter = tool_dict.get("D")
        
        self.session.commit()

    
    def user_load_spindle(self, toolno, params):
        pass
    
    def user_unload_spindle(self, toolno, params):
        pass


def main():
    
    tool_db_man = DataBaseManager()
    
    try:
        tooldb_loop()  # loop forever, use callbacks
    except Exception as e:
        print(f"Exception = {e}", file=sys.stderr)
    
    tool_db_man.close()

if __name__ == "__main__":
    main()