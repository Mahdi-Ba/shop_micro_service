import datetime

from eventsourcing.domain import Aggregate, event
import uuid


class ChangeFreeAmount(Aggregate.Event):
    free_amount: int
    description: str


class ChangeFreezeAmount(Aggregate.Event):
    freeze_amount: int
    description: str


class Wallet(Aggregate):
    def __init__(self):
        self.person = None
        self.free_amount = 0
        self.freeze_amount = 0
        self.description = ''

    @event(ChangeFreeAmount)
    def increase_free_wallet(self, price):
        self.free_amount += price
        self.description = 'increase'

    @event(ChangeFreeAmount)
    def decrease_free_wallet(self, price):
        self.free_amount -= price
        self.description = 'decrease'

    @event(ChangeFreezeAmount)
    def increase_freeze_wallet(self, price):
        self.freeze_amount += price
        self.description = 'increase'

    @event(ChangeFreezeAmount)
    def decrease_freeze_wallet(self, price):
        self.freeze_amount -= price
        self.description = 'decrease'

    def get_amount(self):
        return self.free_amount, self.freeze_amount


class CreateTransaction:
    price: int
    order_id: str
    created_at: str

class ConfirmTransaction:
    is_success: bool
    is_lock: bool
    updated_at: str

class RejectTransaction:
    is_fail: bool
    is_lock: bool
    updated_at: str



class Transaction(Aggregate):
    def __init__(self):
        self._id = None
        self.price = 0
        self.created_at = None
        self.updated_at = None
        self.is_success = None
        self.is_lock = False
        self.is_fail = False
        self.order_id = None

    @event(CreateTransaction)
    def create_transaction(self, price, order_id):
        self._id = str(uuid.uuid4())
        self.price = price
        self.order_id = order_id
        self.created_at = datetime.datetime.utcnow()

    @event(ConfirmTransaction)
    def confirm_transaction(self):
        if self.is_lock:
            raise ValueError("transaction can't be modify")
        self.updated_at = datetime.datetime.utcnow()
        self.is_success = True
        self.is_lock = True

    @event(RejectTransaction)
    def reject_transaction(self):
        if self.is_lock:
            raise ValueError("transaction can't be modify")
        self.updated_at = datetime.datetime.utcnow()
        self.is_fail = True
        self.is_lock = True
