class Scope:
    def __init__(self, key, typ, path, available_supplier_types, demand):
        self.key = key
        self.type = typ
        self.path = path
        self.demand = demand
        self.available_supplier_types = available_supplier_types


def merge_suppliers(original, merge_op):
    merged = {}
    if not merge_op.get("clear", False):
        merged.update(original)
    merged.update(merge_op.get("add", {}))
    for key in merge_op.get("remove", []):
        merged.pop(key, None)
    return merged


def global_demand(props):
    key = props.get("key")
    _type = props.get("type")
    path = props.get("path")
    suppliers = props.get("suppliers", {})

    if not key or not _type or not path:
        raise ValueError("Key, Type, and Path are required in global_demand.")

    supplier_func = suppliers.get(_type)
    if supplier_func:
        available_supplier_types = list(suppliers.keys())
        scope = Scope(
            key, _type, path, available_supplier_types, create_scoped_demand(props)
        )
        return supplier_func(props.get("data"), scope)
    else:
        raise RuntimeError(f"Supplier not found for type: {_type} at path: {path}")


def create_scoped_demand(super_props):
    def demand_func(props):
        demand_key = props.get("key", super_props["key"])
        if "type" not in props:
            raise ValueError("Type is required in scoped demand.")

        path = list(super_props["path"])  # shallow copy
        path.append({"key": demand_key, "type": props["type"]})

        new_suppliers = merge_suppliers(
            super_props["suppliers"], props.get("suppliers", {})
        )

        return global_demand(
            {
                "key": demand_key,
                "type": props["type"],
                "path": path,
                "data": props.get("data"),
                "suppliers": new_suppliers,
            }
        )

    return demand_func


def supply_demand(root_supplier, suppliers):
    suppliers_copy = dict(suppliers)
    suppliers_copy["$$root"] = root_supplier
    return global_demand(
        {
            "key": "root",
            "type": "$$root",
            "path": [{"key": "root", "type": "$$root"}],
            "suppliers": suppliers_copy,
        }
    )


def cached(supplier):
    cache = {"called": False, "value": None}

    def wrapped(data, scope):
        if data is not None:
            raise ValueError("cached suppliers do not accept data.")

        if cache["called"]:
            return cache["value"]

        # Not called yet, do the work
        cache["called"] = True
        cache["value"] = supplier(None, scope)
        return cache["value"]

    return wrapped
