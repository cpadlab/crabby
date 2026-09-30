from enum import Enum
from crabby.shared.logger import logger


class PetState(Enum):
    """
    Enumeration of possible pet behavior and movement states.
    """
    IDLE = "idle"
    MOVING_LEFT = "moving_left"
    MOVING_RIGHT = "moving_right"


class PetSkin:
    """
    Manages visual state representation and console reporting for the pet.

    Attributes:
        current_state: The current active `PetState`.
    """

    def __init__(self, initial_state: PetState = PetState.IDLE) -> None:
        """
        Initializes the PetSkin with a starting state.

        Args:
            initial_state: The starting `PetState`. Defaults to `PetState.IDLE`.
        """
        self._current_state: PetState = initial_state
        self._log_state(initial_state)


    @property
    def current_state(self) -> PetState:
        """
        Gets the current state of the pet skin.

        Returns:
            PetState: The currently active state.
        """
        return self._current_state


    def set_state(self, new_state: PetState) -> None:
        """
        Updates the pet state and reports transitions to the console.

        Args:
            new_state: The new `PetState` to transition to.
        """
        if self._current_state != new_state:
            self._current_state = new_state
            self._log_state(new_state)


    def _log_state(self, state: PetState) -> None:
        """
        Prints and logs state transitions to standard output and the logger.

        Args:
            state: The state being reported.
        """
        if state == PetState.MOVING_RIGHT:
            msg = "Pet Skin Status: Moving to the right"
        elif state == PetState.MOVING_LEFT:
            msg = "Pet Skin Status: Moving to the left"
        elif state == PetState.IDLE:
            msg = "Pet Skin Status: IDLE"
        else:
            msg = f"Pet Skin Status: {state.value}"

        logger.info(msg)
