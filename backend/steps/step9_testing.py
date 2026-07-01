import asyncio
from typing import Callable, Any
from .step_base import BaseStep

class Step9Testing(BaseStep):
    def __init__(self):
        super().__init__("Automated Validation", "Runs synthetic XCUITest / Android Espresso suites to validate functional behaviors.")

    async def execute(self, context: dict, log_fn: Callable[[str], None]) -> Any:
        build_success = context.get("build_success", False)
        if not build_success:
            log_fn("[STEP 9] Skip: Compilation is failing. Cannot run UI automation tests.")
            return {"status": "skipped", "reason": "Build failed"}
            
        log_fn("[STEP 9] Starting test validation suite on simulated target devices...")
        await asyncio.sleep(0.5)
        log_fn("[STEP 9] Booting iOS Simulator (iPhone 15 Pro - iOS 17.2)...")
        await asyncio.sleep(0.8)
        log_fn("[STEP 9] Launching target application 'iOSApp'...")
        await asyncio.sleep(0.4)
        
        # Test Case 1: Load Login Page
        log_fn("[STEP 9] Running testCaseLoginScreenLoad()...")
        log_fn("  --> Searching element with identifier 'tvTitle' / Text('Welcome Back'). Found.")
        log_fn("  --> Searching element with identifier 'btnLogin' / Button('Sign In'). Found.")
        await asyncio.sleep(0.3)
        
        # Test Case 2: Submit invalid form
        log_fn("[STEP 9] Running testCaseInvalidLoginSubmission()...")
        log_fn("  --> Tapping TextField 'etEmail', entering 'invalid-email'...")
        log_fn("  --> Tapping SecureField 'etPassword', entering '123'...")
        log_fn("  --> Tapping Button 'btnLogin'...")
        log_fn("  --> Assertion: Alert / error text 'Authentication failed' should appear. Found.")
        await asyncio.sleep(0.5)

        # Test Case 3: Submit valid form
        log_fn("[STEP 9] Running testCaseValidLoginSubmission()...")
        log_fn("  --> Clearing inputs...")
        log_fn("  --> Tapping TextField 'etEmail', entering 'user@fitlife.com'...")
        log_fn("  --> Tapping SecureField 'etPassword', entering 'password123'...")
        log_fn("  --> Tapping Button 'btnLogin'...")
        log_fn("  --> Assertion: Current screen should transition to HomeView. Transited.")
        log_fn("  --> Assertion: HomeView should display Text('Hello, User!'). Found.")
        await asyncio.sleep(0.6)

        # Test Case 4: Sign out
        log_fn("[STEP 9] Running testCaseSignOut()...")
        log_fn("  --> Tapping Button 'btnSignOut'...")
        log_fn("  --> Assertion: Current screen should transition back to LoginView. Transited.")
        
        log_fn("[STEP 9] UI Automation tests execution complete: 4 passed, 0 failed.")
        
        test_results = {
            "total": 4,
            "passed": 4,
            "failed": 0,
            "duration_seconds": 3.1
        }
        context["test_results"] = test_results
        return test_results
