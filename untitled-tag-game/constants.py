"Built-in constants for moving."
from typing import TypeAlias
MoveType:TypeAlias = int
FlagTypes:TypeAlias = list
MOVE_FORWARD:MoveType = 1
MOVE_LEFT:MoveType = 2
MOVE_RIGHT:MoveType = 3
MOVE_BACKWARD:MoveType = 4
FLAGS:FlagTypes = ["player", "opponent"]
MOVE_FLAGS:FlagTypes = [MOVE_FORWARD, MOVE_LEFT, MOVE_RIGHT, MOVE_BACKWARD]
MODES = ["single", "multi"]
TEAMS = ["red", "blue"]
ROLES=["bot", "player", "opponent"]