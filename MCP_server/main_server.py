from fastmcp import FastMCP


# Create an instance of FastMCP server
mcp = FastMCP("My server")

# Add a simple tool to the server
@mcp.tool
def greet_tool(name: str) -> str:
    return f"Hello, {name}!"

# Run the server
if __name__ == "__main__":
    mcp.run()