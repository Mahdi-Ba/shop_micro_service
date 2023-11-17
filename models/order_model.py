import datetime
import uuid

from eventsourcing.domain import Aggregate, event

from goods_model import Goods


class PaymentProcessed(Aggregate.Event):
    is_paid: bool


class OrderDispatched(Aggregate.Event):
    is_dispatched: bool


class OrderDelivered(Aggregate.Event):
    is_delivered: bool


class OrderPlaced(Aggregate.Event):
    order_id: int
    buyer_id: int
    goods_id: int
    is_active: bool


class OrderCancelled(Aggregate.Event):
    order_id: int


class Order(Aggregate):
    def __init__(self):
        self.order_id = None
        self.buyer_id = None
        self.goods_id = None
        self.is_active = False
        self.is_paid = False
        self.is_dispatched = False
        self.is_delivered = False
        self.message = ''

    def get_order(self, order_id):
        if self.order_id == order_id:
            return self
        raise ValueError('not found')

    @event(OrderPlaced)
    def place_order(self, buyer_id, goods_id):
        item = Goods().find_one_item(goods_id)
        item.change_is_ordered(True)
        self.order_id = str(uuid.uuid4())
        self.buyer_id = buyer_id
        self.goods_id = goods_id
        self.is_active = True
        self.is_paid = False
        self.is_dispatched = False
        self.is_delivered = False

    @event(OrderCancelled)
    def cancel_order(self, order_id):
        if not self.is_active:
            raise ValueError("Order is not active and cannot be cancelled.")
        if self.order_id != order_id:
            raise ValueError("Order ID does not match.")
        self.is_active = False

    @event(PaymentProcessed)
    def payment_process(self):
        self.is_paid = True

    @event(OrderDelivered)
    def order_delivered(self):
        self.is_delivered = True

    @event(OrderDispatched)
    def dispatch_order(self):
        if not self.is_paid:
            raise ValueError("Cannot dispatch an order that hasn't been paid for.")
        self.is_dispatched = True
