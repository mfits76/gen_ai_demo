from typing import Any

from genai_hub.integrations.base import EnterpriseConnector


class SAPERPConnector(EnterpriseConnector):
    """SAP-style ERP connector for inventory and order management."""

    system_name = "sap_erp"

    def __init__(self) -> None:
        self._inventory: dict[str, dict[str, Any]] = {
            "SKU-A100": {"sku": "SKU-A100", "name": "Industrial Sensor Module", "stock": 142, "unit_price_chf": 890.0},
            "SKU-B200": {"sku": "SKU-B200", "name": "Control Unit Pro", "stock": 23, "unit_price_chf": 2450.0},
            "SKU-C300": {"sku": "SKU-C300", "name": "Maintenance Kit", "stock": 0, "unit_price_chf": 120.0},
        }
        self._orders: list[dict[str, Any]] = []

    async def fetch(self, resource_id: str) -> dict[str, Any]:
        if resource_id.startswith("ORD-"):
            for order in self._orders:
                if order["id"] == resource_id:
                    return dict(order)
            raise KeyError(f"ERP order '{resource_id}' not found")
        product = self._inventory.get(resource_id)
        if not product:
            raise KeyError(f"ERP product '{resource_id}' not found")
        return dict(product)

    async def check_inventory(self, sku: str, quantity: int) -> dict[str, Any]:
        product = self._inventory.get(sku)
        if not product:
            return {"available": False, "reason": "SKU not found", "sku": sku}
        stock = product["stock"]
        return {
            "available": stock >= quantity,
            "sku": sku,
            "requested": quantity,
            "in_stock": stock,
            "unit_price_chf": product["unit_price_chf"],
        }

    async def push(self, payload: dict[str, Any]) -> dict[str, Any]:
        order_id = f"ORD-{len(self._orders) + 1001}"
        order = {
            "id": order_id,
            "status": "draft",
            "lines": payload.get("lines", []),
            "customer_ref": payload.get("customer_ref"),
            "total_chf": sum(
                line.get("quantity", 0) * line.get("unit_price_chf", 0) for line in payload.get("lines", [])
            ),
        }
        self._orders.append(order)
        return {"status": "created", "id": order_id, "system": self.system_name, "order": order}

    async def health_check(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "system": self.system_name,
            "products": len(self._inventory),
            "orders": len(self._orders),
        }
