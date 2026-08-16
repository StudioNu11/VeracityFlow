import sys
import ctypes
import keyboard
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal
from gemini_client import client
from Vision import vision
from Evidence import evidence
from Scoring import scoring
from popup import show_popup
from playsound import playsound
from notifypy import Notify
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
import mute

notification = Notify()
notification.application_name = "VeracityFlow"
notification.icon = "logo.ico"

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("veracityflow.app")
except Exception:
    pass

verification_lock = threading.Lock()


class Bridge(QObject):
    result_ready = pyqtSignal(dict)


bridge = Bridge()
bridge.result_ready.connect(lambda result: show_popup(result))

try:
    client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=["ping"]
    )
except Exception:
    pass

def makesound(file):
    if mute.is_muted():
        return
    else:
        playsound(file, block = False)

def on_hotkey():
    try:
        if not verification_lock.acquire(blocking=False):
            makesound('Verifying.mp3')
            notification.title = "Verifying..."
            notification.message = "Verification in progress."
            notification.send(block=False)
            return
        try:
            makesound('Start.mp3')
            data = vision()
            if data.get("claim") is None:
                notification.title = "No claim found."
                notification.message = "No verifiable claim was found."
                notification.send(block=False)
                return
            veracity_input = evidence(data)
            result = scoring(veracity_input)
            result["claim"] = data["claim"]
            if result["confidence_score"] > 60:
                makesound('Popup.mp3')
                bridge.result_ready.emit(result)
            else:
                notification.title = "Not enough verifiable information"
                notification.message = "Not enough info found. The claim might be too new. Try again later"
                notification.send(block=False)
        finally:
            verification_lock.release()
    except Exception as e:
        notification.title = "VeracityFlow encountered an error."
        notification.message = "There was an error during verification, please try again later. Error: " + str(e)
        notification.send(block=False)



keyboard.add_hotkey("alt+shift+z", lambda: threading.Thread(target=on_hotkey).start())
notification.title = "VeracityFlow is running..."
notification.message = "Press Alt+Shift+Z to use."
notification.send(block=False)

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("logo.ico"))
app.setQuitOnLastWindowClosed(False)
tray_icon = QSystemTrayIcon(QIcon("logo.ico"), app)
tray_icon.setToolTip("VeracityFlow")
menu = QMenu()
exit_action = QAction("Exit")
exit_action.triggered.connect(app.quit)
menu.addAction(exit_action)
tray_icon.setContextMenu(menu)
tray_icon.show()
app.exec_()
