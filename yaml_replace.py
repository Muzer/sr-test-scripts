import re

def replace_line(path, key, value):
    print("Replacing:", key, "->", value, "in", path)
    pattern = r"{key}( *):( *)(?:[^#\s]*)(.*)".format(key=key)

    with open(path) as fd:
        lines = list(fd)

    for i, line in enumerate(lines):
        match = re.match(pattern, line)
        if match is not None:
            lines[i] = "{key}{0}:{1}{value}{2}\n".format(*match.groups(),
                                                         key=key, value=value)
            break
    else:
        lines.append("{}: {}\n".format(key, value))

    with open(path, "w") as fd:
        for line in lines:
            fd.write(line)


def replace_condition(path, new_condition):
    replace_line(path, "condition", new_condition)


def replace_serial(path, new_serial):
    replace_line(path, "serial", new_serial)

