from supply_demand import supply_demand
import asyncio


async def first_supplier(data, scope) -> str:
    print("First supplier function called. Simulating delay...")
    await asyncio.sleep(2)  # Simulates a delay of 2 seconds
    print("First supplier function completed.")
    return "1st"


async def second_supplier(data, scope) -> str:
    print("Second supplier function called.")
    return "2nd"


async def third_supplier(data, scope):
    print("Third supplier function called.")
    return await scope.demand(
        {
            "type": "first",
        }
    )


async def root_supplier(data, scope):
    print("Root supplier function called.")
    res = await scope.demand(
        {
            "type": "third",
            "suppliers": {"add": {"third": third_supplier}},
        }
    )
    print("Root supplier function call result is:", res)


if __name__ == "__main__":
    suppliers = {"first": first_supplier, "second": second_supplier}
    asyncio.run(supply_demand(root_supplier, suppliers))
