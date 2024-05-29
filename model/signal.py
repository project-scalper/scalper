#!/usr/bin/python3

from model.base_model import BaseModel
from datetime import datetime


class Signal(BaseModel):
    __tablename__ = 'signals'

    symbol = ''
    completed_date = datetime.now()
    signal = ''
    pnl = 0
    leverage = 20

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)