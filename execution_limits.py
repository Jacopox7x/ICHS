"""execution_limits.py - Guardiano dell'esecuzione per iCrawler.

Controllo preventivo: si esegue PRIMA dell'azione.
Contabilizzazione: si esegue NEL punto reale di esecuzione (record_*).
Ogni azione ha il proprio contatore e il proprio limite.
"""

from dataclasses import dataclass, field
from time import monotonic


DEFAULT_LIMITS = {
    "max_model_calls": 12,
    "max_tool_calls": 20,
    "max_retries": 2,
    "max_regenerations": 2,
    "max_workflow_seconds": 180,
    "max_input_chars": 20000,
    "max_output_chars": 50000,
    "remaining_budget": float("inf"),
}

# Mappa azione -> (chiave contatore usage, chiave limite)
ACTION_LIMIT_MAP = {
    "model_call": ("model_calls", "max_model_calls"),
    "tool_call": ("tool_calls", "max_tool_calls"),
    "retry": ("retries", "max_retries"),
    "regeneration": ("regenerations", "max_regenerations"),
}


@dataclass
class ExecutionContext:
    limits: dict = field(default_factory=lambda: dict(DEFAULT_LIMITS))
    usage: dict = field(default_factory=lambda: {
        "model_calls": 0,
        "tool_calls": 0,
        "retries": 0,
        "regenerations": 0,
    })
    started_at: float = field(default_factory=monotonic)

    def elapsed(self) -> float:
        return monotonic() - self.started_at


def check_execution_limits(ctx, action: str, estimated_cost: float = 0) -> dict:
    # 1. Azione conosciuta?
    if action not in ACTION_LIMIT_MAP:
        return {
            "allowed": False,
            "limit_name": "unknown_action",
            "reason": f"Azione sconosciuta: {action}",
            "remaining": None,
        }

    counter_key, limit_key = ACTION_LIMIT_MAP[action]
    used = ctx.usage[counter_key]
    maximum = ctx.limits[limit_key]

    # 2. Limite specifico dell'azione richiesta
    if used >= maximum:
        return {
            "allowed": False,
            "limit_name": limit_key,
            "reason": f"Limite raggiunto: {limit_key} ({used}/{maximum})",
            "remaining": 0,
        }

    # 3. Timeout workflow (vale per tutte le azioni)
    elapsed = ctx.elapsed()
    if elapsed >= ctx.limits["max_workflow_seconds"]:
        return {
            "allowed": False,
            "limit_name": "workflow_seconds",
            "reason": f"Timeout workflow ({elapsed:.1f}s)",
            "remaining": 0,
        }

    # 4. Budget (controllo preventivo, non contabilizzazione cumulativa)
    if estimated_cost > ctx.limits["remaining_budget"]:
        return {
            "allowed": False,
            "limit_name": "budget",
            "reason": "Budget stimato insufficiente",
            "remaining": ctx.limits["remaining_budget"],
        }

    return {
        "allowed": True,
        "limit_name": None,
        "reason": "Limiti rispettati",
        "remaining": maximum - used,
    }


def record_model_call(ctx) -> None:
    ctx.usage["model_calls"] += 1


def record_tool_call(ctx) -> None:
    ctx.usage["tool_calls"] += 1


def record_retry(ctx) -> None:
    ctx.usage["retries"] += 1


def record_regeneration(ctx) -> None:
    ctx.usage["regenerations"] += 1


def check_input_size(ctx, text: str) -> dict:
    if len(text) > ctx.limits["max_input_chars"]:
        return {
            "allowed": False,
            "limit_name": "input_chars",
            "reason": f"Input troppo grande ({len(text)} > {ctx.limits['max_input_chars']})",
            "remaining": 0,
        }
    return {"allowed": True, "limit_name": None, "reason": "OK", "remaining": None}


def check_output_size(ctx, text: str) -> dict:
    if len(text) > ctx.limits["max_output_chars"]:
        return {
            "allowed": False,
            "limit_name": "output_chars",
            "reason": f"Output troppo grande ({len(text)} > {ctx.limits['max_output_chars']})",
            "remaining": 0,
        }
    return {"allowed": True, "limit_name": None, "reason": "OK", "remaining": None}
