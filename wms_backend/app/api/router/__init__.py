# app/api/router/__init__.py
from app.api.router.warehouse import router as routes_warehouse
from app.api.router.product import router as routes_product
from app.api.router.inbound import router as routes_inbound
from app.api.router.outbound import router as routes_outbound
from app.api.router.slotting import router as routes_slotting
from app.api.router.picking import router as routes_picking
