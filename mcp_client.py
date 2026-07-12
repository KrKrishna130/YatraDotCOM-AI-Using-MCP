import os
import asyncio
import certifi
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

load_dotenv()


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# for MCP implementation need 4 things
# 1.MCP Server 2.MCP client 3.Tools 4.URL & API key which will used inide tools

# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)


client = MultiServerMCPClient(
    {  # yaha hme har MCP server ko list me {} me add krna hota hai
        # yaha Travily add kr rahe hai
        "tavily": {  # chuki Remote MCP server me streamable_http connection rahta hai
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },
# yaha aviationstack add kr rahe hai ye local server hai Git hub se le rahe hai
        "aviationstack": { # yah name=aviationstack change kr skte hai chuki Local MCP server me stdio connection rahta hai
            "transport": "stdio", #local Mcp se comminicate k liye stdio lgta hai
            "command": "uvx",
            "args": [
                "aviationstack-mcp"
            ],
            "env": {
                "AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY
            }
        },
# yaha weather add kr rahe hai
         "weather": {  # chuki Local MCP server me stdio connection rahta hai
            "transport": "stdio",
            # yaha ye wo wala path hoga jaha hamara env file me python.exe hoga
            #  conda create -n travel python=3.11 -y
             # conda activate travel is time ka env location dete hai
             
            # environment location: C:\Users\Krishna Kumar\.conda\envs\travel
            # added / updated specs:
            # - python=3.11
# C:\Users\Krishna Kumar\.conda\envs\travel
# hm local server bna rahe hai n isliye local env ka python lagega  custom_weather_mcp_server.py ko run k liye
            # "command": r"C:\Anaconda3\envs\travel\python.exe",
             "command": r"C:\Users\Krishna Kumar\.conda\envs\travel\python.exe",


            "args": [ # yaha local path pura de denge
                # E:\AI Major Project\YatraDotCOM_MultiAgent_MCP\TripMate-AI-Using-MCP-main\TripMate-AI-Using-MCP-main\custom_weather_mcp_server.py
                # r"D:\Bappy\Coding\Youtube\Deployments\TripMate-AI-Using-MCP\custom_weather_mcp_server.py"
                r"E:\AI Major Project\YatraDotCOM_MultiAgent_MCP\TripMate-AI-Using-MCP-main\TripMate-AI-Using-MCP-main\custom_weather_mcp_server.py"
            ],
            "env": {
                "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
            }
        }

        

        

    }

)




# Check if the client is connected to all servers
async def get_all_tools():

    tools = await client.get_tools()

    print("\nAvailable MCP Tools:\n")

    for tool in tools:
        print(tool.name)




###################################
# Tavlily and Aviation Tools
###################################


search_tool = None
aviation_tools = {}

async def initialize_mcp():

    global search_tool
    global aviation_tools

    if search_tool is not None and aviation_tools:
        return

    tools = await client.get_tools()

    print("\nAvailable MCP Tools:\n")

    for tool in tools:
        print(tool.name)

    search_tool = next(
        tool
        for tool in tools
        if tool.name == "tavily_search"
    )

    aviation_tools = {
        tool.name: tool
        for tool in tools
        if tool.name != "tavily_search"
    }



# yaha Hm search_tool hi lete hai for real time Internet Search 
async def tavily_mcp_search(query: str):
    await initialize_mcp()
    result = await search_tool.ainvoke(
        {
            "query": query
        }
    )
    return result




async def aviation_mcp_call(
    tool_name: str,
    tool_args: dict = None
):

    tools = await client.get_tools()

    tool = next(
        t for t in tools
        if t.name == tool_name
    )

    result = await tool.ainvoke(
        tool_args or {}
    )

    return result






###################################
# Weather Tools
###################################

weather_tool = None
forecast_tool = None


async def initialize_weather_tools():

    global weather_tool, forecast_tool

    if weather_tool is not None:
        return

    tools = await client.get_tools()

    weather_tool = next(
        t for t in tools
        if t.name == "get_current_weather"
    )

    forecast_tool = next(
        t for t in tools
        if t.name == "get_forecast"
    )


async def weather_mcp_search(city: str):

    await initialize_weather_tools()

    return await weather_tool.ainvoke(
        {
            "city": city
        }
    )


async def forecast_mcp_search(city: str):

    await initialize_weather_tools()

    return await forecast_tool.ainvoke(
        {
            "city": city
        }
    )




###################################
# Destination Extractor
###################################

def extract_destination(query: str):

    prompt = f"""
    Extract only the destination city or country.

    Query:
    {query}

    Return only destination name.
    """

    response = llm.invoke(prompt)

    return response.content.strip()


