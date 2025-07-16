import unittest

from supply_demand import supply_demand, cached  # etc.


class TestSupplyDemand(unittest.TestCase):
    def test_simple_resolution(self):
        def simple_supplier(data, scope):
            return "simple_value"

        result = supply_demand(simple_supplier, {})
        self.assertEqual(result, "simple_value")

    def test_available_types(self):

        def a_supplier(data, scope):
            return "A"

        def b_supplier(data, scope):
            return "B"

        def main_supplier(data, scope):
            return scope.available_supplier_types

        result = supply_demand(main_supplier, {"a": a_supplier, "b": b_supplier})
        self.assertEqual(result, ["a", "b", "$$root"])

    def test_nested_demand(self):
        def root_supplier(data, scope):
            # Demand 'bar' of type 'baz'
            return "root_" + scope.demand({"key": "bar", "type": "baz"})

        def bar_supplier(data, scope):
            return "nested_value"

        result = supply_demand(root_supplier, {"baz": bar_supplier})
        self.assertEqual(result, "root_nested_value")

    def test_add_and_remove_suppliers(self):
        def main_supplier(data, scope):
            return scope.demand({"key": "a", "type": "alpha"})

        def alpha_supplier(data, scope):
            return "alpha_value"

        # Now, without the supplier, should raise (use assertRaises)
        with self.assertRaises(RuntimeError):
            supply_demand(main_supplier, {})

        # Add alpha - now it works
        result = supply_demand(main_supplier, {"alpha": alpha_supplier})
        self.assertEqual(result, "alpha_value")

        # Removes alpha supplier before demand, should raise
        def removing_supplier(data, scope):
            return scope.demand(
                {"key": "a", "type": "alpha", "suppliers": {"remove": ["alpha"]}}
            )

        with self.assertRaises(RuntimeError):
            supply_demand(removing_supplier, {"alpha": alpha_supplier})

    def test_supply_chain_with_data(self):
        def main_supplier(data, scope):
            # Pass custom data to foo_supplier
            return scope.demand({"key": "foo", "type": "bar", "data": 21})

        def foo_supplier(data, scope):
            return data * 2

        result = supply_demand(main_supplier, {"bar": foo_supplier})
        self.assertEqual(result, 42)

    def test_error_on_missing_type_in_scoped_demand(self):
        def main_supplier(data, scope):
            # Try to demand without specifying type
            try:
                scope.demand({"key": "fail"})
                return None  # Should not reach here
            except ValueError as ex:
                return str(ex)

        result = supply_demand(main_supplier, {})
        self.assertIn("Type is required", result)

    def test_cached(self):
        import asyncio

        async def test_body():
            call_count = [0]

            async def foo_supplier(data, scope):
                call_count[0] += 1
                await asyncio.sleep(0.01)
                return call_count[0]

            async def root_supplier(data, scope):
                fut1 = scope.demand({"key": "foo1", "type": "foo"})
                fut2 = scope.demand({"key": "foo2", "type": "foo"})
                result1, result2 = await asyncio.gather(fut1, fut2)
                return (result1, result2)

            result = await supply_demand(root_supplier, {"foo": cached(foo_supplier)})
            self.assertEqual(result, (1, 1))
            self.assertEqual(call_count[0], 1)

        asyncio.run(test_body())

    def test_path_is_array(self):
        def root_supplier(data, scope):
            self.assertEqual(scope.path, [{"key": "root", "type": "$$root"}])
            # Demand nested, should get appended path
            return scope.demand({"key": "foo", "type": "bar"})

        def foo_supplier(data, scope):
            self.assertEqual(
                scope.path,
                [{"key": "root", "type": "$$root"}, {"key": "foo", "type": "bar"}],
            )
            return "ok"

        supply_demand(root_supplier, {"bar": foo_supplier})

    def test_quick_start_example(self):
        import asyncio

        async def value_supplier(data, scope):
            return 42

        async def root_supplier(data, scope):
            answer = await scope.demand({"type": "value"})
            # Instead of print, we assert result in the test.
            return answer

        suppliers = {"value": value_supplier}
        result = asyncio.run(supply_demand(root_supplier, suppliers))
        self.assertEqual(result, 42)

    def test_dependency_chain_example(self):
        import asyncio

        async def A(data, scope):
            return 1

        async def B(data, scope):
            a_val = await scope.demand({"type": "A"})
            return a_val + 5

        async def root(data, scope):
            result = await scope.demand({"type": "B"})
            return result

        suppliers = {"A": A, "B": B}
        result = asyncio.run(supply_demand(root, suppliers))
        self.assertEqual(result, 6)


if __name__ == "__main__":
    unittest.main()
