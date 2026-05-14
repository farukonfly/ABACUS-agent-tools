"""Initialize the MCP server used by Abacus Agent tools."""

import os
import inspect
import logging
from functools import wraps
from pprint import pformat


logger = logging.getLogger(__name__)


def _format_mcp_arguments(func, *args, **kwargs) -> str:
    """Format tool arguments as a friendly key-value block."""

    try:
        signature = inspect.signature(func)
        bound = signature.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        arguments = bound.arguments
    except Exception:
        arguments = {f"arg_{index}": value for index, value in enumerate(args)}
        arguments.update(kwargs)

    if not arguments:
        return "  (no arguments)"

    lines = []
    for key, value in arguments.items():
        rendered = pformat(value, width=88, compact=False, sort_dicts=True)
        rendered_lines = rendered.splitlines() or [""]
        if len(rendered_lines) == 1:
            lines.append(f"  {key} = {rendered_lines[0]}")
            continue

        lines.append(f"  {key} =")
        lines.extend(f"    {line}" for line in rendered_lines)

    return "\n".join(lines)


def _log_mcp_tool_call(tool_name, func):
    """Wrap a tool callable so every call and its result is logged."""

    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.info("MCP tool call: %s\n%s", tool_name, _format_mcp_arguments(func, *args, **kwargs))
            result = await func(*args, **kwargs)
            logger.info("MCP tool %s returned:\n%s", tool_name, pformat(result, width=88))
            return result

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger.info("MCP tool call: %s\n%s", tool_name, _format_mcp_arguments(func, *args, **kwargs))
        result = func(*args, **kwargs)
        logger.info("MCP tool %s returned:\n%s", tool_name, pformat(result, width=88))
        return result

    return sync_wrapper


def _wrap_mcp_tool_registration(mcp_instance):
    """Patch the MCP tool decorator so all registered tools are logged."""

    original_tool = mcp_instance.tool

    def logged_tool(*tool_args, **tool_kwargs):
        decorator = original_tool(*tool_args, **tool_kwargs)

        def register(func):
            return decorator(_log_mcp_tool_call(func.__name__, func))

        return register

    mcp_instance.tool = logged_tool

port = os.environ.get("ABACUSAGENT_PORT", "50001")
host = os.environ.get("ABACUSAGENT_HOST", "0.0.0.0")
model = os.environ.get("ABACUSAGENT_MODEL", "fastmcp")

if model == "dp":
    from dp.agent.server import CalculationMCPServer
    mcp = CalculationMCPServer("ABACUSAGENT", port=port, host=host)
    _wrap_mcp_tool_registration(mcp)
elif model == "fastmcp":
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("ABACUSAGENT", port=port, host=host)
    _wrap_mcp_tool_registration(mcp)
elif model == "test": # For unit test of models
    class MCP:
        def tool(self):
            def decorator(func):
                return func
            return decorator
    mcp = MCP()
    _wrap_mcp_tool_registration(mcp)
else:
    print("Please set the environment variable ABACUSAGENT_MODEL to dp, fastmcp or test.")
    raise ValueError("Invalid ABACUSAGENT_MODEL. Please set it to dp, fastmcp or test.")
