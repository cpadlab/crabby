from PyQt6.QtCore import (
    QEasingCurve,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    Qt,
)
from PyQt6.QtGui import QGuiApplication, QMouseEvent
from PyQt6.QtWidgets import QWidget


class DragController(QObject):
    """
    Manages drag physics, screen padding, and smooth magnetic edge snapping.

    Attributes:
        target: The target QWidget instance being manipulated.
        screen_margin: Safe padding in pixels maintained from all screen boundaries.
        is_dragging: Whether the user is actively dragging the widget with the mouse.
    """


    def __init__(self, target: QWidget, screen_margin: int = 12) -> None:
        """
        Initializes the DragController.

        Args:
            target: The QWidget instance to control.
            screen_margin: Margin in pixels from screen edges. Defaults to 12.
        """
        super().__init__(target)
        self.target: QWidget = target
        self.screen_margin: int = screen_margin
        self.is_dragging: bool = False
        self._drag_offset: QPoint = QPoint()

        self._snap_animation = QPropertyAnimation(self.target, b"pos", self)
        self._snap_animation.setEasingCurve(QEasingCurve.Type.OutCubic)


    def _get_current_screen_geometry(self) -> QRect:
        """
        Determines the available geometry of the screen containing the pet.

        Returns:
            QRect: Screen area excluding the OS taskbar/dock.
        """
        center_point = self.target.geometry().center()
        screen = QGuiApplication.screenAt(center_point)
        if not screen:
            screen = QGuiApplication.primaryScreen()
        return screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)


    def _get_clamped_bounds(self, screen_rect: QRect) -> tuple[int, int, int, int]:
        """
        Calculates min and max (x, y) coordinates respecting margins.

        Args:
            screen_rect: Available screen geometry.

        Returns:
            tuple[int, int, int, int]: (min_x, max_x, min_y, max_y)
        """
        min_x = screen_rect.left() + self.screen_margin
        max_x = screen_rect.right() - self.target.width() - self.screen_margin + 1
        min_y = screen_rect.top() + self.screen_margin
        max_y = screen_rect.bottom() - self.target.height() - self.screen_margin + 1
        return min_x, max_x, min_y, max_y


    def _calculate_nearest_magnet_point(self, current_x: int, current_y: int, screen_rect: QRect) -> QPoint:
        """
        Computes the target point on the closest screen boundary.

        Evaluates distance to left, right, top, and bottom edges and snaps to the nearest.

        Args:
            current_x: Current widget x position.
            current_y: Current widget y position.
            screen_rect: Available screen area.

        Returns:
            QPoint: Target magnetic snap coordinates.
        """
        min_x, max_x, min_y, max_y = self._get_clamped_bounds(screen_rect)

        dist_left = abs(current_x - min_x)
        dist_right = abs(max_x - current_x)
        dist_top = abs(current_y - min_y)
        dist_bottom = abs(max_y - current_y)

        min_dist = min(dist_left, dist_right, dist_top, dist_bottom)

        if min_dist == dist_left:
            return QPoint(min_x, max(min_y, min(current_y, max_y)))
        elif min_dist == dist_right:
            return QPoint(max_x, max(min_y, min(current_y, max_y)))
        elif min_dist == dist_top:
            return QPoint(max(min_x, min(current_x, max_x)), min_y)
        else:
            return QPoint(max(min_x, min(current_x, max_x)), max_y)


    def handle_press(self, event: QMouseEvent) -> bool:
        """
        Interrupts running animations and initiates the dragging state.

        Args:
            event: Mouse press event.

        Returns:
            bool: True if dragging started.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self._snap_animation.state() == QPropertyAnimation.State.Running:
                self._snap_animation.stop()

            self.is_dragging = True
            self._drag_offset = (
                event.globalPosition().toPoint() - self.target.frameGeometry().topLeft()
            )
            self.target.setCursor(Qt.CursorShape.ClosedHandCursor)
        
            event.accept()
            return True
        
        return False

    def handle_move(self, event: QMouseEvent) -> bool:
        """
        Constrains movement within screen margins while dragging.

        Args:
            event: Mouse movement event.

        Returns:
            bool: True if position changed.
        """
        if self.is_dragging and (event.buttons() & Qt.MouseButton.LeftButton):
            raw_pos = event.globalPosition().toPoint() - self._drag_offset
            screen_rect = self._get_current_screen_geometry()
            min_x, max_x, min_y, max_y = self._get_clamped_bounds(screen_rect)

            clamped_x = max(min_x, min(raw_pos.x(), max_x))
            clamped_y = max(min_y, min(raw_pos.y(), max_y))

            self.target.move(clamped_x, clamped_y)
            
            event.accept()
            return True
        
        return False


    def handle_release(self, event: QMouseEvent) -> bool:
        """
        Calculates nearest boundary edge and glides smoothly to it.

        Args:
            event: Mouse release event.

        Returns:
            bool: True if release was processed.
        """
        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.target.setCursor(Qt.CursorShape.PointingHandCursor)

            screen_rect = self._get_current_screen_geometry()
            target_pos = self._calculate_nearest_magnet_point(
                self.target.x(), self.target.y(), screen_rect
            )
            current_pos = self.target.pos()

            if current_pos != target_pos:
                dx = target_pos.x() - current_pos.x()
                dy = target_pos.y() - current_pos.y()
                distance = (dx * dx + dy * dy) ** 0.5

                duration = int(220 + (distance * 0.3))
                self._snap_animation.stop()
                self._snap_animation.setDuration(min(duration, 450))
                self._snap_animation.setStartValue(current_pos)
                self._snap_animation.setEndValue(target_pos)
                self._snap_animation.start()

            event.accept()
            return True

        return False