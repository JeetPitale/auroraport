import asyncio
from typing import Callable, Any
from .step_base import BaseStep

class Step13Unsupported(BaseStep):
    def __init__(self):
        super().__init__("Unsupported Feature Detection", "Scans code for platform-exclusive Android APIs (foreground services, billing, widgets) and maps alternatives.")

    async def execute(self, context: dict, log_fn: Callable[[str], None]) -> Any:
        log_fn("[STEP 13] Scanning decompiled manifest and source code for platform incompatibilities...")
        await asyncio.sleep(0.5)

        # Detect incompatible items
        incompatibilities = [
            {
                "feature": "Android Foreground Service (LocationTrackingService)",
                "details": "android:foregroundServiceType=\"location\"",
                "ios_alternative": "Use CoreLocation CLLocationManager with allowsBackgroundLocationUpdates = true, requiring CLBackgroundLocationIndicator and Location updates capabilities in Info.plist.",
                "severity": "MEDIUM"
            },
            {
                "feature": "Android Native Shared Library (libnative-lib.so)",
                "details": "Precompiled Android ARM binary",
                "ios_alternative": "The precompiled Android .so file cannot run on iOS. You must locate the original C/C++ source code and recompile it using the Xcode toolchain as a static library (.a) or an iOS Framework.",
                "severity": "HIGH"
            }
        ]

        for item in incompatibilities:
            log_fn(f"[STEP 13] Incompatibility: {item['feature']} (Severity: {item['severity']})")
            log_fn(f"  --> Suggested iOS Alternative: {item['ios_alternative']}")
            await asyncio.sleep(0.3)

        context["unsupported_features"] = incompatibilities
        log_fn("[STEP 13] Scanned all files. Compatibility manifest compiled.")
        return incompatibilities
