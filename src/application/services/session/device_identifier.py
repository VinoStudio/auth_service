from typing import Dict, Any
from dataclasses import dataclass
from user_agents import parse
import hashlib
import orjson

from src.application.base.interface.request import RequestProtocol

import src.application.dto as dto


@dataclass
class DeviceIdentifier:
    @staticmethod
    def generate_device_info(request: RequestProtocol) -> dto.DeviceInformation:

        user_agent_string = request.headers.get("user-agent", "")
        headers = dict(request.headers)

        # Parse user agent for device information
        ua = parse(user_agent_string)

        # Create a shorter representation of user agent
        browser = f"{ua.browser.family} {ua.browser.version_string}"
        os = f"{ua.os.family} {ua.os.version_string}"

        # Create simplified user agent string (limit to 100 chars)
        simplified_ua = f"{browser} on {os}"[:100]

        # Create device info JSON
        device_info = {
            "browser_family": ua.browser.family,
            "os_family": ua.os.family,
            "device": ua.get_device(),
            "accept_lang": headers.get("accept-language", ""),
            "accept_encoding": headers.get("accept-encoding", ""),
        }

        # here we are creating bytes of parsed user_agent and then store it in session database model for future usage
        fingerprint_json = orjson.dumps(device_info)
        device_hash = hashlib.sha256(fingerprint_json).hexdigest()

        device_data: dto.DeviceInformation = dto.DeviceInformation(
            device_info=fingerprint_json,
            device_id=device_hash,
            user_agent=simplified_ua,
        )

        return device_data

    @staticmethod
    def verify_device(
        request: RequestProtocol, jwt_device_data: Dict[str, str]
    ) -> bool:
        # Generate current device fingerprint
        current_device = DeviceIdentifier.generate_device_info(request)

        # Main verification: device hash must match
        if current_device.device_id != jwt_device_data.get("di"):
            # Optional fuzzy matching here if needed
            return False

        return True
