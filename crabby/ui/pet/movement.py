from PyQt6.QtCore import (
    QEasingCurve,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QGuiApplication, QMouseEvent
from PyQt6.QtWidgets import QWidget


class DragController(QObject):
    """
    Manages drag physics, screen padding, and smooth magnetic edge snapping.

    Attributes:
        position_settled: Signal emitted with (x, y) coordinates when the target
            widget completes its magnetic snap animation or settles into place.
        target: The widget being dragged and animated.
        screen_margin: Margin in pixels maintained between the widget and screen edges.
        is_dragging: Whether a mouse drag operation is actively in progress.
    """


    position_settled = pyqtSignal(int, int)


    def __init__(self, target: QWidget, screen_margin: int = 12) -> None:
        """
        Initializes the DragController with a target widget and margin.

        Args:
            target: The widget instance to be moved and animated.
            screen_margin: Minimum margin in pixels to keep from the screen
                boundaries. Defaults to 12.
        """
        super().__init__(target)
        self.target: QWidget = target
        self.screen_margin: int = screen_margin
        self.is_dragging: bool = False
        self._drag_offset: QPoint = QPoint()

        self._snap_animation = QPropertyAnimation(self.target, b"pos", self)
        self._snap_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._snap_animation.finished.connect(self._on_animation_finished)


    def _on_animation_finished(self) -> None:
        """
        Emits settlement coordinates once magnetic animation completes.
        """
        self.position_settled.emit(self.target.x(), self.target.y())


    def _get_current_screen_geometry(self) -> QRect:
        """
        Retrieves the available geometry of the screen containing the target widget.

        Resolves the screen using the target's center point. Falls back to the
        primary screen or a default 1080p rectangle if no screen is detected.

        Returns:
            QRect: The available geometry bounds excluding taskbars and docks.
        """
        center_point = self.target.geometry().center()
        screen = QGuiApplication.screenAt(center_point)

        if not screen:
            screen = QGuiApplication.primaryScreen()

        return screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)


    def _get_clamped_bounds(self, screen_rect: QRect) -> tuple[int, int, int, int]:
        """
        Calculates coordinate boundaries clamped to screen margins.

        Args:
            screen_rect: The geometry of the screen to bound within.

        Returns:
            tuple[int, int, int, int]: A tuple containing (min_x, max_x, min_y, max_y)
            permissible top-left coordinates for the target widget.
        """
        min_x = screen_rect.left() + self.screen_margin
        max_x = screen_rect.right() - self.target.width() - self.screen_margin + 1
        min_y = screen_rect.top() + self.screen_margin
        max_y = screen_rect.bottom() - self.target.height() - self.screen_margin + 1

        return min_x, max_x, min_y, max_y


    def _calculate_nearest_magnet_point(
        self, current_x: int, current_y: int, screen_rect: QRect
    ) -> QPoint:
        """
        Finds the closest edge point on the screen to snap the widget onto.

        Compares the perpendicular distances from the widget's current coordinates
        to all four screen boundaries (accounting for margins) and chooses the
        closest edge.

        Args:
            current_x: Current horizontal coordinate of the widget.
            current_y: Current vertical coordinate of the widget.
            screen_rect: The geometry of the screen to snap against.

        Returns:
            QPoint: The closest point on the nearest margin boundary.
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
        Handles mouse press events to initiate dragging.

        Stops any ongoing snapping animation, records the relative click offset,
        and switches the cursor to a closed hand.

        Args:
            event: The mouse event received from the target widget.

        Returns:
            bool: True if the event was consumed and dragging initiated; False otherwise.
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
        Handles mouse move events to update the target widget's position.

        Moves the widget while clamping coordinates within the visible screen boundaries.

        Args:
            event: The mouse move event received from the target widget.

        Returns:
            bool: True if the movement was handled; False otherwise.
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
        Handles mouse release events to end dragging and trigger magnetic snapping.

        Restores the cursor, calculates the nearest edge, and either initiates a
        smooth snapping animation or emits `position_settled` directly if already in place.

        Args:
            event: The mouse release event received from the target widget.

        Returns:
            bool: True if the release was handled; False otherwise.
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
            else:
                self.position_settled.emit(target_pos.x(), target_pos.y())

            event.accept()
            return True

        return False