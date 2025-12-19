"""
Economic Simulation System

Simulates supply/demand economics affecting prices and narrative.
Locations have different resource availability and trade opportunities.

Features:
- Location-based pricing
- Supply/demand fluctuations
- Trade route effects
- Economic narrative hooks
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import random


class ResourceType(Enum):
    """Types of tradeable resources."""
    FUEL = "fuel"
    FOOD = "food"
    PARTS = "parts"
    WEAPONS = "weapons"
    MEDICINE = "medicine"
    DATA = "data"
    LUXURY = "luxury"
    CONTRABAND = "contraband"


class EconomicCondition(Enum):
    """Economic conditions of a location."""
    PROSPEROUS = "prosperous"  # Lower prices, high availability
    STABLE = "stable"          # Normal prices
    STRUGGLING = "struggling"  # Higher prices, lower availability
    CRISIS = "crisis"          # Very high prices, scarcity
    BLOCKADED = "blockaded"    # Extreme prices, severe scarcity


@dataclass
class ResourcePrice:
    """Price and availability of a resource."""
    resource_type: ResourceType
    base_price: int
    current_price: int
    availability: float  # 0-1, how much is available
    trend: str = "stable"  # rising, falling, stable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_type": self.resource_type.value,
            "base_price": self.base_price,
            "current_price": self.current_price,
            "availability": self.availability,
            "trend": self.trend,
        }


@dataclass
class LocationEconomy:
    """Economic state of a location."""
    location_id: str
    condition: EconomicCondition
    prices: Dict[ResourceType, ResourcePrice] = field(default_factory=dict)
    exports: List[ResourceType] = field(default_factory=list)  # Cheap here
    imports: List[ResourceType] = field(default_factory=list)  # Expensive here
    special_goods: List[str] = field(default_factory=list)     # Unique items

    def to_dict(self) -> Dict[str, Any]:
        return {
            "location_id": self.location_id,
            "condition": self.condition.value,
            "prices": {k.value: v.to_dict() for k, v in self.prices.items()},
            "exports": [e.value for e in self.exports],
            "imports": [i.value for i in self.imports],
            "special_goods": self.special_goods,
        }


# Base prices for resources
BASE_PRICES = {
    ResourceType.FUEL: 10,
    ResourceType.FOOD: 5,
    ResourceType.PARTS: 20,
    ResourceType.WEAPONS: 50,
    ResourceType.MEDICINE: 30,
    ResourceType.DATA: 25,
    ResourceType.LUXURY: 100,
    ResourceType.CONTRABAND: 75,
}

# Economic condition modifiers
CONDITION_MODIFIERS = {
    EconomicCondition.PROSPEROUS: {"price": 0.8, "availability": 1.2},
    EconomicCondition.STABLE: {"price": 1.0, "availability": 1.0},
    EconomicCondition.STRUGGLING: {"price": 1.3, "availability": 0.7},
    EconomicCondition.CRISIS: {"price": 2.0, "availability": 0.3},
    EconomicCondition.BLOCKADED: {"price": 3.0, "availability": 0.1},
}


class EconomicSystem:
    """
    Engine for economic simulation.

    Features:
    - Dynamic pricing by location
    - Supply/demand modeling
    - Trade opportunity detection
    - Economic narrative hooks
    """

    def __init__(self):
        self._locations: Dict[str, LocationEconomy] = {}
        self._player_credits: int = 100
        self._trade_history: List[Dict[str, Any]] = []

    def register_location(
        self,
        location_id: str,
        condition: EconomicCondition = EconomicCondition.STABLE,
        exports: List[ResourceType] = None,
        imports: List[ResourceType] = None
    ):
        """Register a location's economy."""
        economy = LocationEconomy(
            location_id=location_id,
            condition=condition,
            exports=exports or [],
            imports=imports or [],
        )

        # Initialize prices
        self._calculate_prices(economy)
        self._locations[location_id.lower()] = economy

    def _calculate_prices(self, economy: LocationEconomy):
        """Calculate current prices for a location."""
        condition_mod = CONDITION_MODIFIERS[economy.condition]

        for resource_type, base_price in BASE_PRICES.items():
            price_modifier = condition_mod["price"]
            availability = condition_mod["availability"]

            # Exports are cheaper
            if resource_type in economy.exports:
                price_modifier *= 0.7
                availability *= 1.5

            # Imports are more expensive
            if resource_type in economy.imports:
                price_modifier *= 1.4
                availability *= 0.6

            # Add some randomness
            price_modifier *= random.uniform(0.9, 1.1)
            availability = min(1.0, availability * random.uniform(0.8, 1.0))

            economy.prices[resource_type] = ResourcePrice(
                resource_type=resource_type,
                base_price=base_price,
                current_price=int(base_price * price_modifier),
                availability=round(availability, 2),
                trend=random.choice(["rising", "falling", "stable"]),
            )

    def get_price(
        self,
        location_id: str,
        resource_type: ResourceType
    ) -> Optional[int]:
        """Get current price at a location."""
        economy = self._locations.get(location_id.lower())
        if not economy:
            return None

        price_info = economy.prices.get(resource_type)
        return price_info.current_price if price_info else None

    def get_availability(
        self,
        location_id: str,
        resource_type: ResourceType
    ) -> float:
        """Get resource availability (0-1) at a location."""
        economy = self._locations.get(location_id.lower())
        if not economy:
            return 0.5

        price_info = economy.prices.get(resource_type)
        return price_info.availability if price_info else 0.5

    def find_trade_opportunities(
        self,
        from_location: str,
        to_location: str
    ) -> List[Dict[str, Any]]:
        """Find profitable trade routes between locations."""
        from_econ = self._locations.get(from_location.lower())
        to_econ = self._locations.get(to_location.lower())

        if not from_econ or not to_econ:
            return []

        opportunities = []

        for resource_type in ResourceType:
            from_price = from_econ.prices.get(resource_type)
            to_price = to_econ.prices.get(resource_type)

            if not from_price or not to_price:
                continue

            profit_margin = to_price.current_price - from_price.current_price
            profit_percent = (profit_margin / from_price.current_price) * 100

            if profit_percent > 20:  # At least 20% profit
                opportunities.append({
                    "resource": resource_type.value,
                    "buy_price": from_price.current_price,
                    "sell_price": to_price.current_price,
                    "profit_margin": profit_margin,
                    "profit_percent": round(profit_percent, 1),
                    "buy_availability": from_price.availability,
                    "risk": "low" if from_price.availability > 0.5 else "high",
                })

        # Sort by profit
        opportunities.sort(key=lambda x: x["profit_margin"], reverse=True)
        return opportunities[:5]

    def simulate_market_shift(self, location_id: str):
        """Simulate market changes over time."""
        economy = self._locations.get(location_id.lower())
        if not economy:
            return

        for resource_type, price_info in economy.prices.items():
            # Follow trend
            if price_info.trend == "rising":
                change = random.uniform(0.05, 0.15)
            elif price_info.trend == "falling":
                change = random.uniform(-0.15, -0.05)
            else:
                change = random.uniform(-0.05, 0.05)

            new_price = int(price_info.current_price * (1 + change))
            new_price = max(1, min(new_price, price_info.base_price * 5))
            price_info.current_price = new_price

            # Small chance to change trend
            if random.random() < 0.2:
                price_info.trend = random.choice(["rising", "falling", "stable"])

            # Availability shifts
            avail_change = random.uniform(-0.1, 0.1)
            price_info.availability = max(0.05, min(1.0, price_info.availability + avail_change))

    def get_market_summary(self, location_id: str) -> str:
        """Get a narrative market summary."""
        economy = self._locations.get(location_id.lower())
        if not economy:
            return "Economic data unavailable."

        condition_desc = {
            EconomicCondition.PROSPEROUS: "Markets are thriving",
            EconomicCondition.STABLE: "The economy is stable",
            EconomicCondition.STRUGGLING: "Times are hard",
            EconomicCondition.CRISIS: "The economy is in crisis",
            EconomicCondition.BLOCKADED: "Blockade has strangled trade",
        }

        lines = [condition_desc.get(economy.condition, "Markets operate.")]

        # Find extremes
        cheapest = min(economy.prices.items(), key=lambda x: x[1].current_price)
        most_expensive = max(economy.prices.items(), key=lambda x: x[1].current_price)
        scarcest = min(economy.prices.items(), key=lambda x: x[1].availability)

        lines.append(f"{cheapest[0].value.title()} is plentiful.")
        lines.append(f"{most_expensive[0].value.title()} commands premium prices.")

        if scarcest[1].availability < 0.3:
            lines.append(f"{scarcest[0].value.title()} is scarce.")

        return " ".join(lines)

    def get_narrator_context(self, location_id: str = None) -> str:
        """Generate economic context for narrator."""
        if not location_id:
            return ""

        economy = self._locations.get(location_id.lower())
        if not economy:
            return ""

        lines = [f"[ECONOMY: {location_id}]"]
        lines.append(f"Condition: {economy.condition.value}")

        if economy.exports:
            lines.append(f"Cheap: {', '.join(e.value for e in economy.exports)}")
        if economy.imports:
            lines.append(f"Expensive: {', '.join(i.value for i in economy.imports)}")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize system state."""
        return {
            "locations": {k: v.to_dict() for k, v in self._locations.items()},
            "player_credits": self._player_credits,
            "trade_history": self._trade_history[-20:],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EconomicSystem":
        """Deserialize system state."""
        system = cls()
        system._player_credits = data.get("player_credits", 100)
        system._trade_history = data.get("trade_history", [])
        return system


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ECONOMIC SYSTEM TEST")
    print("=" * 60)

    system = EconomicSystem()

    # Register test locations
    system.register_location(
        "Waystation Alpha",
        EconomicCondition.PROSPEROUS,
        exports=[ResourceType.FUEL, ResourceType.PARTS],
        imports=[ResourceType.FOOD, ResourceType.LUXURY],
    )

    system.register_location(
        "Mining Colony",
        EconomicCondition.STRUGGLING,
        exports=[ResourceType.PARTS],
        imports=[ResourceType.FOOD, ResourceType.MEDICINE],
    )

    system.register_location(
        "Frontier Outpost",
        EconomicCondition.CRISIS,
        imports=[ResourceType.FUEL, ResourceType.WEAPONS, ResourceType.MEDICINE],
    )

    # Test prices
    print("\n--- Prices at Waystation Alpha ---")
    economy = system._locations["waystation alpha"]
    for resource, price in economy.prices.items():
        print(f"{resource.value}: {price.current_price} credits ({price.availability:.0%} available)")

    # Test trade opportunities
    print("\n--- Trade Opportunities: Waystation Alpha -> Frontier Outpost ---")
    opportunities = system.find_trade_opportunities("Waystation Alpha", "Frontier Outpost")
    for opp in opportunities:
        print(f"{opp['resource']}: Buy {opp['buy_price']} -> Sell {opp['sell_price']} ({opp['profit_percent']}% profit)")

    # Test market summary
    print("\n--- Market Summary ---")
    print(system.get_market_summary("Waystation Alpha"))
    print(system.get_market_summary("Frontier Outpost"))
