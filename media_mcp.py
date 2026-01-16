from mcp_server import MCPServer
from media import Media


class MediaMCPServer(MCPServer):

    def __init__(self, name: str, port: int, media : Media):
        super().__init__(name, port)
        self.media = media

        @self.mcp.tool(name="get_media_title", description="Returns the title of the currently playing media.")
        def get_media_title() -> str:
            return self.media.title

        @self.mcp.tool(name="get_media_source", description="Returns the current input source (e.g., 'TUNER', 'TV').")
        def get_media_source() -> str:
            return self.media.source

        @self.mcp.tool(name="get_media_volume", description="Returns the current system volume level.")
        def get_media_volume() -> int:
            return self.media.volume

        @self.mcp.tool(name="get_media_power_status", description="Checks if the device is powered on.")
        def get_media_power_status() -> bool:
            return self.media.power == 1

        @self.mcp.tool(name="set_media_source", description="Changes the active input source.")
        def set_media_source(source: str):
            """
            :param source: The name of the source to switch to.
            """
            self.media.set_source(source)

        @self.mcp.tool(name="set_media_volume", description="Updates the device volume.")
        def set_media_volume(vol: int):
            """
            :param vol: Integer value representing the target volume level.
            """
            self.media.set_volume(vol)

        @self.mcp.tool(name="set_media_power", description="Controls the power state of the media device.")
        def set_media_power(on: bool):
            """
            :param on: Set to True to power on, False to power off.
            """
            self.media.set_power(on)

# npx @modelcontextprotocol/inspector

