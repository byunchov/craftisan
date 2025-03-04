import re
import sys
from pprint import pprint

VARIABLE_LINE_PATTERN = r'#(?:<([^>]+)>|(\d+))\s*=\s*([\d.]+|\[.*?\])\s*(?:\(([^)]+)\)|;\s*(.*?)?)?$'
SECTION_PATTERN = r'(?:[(;]\s*#?(\w+)\s*[)]*)'

SECTIONS_MINIMAL = ('dim', 'offsets')
SECTIONS = (*SECTIONS_MINIMAL, 'public', 'executions', 'feeds')
VARIABLE_TYPES = ('b', 'i', 'f')

def parse_gcode(file_path):
    parsed_data = {
        'dim': {'l': 0.0, 'h': 0.0, 's': 0.0},
        'offsets': {'ofx': 0.0, 'ofy': 0.0, 'ofz': 0.0},
        'public': {},
        # 'executions': {},
        # 'feeds': {}
    }

    dtype_callbacks = {
        'b': bool, 
        'i': int,
        'f': float,
    }

    parsed_sections = []
    current_section = None
    total_sections = len(SECTIONS)

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            match_section = re.match(SECTION_PATTERN, line, re.IGNORECASE)
            assignment_match = re.match(VARIABLE_LINE_PATTERN, line)

            if match_section and not assignment_match:
                current_section = match_section.group(1).lower()
                print(f"{current_section=}")

                if current_section not in parsed_sections:
                    parsed_sections.append(current_section)
                
                continue

            if current_section in SECTIONS and assignment_match:
                identifier = assignment_match.group(1) or assignment_match.group(2)
                value = assignment_match.group(3)
                comment_raw = assignment_match.group(4) or assignment_match.group(5) or ""
                comment_split = comment_raw.split('|')
                description = comment_split[0].strip()
                dtype_raw = comment_split[-1].strip().lower()

                if current_section not in parsed_data:
                    parsed_data[current_section] = {}
                
                if current_section == 'executions':
                    dtype = 'b'
                else:
                    dtype = dtype_raw if dtype_raw in VARIABLE_TYPES else 'f'

                if current_section in SECTIONS_MINIMAL:
                    parsed_data[current_section][identifier] = float(value)
                else:
                    callback = dtype_callbacks[dtype]
                    value = callback(value)

                    parsed_data[current_section][identifier] = {'value': value, 'description': description, 'dtype': dtype}

            # if current_section == SECTIONS[-1] and not assignment_match:
            parsed_section_count = len(parsed_sections)
            if (parsed_section_count == total_sections or parsed_sections == 2) and not assignment_match:
                break

    return parsed_data

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit()
    file_path = sys.argv[1]
    parsed_data = parse_gcode(file_path)
    with open('test_parsed.txt', 'w+') as f:
        pprint(parsed_data, stream=f, sort_dicts=False)

    print(f'Done parsing `{file_path}`')