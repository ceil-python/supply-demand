from SupplyDemand import supply_demand, Scope, DemandReturn
import asyncio
from typing import Any, Optional


async def first_supplier(data: Optional[Any], scope: Scope) -> str:
    print("First supplier function called. Simulating delay...")
    await asyncio.sleep(2)  # Simulates a delay of 2 seconds
    print("First supplier function completed.")
    return "1st"


async def second_supplier(data: Optional[Any], scope: Scope) -> str:
    print("Second supplier function called.")
    return "2nd"


async def third_supplier(data: Optional[Any], scope: Scope) -> DemandReturn:
    print("Third supplier function called.")
    return await scope["demand"](
        {
            "type": "first",
        }
    )


async def root_supplier(data: Optional[Any], scope: Scope) -> None:
    print("Root supplier function called.")
    res = await scope["demand"](
        {
            "type": "third",
            "suppliers_merge": {"add": {"third": third_supplier}},
        }
    )
    print("Root supplier function call result is:", res)


if __name__ == "__main__":
    suppliers = {"first": first_supplier, "second": second_supplier}
    asyncio.run(supply_demand(root_supplier, suppliers))
