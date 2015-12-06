import datetime
import os
import sys
#import psutil
import asyncio
import subprocess
import configparser

# List of lists, list of elements,
# if right, left or center
# and in which order they should be shown.

# shown_objects = {pacages:['r', '0', 'data as a string'],
#                  date:['c', '0', 'data as a string']}
shown_objects = {}

def showing_objects(config, loop):
    current_objects = shown_objects.copy()
    left_objects = []
    center_objects = []
    right_objects = []
    # Sorting stuff into left, right or center on the bar.
    for object in current_objects:
        if current_objects[object][0] == 'l':
            left_objects.append(current_objects[object])
        elif current_objects[object][0] == 'c':
            center_objects.append(current_objects[object])
        else:
            right_objects.append(current_objects[object])
    # Sorting by number priority.
    left_sorted = sorted(left_objects, key=lambda left_sorted: left_sorted[1])
    center_sorted = sorted(center_objects, key=lambda center_sorted: center_sorted[1])
    right_sorted = sorted(right_objects, key=lambda right_sorted: right_sorted[1])
    # Creating the strings...
    padding = ''
    for i in range(0, int(config['side_padding'])):
        padding += ' '
    left_items = '%{l}' + padding
    for i in left_sorted:
        left_items += i[2]
    center_items = '%{c}'
    for i in center_sorted:
        center_items += i[2]
    right_items = '%{r}'
    for i in right_sorted:
        right_items += i[2]
    right_items += padding
    print(left_items, center_items, right_items, flush=True)
    loop.call_later(1, showing_objects, config, loop)

def formating(obj, orientation='l', order=0):
    return [orientation, order, obj]

def coloring(obj, fg_color):
    ret = '%{F#' + fg_color + '}' + obj + '%{F-}'
    return ret

def display_bspwm(config, loop):
    bsp_event = subprocess.check_output(["bspc", "control", "--get-status"], universal_newlines=True).strip()
    bsp_events = bsp_event.split(':')
    # First part is not used for anything fun so lets remove it.
    bsp_events.pop(0)
    # Last element is the Layout, lets save it somewhere else.
    bsp_layout = bsp_events.pop(len(bsp_events) - 1)
    bsp_tabs = []
    for i in bsp_events:
        # o means unfocused desktop with open windows.
        # f means unfocused desktop without open windows.
        # O is the focused desktop with open windows.
        # F is the focused desktop without open windows.
        if i.startswith('o'):
            bsp_tabs.append(coloring(i[1:], config['unfocus_fg_color'].rstrip()))
        elif i.startswith('O') or i.startswith('F'):
            bsp_tabs.append(coloring(i[1:], config['focus_fg_color'].rstrip()))
        else:
            pass
            #print('slask')
    bsp_string = ' '.join(bsp_tabs)
    shown_objects['bspwm'] = formating(bsp_string, config['alignment'], config['priority'])
    loop.call_later(1, display_bspwm, config, loop)

def display_date(config, loop):
    title = coloring(config['title'], config['title_color'])
    content = coloring(str(datetime.datetime.strftime(datetime.datetime.now(),
                           config.get('parsing', raw=True))), config['fg_color'])
    shown_objects['date'] = formating(title + ' ' + content, config['alignment'], config['priority'])
    loop.call_later(1, display_date, config, loop)

def display_packages(config, loop):
    p1 = subprocess.Popen(["pacman", "-Qu"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["wc", "-l"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]
    title = coloring(config['title'], config['title_color'])
    content = coloring(output.decode("utf-8").strip(), config['fg_color'])
    shown_objects['packages'] = formating(title + ' ' + content, config['alignment'], config['priority'])
    loop.call_later(120, display_packages, config, loop)

def main():
    config = configparser.ConfigParser()
    config.read('lemon-collector.conf')
    loop = asyncio.get_event_loop()
    # Just so we only get sane input from the configuration file.
    function_mapping = {
            'bspwm' : display_bspwm,
            'date'  : display_date,
            'pacman': display_packages,
    }
    # Figuring out which modules to load.
    enabledmod = config['general']['enabled_modules'].split()
    for i in enabledmod:
        try:
            loop.call_soon(function_mapping[i], config[i], loop)
        except KeyError:
            print(i, 'is not propperly mapped.')

    loop.call_soon(showing_objects, config['lemonbar'], loop)

    # Blocking call interrupted by loop.stop()
    loop.run_forever()
    loop.close()

if __name__ == '__main__':
    main()
