from eventsourcing.domain import Aggregate, event
import uuid


class GoodsCreated(Aggregate.Event):
    _id: str
    seller_id: int
    name: str
    description: str
    price: int
    is_ordered: bool


class GoodsChangeOrder(Aggregate.Event):
    _id: str
    is_ordered: bool


class Goods(Aggregate):
    def __init__(self):
        self._id = None
        self.seller_id = None
        self.name = None
        self.description = None
        self.price = 0
        self.is_ordered = False

    @event(GoodsCreated)
    def create_goods(self, seller_id, name, description, price):
        self._id = str(uuid.uuid4())
        self.seller_id = seller_id
        self.name = name
        self.description = description
        self.price = price

    def find_one_item(self, item_id):
        if self._id == item_id:
            return self
        raise ValueError('not found')

    @event(GoodsChangeOrder)
    def change_is_ordered(self, is_ordered: bool):
        self.is_ordered = is_ordered
