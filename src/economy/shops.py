from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ShopItem:
    item_id: str
    price: int
    stock: int = 1
    tags: List[str] = field(default_factory=list)


@dataclass
class ShopInventory:
    pool: List[ShopItem]
    rotation_size: int = 3
    rotation_duration: int = 2
    service_fee_pct: float = 0.1

    def rotate(
        self, rng: random.Random, current_session: int, previous: Optional[Dict[str, ShopItem]] = None
    ) -> Tuple[Dict[str, ShopItem], int]:
        candidates = list(self.pool)
        rng.shuffle(candidates)
        chosen = candidates[: self.rotation_size]
        inventory = {item.item_id: ShopItem(**item.__dict__) for item in chosen}
        expires_at = current_session + self.rotation_duration
        return inventory, expires_at

    def apply_service_fee(self, amount: int) -> int:
        return int(round(amount * (1 + self.service_fee_pct)))


class ShopManager:
    """Handles NPC service fees and time-limited shop rotations."""

    def __init__(
        self,
        pool: List[ShopItem],
        rotation_size: int = 3,
        rotation_duration: int = 2,
        service_fee_pct: float = 0.1,
    ):
        self.inventory_helper = ShopInventory(
            pool=pool,
            rotation_size=rotation_size,
            rotation_duration=rotation_duration,
            service_fee_pct=service_fee_pct,
        )
        self.active_inventory: Dict[str, ShopItem] = {}
        self.expires_at_session: int = 0
        self._rng = random.Random(1337)

    def ensure_rotation(self, current_session: int) -> None:
        if not self.active_inventory or current_session >= self.expires_at_session:
            self.active_inventory, self.expires_at_session = self.inventory_helper.rotate(
                self._rng, current_session, previous=self.active_inventory
            )

    def list_items(self, current_session: int) -> Dict[str, ShopItem]:
        self.ensure_rotation(current_session)
        return self.active_inventory

    def purchase(self, item_id: str, balance: int, current_session: int) -> Tuple[int, Optional[ShopItem]]:
        self.ensure_rotation(current_session)
        if current_session >= self.expires_at_session:
            return balance, None

        item = self.active_inventory.get(item_id)
        if not item or item.stock <= 0:
            return balance, None

        total_price = self.inventory_helper.apply_service_fee(item.price)
        if balance < total_price:
            return balance, None

        item.stock -= 1
        balance -= total_price
        return balance, item
