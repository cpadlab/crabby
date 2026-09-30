from PyQt6.QtCore import (
    QEasingCurve,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QGuiApplication, QMouseEvent, QScreen
from PyQt6.QtWidgets import QWidget


class DragController(QObject):
    """
    Manages drag physics, screen padding, and smooth magnetic edge snapping.

    Attributes:
        position_settled: Signal emitted with `(rel_x, rel_y, screen_name)` when
            the target widget settles into its final position, where coordinates
            are normalized ratios between 0.0 and 1.0.
        target: The widget being dragged and animated.
        screen_margin: Margin in pixels maintained between the widget and screen edges.
        is_dragging: Whether a mouse drag operation is actively in progress.
    """


    position_settled = pyqtSignal(float, float, str)


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


    def _get_current_screen(self) -> QScreen:
        """
        Retrieves the screen containing the target widget's center point.

        Returns:
            QScreen: The screen currently under the center of the widget, or
            the primary screen as a fallback.
        """
        center_point = self.target.geometry().center()
        screen = QGuiApplication.screenAt(center_point)
        
        if not screen:
            screen = QGuiApplication.primaryScreen()
        
        return screen


    def _get_current_screen_geometry(self) -> QRect:
        """
        Retrieves the usable geometry of the current screen.

        Returns:
            QRect: Available geometry bounds excluding taskbars, docks, and system bars.
            Falls back to a default 1920x1080 rectangle if no screen is available.
        """
        screen = self._get_current_screen()
        return screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)


    def _get_clamped_bounds(self, screen_rect: QRect) -> tuple[int, int, int, int]:
        """
        Calculates coordinate boundaries clamped to screen margins.

        Args:
            screen_rect: The geometry of the screen to bound within.

        Returns:
            tuple[int, int, int, int]: A tuple containing `(min_x, max_x, min_y, max_y)`
            permissible top-left pixel coordinates for the target widget.
        """
        min_x = screen_rect.left() + self.screen_margin
        max_x = screen_rect.right() - self.target.width() - self.screen_margin + 1
        min_y = screen_rect.top() + self.screen_margin
        max_y = screen_rect.bottom() - self.target.height() - self.screen_margin + 1
        
        return min_x, max_x, min_y, max_y


    def calculate_relative_position(self, point: QPoint) -> tuple[float, float, str]:
        """
        Converts an absolute pixel point into a normalized ratio for the current screen.

        Maps coordinates within the clamped available screen area to values ranging
        from 0.0 to 1.0, rounded to 4 decimal places.

        Args:
            point: Absolute pixel coordinates of the widget.

        Returns:
            tuple[float, float, str]: A tuple of `(rel_x, rel_y, screen_name)` representing
            the normalized horizontal and vertical coordinates alongside the screen identifier.
        """
        screen = self._get_current_screen()
        rect = screen.availableGeometry()
        min_x, max_x, min_y, max_y = self._get_clamped_bounds(rect)

        span_x = max(1, max_x - min_x)
        span_y = max(1, max_y - min_y)

        rel_x = round(max(0.0, min(1.0, (point.x() - min_x) / span_x)), 4)
        rel_y = round(max(0.0, min(1.0, (point.y() - min_y) / span_y)), 4)

        return rel_x, rel_y, screen.name()


    def _on_animation_finished(self) -> None:
        """
        Handles completion of the snap animation and emits settlement coordinates.

        Calculates the normalized relative position and screen identifier from
        the widget's settled pixel coordinates and emits `position_settled`.
        """
        rel_x, rel_y, screen_name = self.calculate_relative_position(self.target.pos())
        self.position_settled.emit(rel_x, rel_y, screen_name)


    def _calculate_nearest_magnet_point(
        self, current_x: int, current_y: int, screen_rect: QRect
    ) -> QPoint:
        """
        Determines the closest clamped screen edge point to snap onto.

        Calculates orthogonal distances to all four margin boundaries and selects
        the nearest edge, maintaining the other axis within valid clamped limits.

        Args:
            current_x: Current horizontal pixel coordinate of the widget.
            current_y: Current vertical pixel coordinate of the widget.
            screen_rect: The usable geometry of the screen to snap against.

        Returns:
            QPoint: The closest destination point on the nearest margin boundary.
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

        Interrupts active snapping animations, captures the drag offset relative
        to the widget's top-left corner, and updates the mouse cursor.

        Args:
            event: The mouse press event.

        Returns:
            bool: True if the left mouse button triggered the drag; False otherwise.
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
        Handles mouse movement to update the dragged widget position.

        Moves the widget following the cursor offset while constraining its
        coordinates within the usable margins of the current screen.

        Args:
            event: The mouse move event.

        Returns:
            bool: True if dragging is active and the event was handled; False otherwise.
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
        Handles mouse release events to end dragging and snap to the nearest edge.

        Restores the pointer cursor, determines the closest edge, and either executes
        a dynamic cubic-ease snapping animation or directly emits `position_settled`
        if already at the destination.

        Args:
            event: The mouse release event.

        Returns:
            bool: True if dragging concluded and the release was handled; False otherwise.
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
                rel_x, rel_y, screen_name = self.calculate_relative_position(target_pos)
                self.position_settled.emit(rel_x, rel_y, screen_name)

            event.accept()
            return True
            
        return False