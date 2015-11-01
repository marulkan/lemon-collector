import datetime
import os
import sys
#import psutil
import asyncio
import subprocess

# List of lists, list of elements,
# if right, left or center
# and in which order they should be shown.

# shown_objects = {pacages:['r', '0', 'data as a string'],
#                  date:['c', '0', 'data as a string']}
shown_objects = {}

# Color template for now:
focus_color = '%{Fred}'
unfocus_color = '%{Fblue}'
unfocus2_color = '%{Fwhite}'
eof_color = '%{F-}'

def showing_objects(loop):
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
    left_items = '%{l}'
    for i in left_sorted:
        left_items += i[2]
    center_items = '%{c}'
    for i in center_sorted:
        center_items += i[2]
    right_items = '%{r}'
    for i in right_sorted:
        right_items += i[2]
    print(left_items, center_items, right_items, flush=True)
    loop.call_later(1, showing_objects, loop)

def formating(obj, orientation='l', order=0):
    return [orientation, order, obj]

def coloring(obj, fg_color):
    ret = fg_color + obj + eof_color
    return ret

def display_bspwm(loop):
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
            bsp_tabs.append(coloring(i[1:], unfocus_color))
        elif i.startswith('O') or i.startswith('F'):
            bsp_tabs.append(coloring(i[1:], focus_color))
        else:
            pass
            #print('slask')
    bsp_string = ' '.join(bsp_tabs)
    shown_objects['bspwm'] = formating(bsp_string, 'c')
    loop.call_later(1, display_bspwm, loop)


def display_date(loop):
    shown_objects['date'] = formating(str(datetime.datetime.now()), 'r', 0)
    loop.call_later(1, display_date, loop)

def display_packages(loop):
    p1 = subprocess.Popen(["pacman", "-Qu"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["wc", "-l"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]
    shown_objects['packages'] = formating(output.decode("utf-8").strip(), 'l', 1)
    loop.call_later(120, display_packages, loop)

loop = asyncio.get_event_loop()

# Schedule the first call to display_date()
loop.call_soon(display_date, loop)
loop.call_soon(display_packages, loop)
loop.call_soon(display_bspwm, loop)
loop.call_soon(showing_objects, loop)

# Blocking call interrupted by loop.stop()
loop.run_forever()
loop.close()
