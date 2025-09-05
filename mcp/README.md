
#### MCP(Model Context Protocol) 
<i>An MCP (Model Context Protocol) server in Python is a program that exposes tools, resources, and prompts to be consumed by large language models (LLMs) or other AI applications


#### Python V3.9 Install
```bash
pip install pymcp
pip install mcp[cli]
pip install uv

# Claude Desktop 
mcp install server.py
mcp dev server.py
```

#### MCP Server tools
```bash
from mcp.server import FunctionTool

# MCP 도구로 만들 파이썬 함수 정의
@FunctionTool
def add_numbers(a: int, b: int) -> int:
    return a + b

# 여러 함수를 하나의 MCP 서버에 추가할 수도 있습니다.
# (예시: convert_functions를 이용하는 방법)
```

#### MCP Server Object/add Function
```bash
from mcp.server import Server

# 서버 객체 정의
my_server = Server("my_python_tool_server")

# 정의된 함수를 서버에 추가
my_server.add_functions([add_numbers])
```

#### MCP Server run
```bash
if __name__ == "__main__":
    logger.info("Starting MCP server...")
    # mcp.run(transport='stdio')
    # transport 옵션을 변경해봅니다
    # mcp.run(transport="sse")
    mcp.run(transport='stdio')

2025-09-05 08:45:08,605 - mcp.server.lowlevel.server - DEBUG - Initializing server 'MCP 서버'
2025-09-05 08:45:08,606 - mcp.server.lowlevel.server - DEBUG - Registering handler for ListToolsRequest
2025-09-05 08:45:08,606 - mcp.server.lowlevel.server - DEBUG - Registering handler for CallToolRequest
2025-09-05 08:45:08,607 - mcp.server.lowlevel.server - DEBUG - Registering handler for ListResourcesRequest
2025-09-05 08:45:08,607 - mcp.server.lowlevel.server - DEBUG - Registering handler for ReadResourceRequest
2025-09-05 08:45:08,608 - mcp.server.lowlevel.server - DEBUG - Registering handler for PromptListRequest
2025-09-05 08:45:08,608 - mcp.server.lowlevel.server - DEBUG - Registering handler for GetPromptRequest
2025-09-05 08:45:08,609 - mcp.server.lowlevel.server - DEBUG - Registering handler for ListResourceTemplatesRequest
2025-09-05 08:45:08,635 - mcp-server - INFO - Starting MCP server...
2025-09-05 08:45:08,649 - asyncio - DEBUG - Using proactor: IocpProactor

    mcp.run(transport="sse")

2025-09-05 08:47:11,160 - mcp.server.lowlevel.server - DEBUG - Initializing server 'MCP 서버'
2025-09-05 08:47:11,161 - mcp.server.lowlevel.server - DEBUG - Registering handler for ListToolsRequest
2025-09-05 08:47:11,161 - mcp.server.lowlevel.server - DEBUG - Registering handler for CallToolRequest
2025-09-05 08:47:11,162 - mcp.server.lowlevel.server - DEBUG - Registering handler for ListResourcesRequest
2025-09-05 08:47:11,162 - mcp.server.lowlevel.server - DEBUG - Registering handler for ReadResourceRequest
2025-09-05 08:47:11,162 - mcp.server.lowlevel.server - DEBUG - Registering handler for PromptListRequest
2025-09-05 08:47:11,163 - mcp.server.lowlevel.server - DEBUG - Registering handler for GetPromptRequest
2025-09-05 08:47:11,163 - mcp.server.lowlevel.server - DEBUG - Registering handler for ListResourceTemplatesRequest
2025-09-05 08:47:11,185 - mcp-server - INFO - Starting MCP server...
2025-09-05 08:47:11,195 - asyncio - DEBUG - Using proactor: IocpProactor
2025-09-05 08:47:11,202 - mcp.server.sse - DEBUG - SseServerTransport initialized with endpoint: /messages/
INFO:     Started server process [32312]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

```


