
from aiogram.fsm.state import State, StatesGroup

class User(StatesGroup):
    category = State()
    quest = State()
    photo = State()
    text = State()
    
