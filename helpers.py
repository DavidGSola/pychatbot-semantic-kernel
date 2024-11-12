def get_libraries():
    libraries = []
    with open('requirements.txt', 'r', encoding='utf-16') as requirements:
        for line in requirements.readlines():
            if '==' in line:
                lib, version = line.strip().split('==')
                libraries.append(f"{lib}: {version}")

    return libraries

def swap_visibility(elements):
    for el in elements: el.visible = not el.visible