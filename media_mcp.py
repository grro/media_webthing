import logging
from mcplib.server import MCPServer
from media import Media


class MediaMCPServer(MCPServer):
    """
    MCP Server for controlling a media player or AV receiver.
    Provides volume control, source switching, and radio station management.
    """

    def __init__(self, name: str, port: int, media: Media):
        super().__init__(name, port)
        self.media = media
        # Define fixed inputs once to ensure consistency
        self._fixed_inputs = ["TV", "SAT", "MEDIAPLAYER", "BLUERAY", "AUX2", "TUNER", "HEOS"]

        @self.mcp.tool(name="get_media_status",
                       description="Returns the full status of the media device including power, volume, source, and available stations.")
        def get_media_status() -> str:
            """
            Provides a comprehensive snapshot of the device state.
            Use this to check what is playing and what options are available.
            """
            try:
                power_state = "ON" if self.media.power == 1 else "OFF/STANDBY"
                volume = self.media.volume
                current_source = self.media.source
                current_title = self.media.title or "None"

                stations = self.media.stationnames
                stations_str = ", ".join(stations) if isinstance(stations, list) else str(stations)

                return (
                    f"Media Player Status ({power_state}):\n"
                    f"- Source: {current_source}\n"
                    f"- Current Title/Station: {current_title}\n"
                    f"- Volume: {volume}/100\n"
                    f"- Available Radio Stations: {stations_str}\n"
                    f"- Valid Fixed Inputs: {', '.join(self._fixed_inputs)}"
                )
            except Exception as e:
                logging.warning(f"Failed to get media status: {e}", exc_info=True)
                return f"Error: Could not retrieve media status. {str(e)}"

        @self.mcp.tool(name="set_media_source",
                       description="Switches the input source or selects a radio station (e.g., 'TV' or 'SWR1').")
        def set_media_source(source: str) -> str:
            """
            Changes the active input. Device must be powered ON.
            Args:
                source: Target input name or radio station name.
            """
            try:
                available_stations = self.media.stationnames if isinstance(self.media.stationnames, list) else []

                if source not in self._fixed_inputs and source not in available_stations:
                    return f"Error: '{source}' is invalid. Use a fixed input {self._fixed_inputs} OR a station from the status report."

                self.media.set_source(source)
                return f"Successfully switched source to '{source}'"
            except Exception as e:
                return f"Error: Failed to set source to '{source}'. {str(e)}"

        @self.mcp.tool(name="set_media_volume",
                       description="Sets the absolute volume (0-100).")
        def set_media_volume(volume_level: int) -> str:
            if not (0 <= volume_level <= 100):
                return "Error: Volume must be between 0 and 100."
            self.media.set_volume(volume_level)
            return f"Success: Volume adjusted to {volume_level}."

        @self.mcp.tool(name="set_media_power",
                       description="Turns the device ON or OFF (Standby).")
        def set_media_power(turn_on: bool) -> str:
            self.media.set_power(turn_on)
            state = "ON" if turn_on else "OFF"
            return f"Success: Device is now {state}."