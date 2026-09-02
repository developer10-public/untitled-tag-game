from builtin import *
from ursina import Ursina
main = Ursina()
fpc = FirstPersonController()
player = Player(parent=fpc,model="",enabled=True)
tpc = ThirdPersonController()
player_third = Player(parent=tpc, model="", enabled=False)
bot = Bot("")

