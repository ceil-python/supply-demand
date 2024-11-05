import asyncio
from typing import Any, Callable, Dict, Optional, Union

# Type aliases
DemandProps = Dict[str, Any]
SupplyMethod = Callable[[Optional[Any], "Scope"], Any]
AsyncSupplyMethod = Callable[[Optional[Any], "Scope"], Any]
ScopedDemand = Callable[[DemandProps], Any]
SuppliersMerge = Dict[str, Union[bool, Dict[str, AsyncSupplyMethod], list]]
ExtendSuppliersMethod = Callable[
    [Dict[str, AsyncSupplyMethod], SuppliersMerge], Dict[str, AsyncSupplyMethod]
]
DemandReturn = Any


class Scope:
    def __init__(self, key: str, _type: str, path: str, demand: ScopedDemand):
        self.key = key
        self.type = _type
        self.path = path
        self.demand = demand


def merge_suppliers(
    original: Dict[str, AsyncSupplyMethod], merge_op: SuppliersMerge
) -> Dict[str, AsyncSupplyMethod]:
    merged = {}
    if not merge_op.get("clear", False):
        merged.update(original)
    merged.update(merge_op.get("add", {}))
    for key in merge_op.get("remove", []):
        merged.pop(key, None)
    return merged


async def global_demand(props: DemandProps) -> DemandReturn:
    key = props["key"]
    _type = props["type"]
    path = props["path"]
    suppliers = props.get("suppliers", {})

    if not key or not _type or not path:
        raise ValueError("Key, Type, and Path are required in global_demand.")

    print(f"Global demand called with: Key: {key}, Type: {_type}, Path: {path}")

    supplier_func = suppliers.get(_type)
    if supplier_func:
        print(f"Calling supplier for type: {_type}")
        return await supplier_func(
            props.get("data"),
            {
                "key": key,
                "type": _type,
                "path": path,
                "demand": create_scoped_demand(props),
            },
        )
    print(f"Supplier not found for type: {_type}")


def create_scoped_demand(super_props: DemandProps) -> ScopedDemand:
    async def demand_func(props: DemandProps) -> DemandReturn:
        demand_key = props.get("key", super_props["key"])

        if "type" not in props:
            raise ValueError("Type is required in scoped demand.")

        path = f"{super_props['path']}/{demand_key}({props['type']})"
        new_suppliers = merge_suppliers(
            super_props["suppliers"], props.get("suppliers_merge", {})
        )

        return await global_demand(
            {
                "key": demand_key,
                "type": props["type"],
                "path": path,
                "data": props.get("data"),
                "suppliers": new_suppliers,
            }
        )

    return demand_func


async def supply_demand(
    root_supplier: AsyncSupplyMethod, suppliers: Dict[str, AsyncSupplyMethod]
) -> DemandReturn:
    suppliers_copy = suppliers.copy()
    suppliers_copy["$$root"] = root_supplier
    return await global_demand(
        {
            "key": "root",
            "type": "$$root",
            "path": "root",
            "suppliers": suppliers_copy,
        }
    )


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
