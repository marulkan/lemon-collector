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

# Colour template for now:
focus_colour = '%{Fwhite}'
unfocus_colour = '%{Fred}'
eof_colour = '%{F-}'

def showing_objects(loop):
    print(str(shown_objects), flush=True)
    loop.call_later(1, showing_objects, loop)

def formating(obj, orientation='l', order=0):
    return [orientation, order, obj]

def colouring(obj, fg_colour):
    ret = fg_colour + obj + eof_colour
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
        if i.startswith('o'):
            bsp_tabs.append(colouring(i[1:], unfocus_colour))
        elif i.startswith('f'):
            pass
            #print('moo')
        elif i.startswith('u'):
            pass
            #print('poo')
        else:
            pass
            #print('slask')
    #print(bsp_tabs)
    shown_objects['bspwm'] = formating(bsp_tabs, 'r')
    loop.call_later(1, display_bspwm, loop)


def display_date(loop):
    shown_objects['date'] = formating(str(datetime.datetime.now()))
    loop.call_later(1, display_date, loop)

def display_packages(loop):
    p1 = subprocess.Popen(["pacman", "-Qu"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["wc", "-l"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]
    shown_objects['packages'] = formating(output.decode("utf-8").strip())
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
