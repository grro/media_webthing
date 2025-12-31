from mcp_server import MCPServer
from media import Media


class MediaMCPServer(MCPServer):

    def __init__(self, name: str, port: int, media : Media):
        super().__init__(name, port)
        self.media = media

        @self.mcp.resource("media://title")
        def get_title() -> str:
            """Returns the title of the currently playing media."""
            return self.media.title

        @self.mcp.resource("media://source")
        def get_source() -> str:
            """Returns the current input source (e.g., 'TUNER', 'TV')."""
            return self.media.source

        @self.mcp.resource("media://volume")
        def get_volume() -> int:
            """Returns the current system volume level."""
            return self.media.volume

        @self.mcp.resource("media://power")
        def get_power() -> bool:
            """Checks if the device is powered on ."""
            return self.media.power == 1

        @self.mcp.tool()
        def set_source(source: str):
            """
            Changes the active input source.
            :param source: The name of the source to switch to.
            """
            self.media.set_source(source)

        @self.mcp.tool()
        def set_volume(vol: int):
            """
            Updates the device volume.
            :param vol: Integer value representing the target volume level.
            """
            self.media.set_volume(vol)

        @self.mcp.tool()
        def set_power(on: bool):
            """
            Controls the power state of the media device.
            :param on: Set to True to power on, False to power off.
            """
            self.media.set_power(on)

# npx @modelcontextprotocol/inspector

