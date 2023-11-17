from datetime import datetime, timezone, timedelta
import celery
import helpers.pubsub as celery_pubsub
from models.goods_model import Goods
from models.order_models import Order
from django.db import transaction


@celery.task
def purchase_item_task(buyer_id, item_id):
    with transaction.atomic():
        item = Goods.objects.select_for_update().find_one_goods(find_one_goods=item_id)
        if item.is_ordered:
            return "Item already sold", False
        else:
            item.change_is_ordered(True)
            order_id = Order.place_order(buyer_id, item_id)
            celery_pubsub.publish('order.purchase.purchase_expire_time',
                                  order_id=order_id, eta=datetime.now(timezone.utc) + timedelta(hours=12))
            return "Purchase successful", True


@celery.task
def payment_process_task(order_id):
    with transaction.atomic():
        order = Order.objects.select_for_update().get_order(order_id)
        if not order.is_active:
            return "Item is deactivated", False
        else:
            order.payment_process()
            celery_pubsub.publish('order.dispatch_order.shipped_expire_time',
                                  order_id=order_id, eta=datetime.now(timezone.utc) + timedelta(hours=24 * 3))
            return "successful payment", True


@celery.task
def dispatch_order_task(order_id):
    with transaction.atomic():
        order = Order.objects.select_for_update().get_order(order_id)
        if not order.is_active:
            return "Item is deactivated", False
        else:
            order.dispatch_order()
            return "successful dispatch",True

@celery.task
def order_delivered_task(order_id):
    with transaction.atomic():
        order = Order.objects.select_for_update().get_order(order_id)
        if not order.is_active:
            return "Item is deactivated", False
        else:
            order.order_delivered()
            return "successful dispatch",True


@celery.task
def shipped_expire_time_task(order_id):
    order = Order().get_order(order_id=order_id)
    if not order.is_delivered:
        order.cancel_order()
        Goods().find_one_item(order.goods_id).change_is_ordered(False)


@celery.task
def purchase_expire_time_task(order_id):
    order = Order().get_order(order_id=order_id)
    if not order.is_paid:
        order.cancel_order()
        Goods().find_one_item(order.goods_id).change_is_ordered(False)


@celery.task
def send_notification(*args, **kwargs):
    print('sending.......!')
    print('sending.......!')
    print('sending.......!')


# order purchase listener
celery_pubsub.subscribe('order.purchase', purchase_item_task)
celery_pubsub.subscribe('order.purchase.purchase_expire_time', purchase_expire_time_task)
celery_pubsub.subscribe('order.purchase.purchase_expire_time', send_notification)

# order payment_process listener
celery_pubsub.subscribe('order.payment_process', payment_process_task)

celery_pubsub.subscribe('order.dispatch_order', dispatch_order_task)
celery_pubsub.subscribe('order.dispatch_order.shipped_expire_time', shipped_expire_time_task)
celery_pubsub.subscribe('order.dispatch_order.shipped_expire_time', send_notification)

celery_pubsub.subscribe('order.order_delivered', order_delivered_task)
celery_pubsub.subscribe('order.order_delivered', send_notification)

# celery_pubsub.publish('order.purchase', buyer_id=1, item_id=42)
# celery_pubsub.publish('order.payment_process', order_id='bd65600d-8669-4903-8a14-af88203add38')
# celery_pubsub.publish('order.dispatch_order', order_id='bd65600d-8669-4903-8a14-af88203add38')
