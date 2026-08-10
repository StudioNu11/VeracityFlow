from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtGui import QFont, QFontMetrics, QIcon
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from playsound import playsound

FONT_FAMILY = "Inter"


def _autosize_font(text, family, max_pt, min_pt, max_width, max_height):
    for size in range(max_pt, min_pt - 1, -1):
        font = QFont(family, size)
        metrics = QFontMetrics(font)
        rect = metrics.boundingRect(0, 0, max_width, 10000, Qt.TextWordWrap, text)
        if rect.height() <= max_height:
            return font
    return QFont(family, min_pt)

_active_dialogs = []


class ResultDialog(QDialog):
    def __init__(self, scored: dict):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowIcon(QIcon("logo.ico"))
        self.setFixedSize(500, 320)
        self.setWindowOpacity(0.0)

        self._drag_pos = None

        container = QFrame(self)
        container.setGeometry(0, 0, 500, 320)
        container.setStyleSheet(
            "background-color: #1a1a1a; border-radius: 16px;"
        )

        outer_layout = QVBoxLayout(container)
        outer_layout.setContentsMargins(28, 24, 28, 24)
        outer_layout.setSpacing(16)

        outer_layout.addStretch()

        if scored.get("error"):
            self._build_error_content(outer_layout, scored)
        else:
            self._build_result_content(outer_layout, scored)

        outer_layout.addStretch()

        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self._fade_out)
        self.close_timer.start(10000)

    def _build_result_content(self, outer_layout, scored):
        self.claim_label = QLabel(scored.get("claim", ""))
        self.claim_label.setFont(QFont(FONT_FAMILY, 13, QFont.Bold))
        self.claim_label.setWordWrap(True)
        self.claim_label.setAlignment(Qt.AlignCenter)
        self.claim_label.setStyleSheet("color: #f2f2f2; background: transparent;")
        outer_layout.addWidget(self.claim_label)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)

        trust_card = self._build_card(
            "Trust rating", str(scored.get("trust_rating", "--"))
        )
        confidence_card = self._build_card(
            "Confidence", f"{scored.get('confidence_score', '--')}%"
        )

        cards_layout.addWidget(trust_card)
        cards_layout.addWidget(confidence_card)
        outer_layout.addLayout(cards_layout)

        reasoning_text = scored.get("reasoning", "")
        available_width = 500 - 28 * 2
        reasoning_font = _autosize_font(
            reasoning_text, FONT_FAMILY, max_pt=10, min_pt=7,
            max_width=available_width, max_height=110
        )

        self.reasoning_label = QLabel(reasoning_text)
        self.reasoning_label.setFont(reasoning_font)
        self.reasoning_label.setWordWrap(True)
        self.reasoning_label.setAlignment(Qt.AlignCenter)
        self.reasoning_label.setStyleSheet("color: #a0a0a0; background: transparent;")
        outer_layout.addWidget(self.reasoning_label)

    def _build_error_content(self, outer_layout, scored):
        title_label = QLabel("Verification failed")
        title_label.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ff6b6b; background: transparent;")
        outer_layout.addWidget(title_label)

        message_label = QLabel(scored.get("message", "Something went wrong. Try again."))
        message_label.setFont(QFont(FONT_FAMILY, 10))
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: #a0a0a0; background: transparent;")
        outer_layout.addWidget(message_label)

    def _build_card(self, label_text: str, value_text: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet("background-color: #2a2a2a; border-radius: 8px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(4)

        label = QLabel(label_text)
        label.setFont(QFont(FONT_FAMILY, 9))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #999999; background: transparent;")

        value = QLabel(value_text)
        value.setFont(QFont(FONT_FAMILY, 22, QFont.Bold))
        value.setAlignment(Qt.AlignCenter)
        value.setStyleSheet("color: #f2f2f2; background: transparent;")

        card_layout.addWidget(label)
        card_layout.addWidget(value)

        return card

    def fade_in(self):
        self.fade_anim.stop()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

    def _fade_out(self):
        self.fade_anim.stop()
        self.fade_anim.setStartValue(self.windowOpacity())
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self._close_self)
        self.fade_anim.start()

    def _close_self(self):
        self.close()
        if self in _active_dialogs:
            _active_dialogs.remove(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


def show_popup(scored: dict):
    dialog = ResultDialog(scored)
    dialog.show()
    dialog.fade_in()
    try:
        playsound("notify.mp3", block=False)
    except Exception:
        pass
    _active_dialogs.append(dialog)
    return dialog
