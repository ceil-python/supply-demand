# supply-demand

[![PyPI version](https://img.shields.io/pypi/v/supply-demand.svg)](https://pypi.org/project/supply-demand/)
[![License](https://img.shields.io/pypi/l/supply-demand.svg)](LICENSE)

A Python library for **dependency orchestration** and “demand/supply” resolution (function DI).  
Inspired by advanced dependency-injection/inversion control, it lets you register “supplier” functions by key/type, and lets any supplier **demand** values from others—allowing composition, overrides, and dependency graphs.

---

## Features

- Register “suppliers” (functions) for different types/keys
- Compose suppliers & override them dynamically
- Pass context (scope) through demands
- Supports both, **async** and sync suppliers
- Auto-manages dependency graph and supplier registry merging

---

## Installation

```bash
pip install supply-demand
```
or

```bash
python -m pip install supply-demand
```
or

```bash
python3 -m pip install supply-demand
```

---

## Quick Start

```python
from supply_demand import supply_demand
import asyncio

async def value_supplier(data, scope):
    return 42

async def root_supplier(data, scope):
    answer = await scope.demand({"type": "value"})
    print("Supply chain returned:", answer)

suppliers = {"value": value_supplier}
asyncio.run(supply_demand(root_supplier, suppliers))
```

---

## Example: Dependency Chain

```python
async def A(data, scope):
    return 1

async def B(data, scope):
    a_val = await scope.demand({"type": "A"})
    return a_val + 5

async def root(data, scope):
    result = await scope.demand({"type": "B"})
    print("Result:", result)

suppliers = {"A": A, "B": B}
asyncio.run(supply_demand(root, suppliers))
```

_Output: `Result: 6`_

---

## API

### supply_demand(root_supplier, suppliers)

- **root_supplier:** Callable `(data, scope)`. The entry point.
- **suppliers:** Dict of `{type: supplier_func, ...}`.

### context.demand(props)

- **props["type"]** — The supplier type to demand.
- Can override suppliers, pass data, etc.

---

## Advanced

Supports registry extension, override, additive/clear logic via:

```python
scope.demand({
  "type": "X",
  "suppliers": {"add": {"X": custom_x_supplier}}
})
```

---

## License

MIT
