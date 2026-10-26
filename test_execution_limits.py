import unittest
from time import monotonic
from execution_limits import (
    ExecutionContext,
    check_execution_limits,
    record_model_call,
    record_tool_call,
    record_retry,
    record_regeneration,
    check_input_size,
    check_output_size,
)


class TestExecutionLimits(unittest.TestCase):

    def test_1_workflow_valido(self):
        ctx = ExecutionContext()
        for _ in range(5):
            d = check_execution_limits(ctx, "model_call")
            self.assertTrue(d["allowed"])
            record_model_call(ctx)
        self.assertEqual(ctx.usage["model_calls"], 5)

    def test_2_limite_model_calls(self):
        ctx = ExecutionContext()
        ctx.limits["max_model_calls"] = 3
        for _ in range(3):
            self.assertTrue(check_execution_limits(ctx, "model_call")["allowed"])
            record_model_call(ctx)
        d = check_execution_limits(ctx, "model_call")
        self.assertFalse(d["allowed"])
        self.assertEqual(d["limit_name"], "max_model_calls")

    def test_3_limite_tool_calls(self):
        ctx = ExecutionContext()
        ctx.limits["max_tool_calls"] = 2
        for _ in range(2):
            self.assertTrue(check_execution_limits(ctx, "tool_call")["allowed"])
            record_tool_call(ctx)
        d = check_execution_limits(ctx, "tool_call")
        self.assertFalse(d["allowed"])
        self.assertEqual(d["limit_name"], "max_tool_calls")

    def test_4_esaurimento_retry(self):
        ctx = ExecutionContext()
        ctx.limits["max_retries"] = 2
        record_retry(ctx)
        record_retry(ctx)
        d = check_execution_limits(ctx, "retry")
        self.assertFalse(d["allowed"])
        self.assertEqual(d["limit_name"], "max_retries")

    def test_5_esaurimento_rigenerazioni(self):
        ctx = ExecutionContext()
        ctx.limits["max_regenerations"] = 1
        record_regeneration(ctx)
        d = check_execution_limits(ctx, "regeneration")
        self.assertFalse(d["allowed"])
        self.assertEqual(d["limit_name"], "max_regenerations")

    def test_6_timeout(self):
        ctx = ExecutionContext()
        ctx.limits["max_workflow_seconds"] = 10
        ctx.started_at = monotonic() - 11
        d = check_execution_limits(ctx, "model_call")
        self.assertFalse(d["allowed"])
        self.assertEqual(d["limit_name"], "workflow_seconds")

    def test_7_input_troppo_grande(self):
        ctx = ExecutionContext()
        ctx.limits["max_input_chars"] = 100
        d = check_input_size(ctx, "x" * 101)
        self.assertFalse(d["allowed"])
        self.assertEqual(d["limit_name"], "input_chars")

    def test_8_output_troppo_grande(self):
        ctx = ExecutionContext()
        ctx.limits["max_output_chars"] = 100
        d = check_output_size(ctx, "x" * 101)
        self.assertFalse(d["allowed"])
        self.assertEqual(d["limit_name"], "output_chars")

    def test_9_budget_insufficiente(self):
        ctx = ExecutionContext()
        ctx.limits["remaining_budget"] = 0.5
        d = check_execution_limits(ctx, "model_call", estimated_cost=1.0)
        self.assertFalse(d["allowed"])
        self.assertEqual(d["limit_name"], "budget")

    def test_10_budget_predefinito_infinito(self):
        ctx = ExecutionContext()
        self.assertEqual(ctx.limits["remaining_budget"], float("inf"))
        d = check_execution_limits(ctx, "model_call", estimated_cost=1_000_000)
        self.assertTrue(d["allowed"])

    def test_11_remaining_corretto(self):
        ctx = ExecutionContext()
        ctx.limits["max_model_calls"] = 10
        record_model_call(ctx)
        record_model_call(ctx)
        d = check_execution_limits(ctx, "model_call")
        self.assertEqual(d["remaining"], 8)

    def test_12_azione_sconosciuta(self):
        ctx = ExecutionContext()
        d = check_execution_limits(ctx, "qualcosa_di_strano")
        self.assertFalse(d["allowed"])
        self.assertEqual(d["limit_name"], "unknown_action")

    def test_13_indipendenza_limiti(self):
        ctx = ExecutionContext()
        ctx.limits["max_tool_calls"] = 1
        record_tool_call(ctx)
        self.assertFalse(check_execution_limits(ctx, "tool_call")["allowed"])
        d = check_execution_limits(ctx, "model_call")
        self.assertTrue(d["allowed"])


if __name__ == "__main__":
    unittest.main()
