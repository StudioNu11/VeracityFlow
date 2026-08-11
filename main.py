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


def on_hotkey():
    try:
        if not verification_lock.acquire(blocking=False):
            playsound('Verifying.mp3', block=False)
            notification.title = "Verifying..."
            notification.message = "Verification in progress."
            notification.send(block=False)
            return
        try:
            playsound('Start.mp3', block=False)
            data = vision()
            if data.get("claim") is None:
                notification.title = "No claim found."
                notification.message = "No verifiable claim was found."
                notification.send(block=False)
                return
            veracity_input = evidence(data)
            result = scoring(veracity_input)
            result["claim"] = data["claim"]
            playsound('Popup.mp3', block=False)
            bridge.result_ready.emit(result)
        finally:
            verification_lock.release()
    except Exception as e:
        notification.title = "VeracityFlow encountered an error."
        notification.message = "There was an error during verification, please try again later."
        notification.send(block=False)



keyboard.add_hotkey("ctrl+shift+v", lambda: threading.Thread(target=on_hotkey).start())
notification.title = "VeracityFlow is running..."
notification.message = "Press Ctrl+Shift+V to use."
notification.send(block=False)

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("logo.ico"))
app.setQuitOnLastWindowClosed(False)
app.exec_()
