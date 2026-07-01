import asyncio
from typing import Callable, Any
from .step_base import BaseStep

class Step5PIM(BaseStep):
    def __init__(self):
        super().__init__("Platform Independent Model (PIM)", "Compiles reverse-engineered resources and metadata into a unified JSON-based screen/action model.")

    async def execute(self, context: dict, log_fn: Callable[[str], None]) -> Any:
        log_fn("[STEP 5] Translating screen declarations and semantics into Platform Independent Model (PIM)...")
        await asyncio.sleep(0.5)

        # Build JSON model representing the screens and components
        pim_model = [
            {
                "screen": "LoginActivity",
                "title": "Welcome Back",
                "components": [
                    {"id": "tvTitle", "type": "Text", "value": "Welcome Back", "style": {"fontSize": "large", "fontWeight": "bold"}},
                    {"id": "etEmail", "type": "TextField", "placeholder": "Email Address", "keyboard": "email"},
                    {"id": "etPassword", "type": "SecureField", "placeholder": "Password", "keyboard": "password"},
                    {"id": "btnLogin", "type": "Button", "label": "Sign In"}
                ],
                "actions": [
                    {
                        "trigger": "btnLogin",
                        "validation": {
                            "email": "contains('@')",
                            "password": "length >= 6"
                        },
                        "success": {
                            "storage": {"key": "is_logged_in", "type": "UserDefaults", "value": True},
                            "navigation": "HomeActivity"
                        },
                        "failure": {
                            "action": "toast",
                            "message": "Authentication failed"
                        }
                    }
                ]
            },
            {
                "screen": "HomeActivity",
                "title": "Home Dashboard",
                "components": [
                    {"id": "tvWelcome", "type": "Text", "value": "Hello, User!", "style": {"fontSize": "medium"}},
                    {"id": "btnSignOut", "type": "Button", "label": "Sign Out"}
                ],
                "actions": [
                    {
                        "trigger": "btnSignOut",
                        "success": {
                            "storage": {"key": "is_logged_in", "type": "UserDefaults", "value": False},
                            "navigation": "LoginActivity"
                        }
                    }
                ]
            }
        ]

        context["pim_model"] = pim_model
        log_fn(f"[STEP 5] PIM generated with {len(pim_model)} screen schemas.")
        log_fn("[STEP 5] Saved PIM model mapping.")
        
        await asyncio.sleep(0.5)
        return pim_model
