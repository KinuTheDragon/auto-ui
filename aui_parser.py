import json

def parse_aui(src):
    data = {"overall title": None,
            "page titles": {},
            "widgets and startfuncs": [],
            "variables": {}}

    for line in src.split("\n"):
        if line.startswith("#"):
            if "#" in line[1:]:
                dummy, page, title = line.split("#")
                page = int(page)
                data["page titles"][page] = title
            else:
                data["overall title"] = line[1:]
        elif line.startswith("&"):
            data["widgets and startfuncs"].append({"type": "startfunc", "object": line[1:]})
        elif line and line[0] in "$%":
            name, dummy, value = line.partition(":")
            if name.startswith("%"): value = int(value)
            data["variables"][name] = value
        else:
            if "=" in line:
                name, dummy, widget = line.partition("=")
            else:
                name, widget = "dummy", line
            widget_type, dummy, widget_pos_data = widget.partition(" @ ")
            pos, dummy, widget_data = widget_pos_data.partition(" ")
            pos = [int(x) for x in pos[1:-1].split(",")]
            widget_from_json = json.loads(widget_data)
            for key, value in widget_from_json.items():
                if "variable" in key and value and value[0] in "$%" and value not in data["variables"]:
                    data["variables"][value] = "" if value[0] == "$" else 0
            widget_dict = {"name": name, "type": widget_type,
                           "pos": pos, "json": widget_from_json}
            data["widgets and startfuncs"].append({"type": "widget", "object": widget_dict})
    
    return data