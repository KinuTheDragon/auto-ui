from aui_parser import parse_aui
from aui_app_maker import to_app

def make_app(src_filename, commands_filename, icon_filename):
    with open(src_filename) as f:
        src = f.read()
    parsed = parse_aui(src)
    data = {"filenames": {"commands": commands_filename, "icon": icon_filename},
            "content": parsed}
    output = to_app(data)
    return output