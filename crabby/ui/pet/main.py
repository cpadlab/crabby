import sys
from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QAction, QContextMenuEvent, QGuiApplication, QMouseEvent, QScreen
from PyQt6.QtWidgets import QApplication, QLabel, QMenu, QVBoxLayout, QWidget

from crabby.core.config import settings
from crabby.shared.logger import logger
from crabby.ui.pet.movement import DragController


class CrabbyPet(QWidget):
    """
    Floating desktop pet companion powered by PyQt6.

    Provides a frameless, transparent, draggable desktop widget that reacts to
    interactions (such as pokes and context menus) and persists its relative
    position across application runs.

    Attributes:
        pet_size: Size in pixels for both width and height of the pet window.
        drag_controller: Controller managing drag physics, clamping, and edge snapping.
        container: Visual wrapper widget hosting styled background and content.
        avatar_label: Label rendering the pet emoji or icon.
        name_label: Label displaying the pet's display name.
    """

    def __init__(self, size: int = 110) -> None:
        """
        Initializes the CrabbyPet widget.

        Args:
            size: Dimension in pixels for the square pet widget. Defaults to 110.
        """
        super().__init__()
        self.pet_size: int = size
        self.drag_controller: DragController = DragController(self)

        self.drag_controller.position_settled.connect(self._on_position_changed)

        self._configure_window()
        self._init_ui()


    def _on_position_changed(self, rel_x: float, rel_y: float, screen_name: str) -> None:
        """
        Persists relative coordinates whenever Crabby settles on screen.

        Args:
            rel_x: Normalized horizontal ratio (0.0 to 1.0) on the target screen.
            rel_y: Normalized vertical ratio (0.0 to 1.0) on the target screen.
            screen_name: Name of the display screen where the pet settled.
        """
        logger.info(
            f"Persisting Crabby position: x={rel_x:.2%}, y={rel_y:.2%}, screen='{screen_name}'"
        )
        settings.update_env(
            PET_REL_X=rel_x,
            PET_REL_Y=rel_y,
            PET_SCREEN_NAME=screen_name,
        )

    def _resolve_target_screen(self) -> QScreen:
        """
        Finds the saved screen by name or falls back to the primary screen.

        Returns:
            QScreen: The screen matching `settings.PET_SCREEN_NAME`, or the primary
            screen if the saved one is disconnected or unset.
        """
        screens = QGuiApplication.screens()
        if settings.PET_SCREEN_NAME:
            for s in screens:
                if s.name() == settings.PET_SCREEN_NAME:
                    return s

        return QGuiApplication.primaryScreen() or screens[0]


    def _restore_or_fallback_position(self) -> None:
        """
        Restores position using relative coordinates or initializes to bottom-right.

        Maps the persisted relative ratios to absolute pixel positions on the
        resolved display screen. If no coordinates were previously saved, places
        the pet in the bottom-right corner and writes those initial values to disk.
        """
        target_screen = self._resolve_target_screen()
        geom = target_screen.availableGeometry()

        margin = self.drag_controller.screen_margin
        min_x = geom.left() + margin
        max_x = geom.right() - self.pet_size - margin + 1
        min_y = geom.top() + margin
        max_y = geom.bottom() - self.pet_size - margin + 1

        span_x = max(1, max_x - min_x)
        span_y = max(1, max_y - min_y)

        if settings.PET_REL_X is not None and settings.PET_REL_Y is not None:
            target_x = int(min_x + (settings.PET_REL_X * span_x))
            target_y = int(min_y + (settings.PET_REL_Y * span_y))

            clamped_x = max(min_x, min(target_x, max_x))
            clamped_y = max(min_y, min(target_y, max_y))

            self.move(clamped_x, clamped_y)
            logger.info(
                f"Restored position on screen '{target_screen.name()}': ({clamped_x}, {clamped_y})"
            )
        else:
            self.move(max_x, max_y)
            rel_x, rel_y, screen_name = self.drag_controller.calculate_relative_position(
                QPoint(max_x, max_y)
            )
            settings.update_env(
                PET_REL_X=rel_x,
                PET_REL_Y=rel_y,
                PET_SCREEN_NAME=screen_name,
            )

    def _configure_window(self) -> None:
        """
        Sets up window flags, translucency, size, and initial position.
        """
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(self.pet_size, self.pet_size)

        self._restore_or_fallback_position()

    def _init_ui(self) -> None:
        """
        Initializes UI elements, visual container, labels, and styles.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget(self)
        self.container.setObjectName("petContainer")
        self.container.setStyleSheet("""
            QWidget#petContainer {
                background-color: rgba(30, 30, 46, 0.88);
                border: 2px solid #F38BA8;
                border-radius: 28px;
            }
            QWidget#petContainer:hover {
                background-color: rgba(30, 30, 46, 0.98);
                border: 2px solid #FAB387;
            }
        """)

        container_layout = QVBoxLayout(self.container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.avatar_label = QLabel("🦀", self.container)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("font-size: 38px; background: transparent;")

        self.name_label = QLabel("Crabby", self.container)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("""
            color: #CDD6F4;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11px;
            font-weight: bold;
            background: transparent;
        """)

        container_layout.addWidget(self.avatar_label)
        container_layout.addWidget(self.name_label)
        layout.addWidget(self.container)

        self.setCursor(Qt.CursorShape.PointingHandCursor)


    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Delegates mouse press events to DragController or superclass.

        Args:
            event: The incoming mouse press event.
        """
        if not self.drag_controller.handle_press(event):
            super().mousePressEvent(event)


    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Delegates mouse move events to DragController or superclass.

        Args:
            event: The incoming mouse move event.
        """
        if not self.drag_controller.handle_move(event):
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Delegates mouse release events to DragController or superclass.

        Args:
            event: The incoming mouse release event.
        """
        if not self.drag_controller.handle_release(event):
            super().mouseReleaseEvent(event)


    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """
        Handles double click events to animate a poke reaction.

        Temporarily replaces the avatar icon with sparkle emojis for 1.2 seconds.

        Args:
            event: The incoming mouse double-click event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            logger.info("Crabby received a poke! 🦀")
            self.avatar_label.setText("✨🦀✨")
            QTimer.singleShot(1200, lambda: self.avatar_label.setText("🦀"))
            event.accept()


    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """
        Displays a custom right-click context menu.

        Args:
            event: The incoming context menu event containing cursor coordinates.
        """
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E1E2E;
                color: #CDD6F4;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item:selected {
                background-color: #313244;
                border-radius: 4px;
            }
        """)

        quit_action = QAction("Despedir a Crabby 👋", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)

        menu.exec(event.globalPos())


def launch_pet() -> None:
    """
    Spawns and executes the Crabby desktop pet application loop.

    Ensures a single `QApplication` instance exists, creates the `CrabbyPet`
    widget, displays it on screen, and blocks on the Qt event loop until closed.
    """
    logger.info("Spawning Crabby desktop pet...")
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    pet = CrabbyPet()
    pet.show()

    logger.info("Crabby is now active on your desktop.")
    sys.exit(app.exec())