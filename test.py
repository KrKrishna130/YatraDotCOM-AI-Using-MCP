import asyncio
# from mcp_client_test import get_all_tools, tavily_mcp_search
from mcp_client import get_all_tools

# yaha hm test kr le rahe hai 
# direct hm isko run krk dekh skte hai=>> python test.py

if __name__ == "__main__":
    asyncio.run(get_all_tools())