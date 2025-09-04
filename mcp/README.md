
#### MCP(Model Context Protocol) 
<i>An MCP (Model Context Protocol) server in Python is a program that exposes tools, resources, and prompts to be consumed by large language models (LLMs) or other AI applications


#### Python V3.9 Install
```bash
pip install pymcp
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
    my_server.run()
```