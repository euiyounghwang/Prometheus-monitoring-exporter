from mcp.server.fastmcp import FastMCP
import logging
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("mcp-server")

# Create an MCP server
# mcp = FastMCP("MCP 서버")
mcp = FastMCP(name="MCP 서버", port=5100, debug=True)
# mcp = FastMCP(name="MCP 서버", debug=True)

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    message = f"Add {a} and {b}"
    logger.info(message)  # 로거를 통한 로그 출력
    return a + b


@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    log_message = f"Tool echo: {message}"
    logger.info(log_message)  # 로거를 통한 로그 출력
    return message


@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    log_message = f"Prompt echo: {message}"
    logger.info(log_message)
    return f"Please process this message: {message}"


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    log_message = f"Greeting for: {name}"
    logger.info(log_message)
    return f"Hello, {name}!"


@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    log_message = f"Resource echo: {message}"
    logger.info(log_message)
    return f"Resource echo: {message}"


''' http://localhost:8000/sse '''
if __name__ == "__main__":
    logger.info("Starting MCP server...")
    # mcp.run(transport='stdio')
    # transport 옵션을 변경해봅니다
    mcp.run(transport="sse")
    