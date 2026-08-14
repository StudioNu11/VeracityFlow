import keyboard
from notifypy import Notify

notification = Notify()
notification.application_name = "VeracityFlow"
notification.icon = "logo.ico"
muted = False

def toggle_mute():
    global muted
    if muted == False:
        muted = True
        notification.title = "Sounds are disabled"
        notification.message = "Sounds are disabled, toggle using Alt+Shift+M"
        notification.send(block=False)

    else:
        muted = False
        notification.title = "Sounds are enabled"
        notification.message = "Sounds are enabled, toggle using Alt+Shift+M"
        notification.send(block=False)


keyboard.add_hotkey("alt+shift+m", toggle_mute)

def is_muted():
    return muted
