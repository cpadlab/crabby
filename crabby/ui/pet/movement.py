from PyQt6.QtCore import QObject, QPoint, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QWidget


class DragController(QObject):
    """
    Manages click-and-drag movement mechanics for a target widget.

    Attributes:
        target: The QWidget instance being moved.
        is_dragging: Whether the drag operation is currently active.
    """


    def __init__(self, target: QWidget) -> None:
        """
        Initializes the drag controller.

        Args:
            target: The QWidget that this controller will reposition.
        """
        super().__init__(target)
        self.target: QWidget = target
        self._drag_offset: QPoint = QPoint()
        self.is_dragging: bool = False


    def handle_press(self, event: QMouseEvent) -> bool:
        """
        Processes the mouse press event to start dragging.

        Args:
            event: The QMouseEvent emitted by the target widget.

        Returns:
            bool: True if the drag operation was started, False otherwise.
        """
        if event.button() == Qt.MouseButton.LeftButton:
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
        Processes mouse movement to update the target widget's position.

        Args:
            event: The QMouseEvent emitted by the target widget.

        Returns:
            bool: True if the target was moved, False otherwise.
        """
        if self.is_dragging and (event.buttons() & Qt.MouseButton.LeftButton):
            new_position = event.globalPosition().toPoint() - self._drag_offset
            
            self.target.move(new_position)
            
            event.accept()
            
            return True
        
        return False


    def handle_release(self, event: QMouseEvent) -> bool:
        """
        Processes the mouse release event to finish dragging.

        Args:
            event: The QMouseEvent emitted by the target widget.

        Returns:
            bool: True if the drag operation ended, False otherwise.
        """
        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.target.setCursor(Qt.CursorShape.PointingHandCursor)
            
            event.accept()
            return True

        return False