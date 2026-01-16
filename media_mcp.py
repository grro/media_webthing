from mcp_server import MCPServer
from media import Media

class MediaMCPServer(MCPServer):

    def __init__(self, name: str, port: int, media: Media):
        super().__init__(name, port)
        self.media = media

        @self.mcp.tool(name="get_media_title", description="Retrieves the title of the track or program currently playing. Returns 'Unknown' if nothing is playing.")
        def get_media_title() -> str:
            return self.media.title or "Unknown"

        @self.mcp.tool(name="get_media_source", description="Gets the currently active input source (e.g., 'TUNER', 'TV', 'HDMI').")
        def get_media_source() -> str:
            return self.media.source

        @self.mcp.tool(name="get_media_volume", description="Gets the current volume level as an integer from 0 (mute) to 100 (max volume).")
        def get_media_volume() -> int:
            return self.media.volume

        @self.mcp.tool(name="get_media_power_status", description="Checks if the device is turned on. Returns True if on, False if standby/off.")
        def get_media_power_status() -> bool:
            return self.media.power == 1

        @self.mcp.tool(name="set_media_source", description="Switches the input source. Ensure the device is powered on before switching.")
        def set_media_source(source: str) -> str:
            """
            :param source: The target source. Common values: 'TUNER', 'TV', 'HDMI1', 'HDMI2'.
            """
            valid_sources = ["TUNER", "TV", "HDMI1", "HDMI2"]

            if source not in valid_sources:
                return f"Error: '{source}' is not valid. Allowed: {valid_sources}"

            self.media.set_source(source)
            return f"Successfully switched source to '{source}'"

        @self.mcp.tool(name="set_media_volume", description="Sets the absolute volume level. Range is 0 to 100.")
        def set_media_volume(volume_level: int) -> str:
            """
            :param volume_level: Target volume (0-100).
            """
            if not (0 <= volume_level <= 100):
                return "Error: Volume must be between 0 (mute) and 100 (max volume)."

            self.media.set_volume(volume_level)
            return f"Volume set to {volume_level}"

        @self.mcp.tool(name="set_media_power", description="Turns the device on or off.")
        def set_media_power(turn_on: bool) -> str:
            """
            :param turn_on: True to turn ON, False to turn OFF.
            """
            self.media.set_power(turn_on)
            state = "ON" if turn_on else "OFF"
            return f"Device powered {state}"

