import os
import pytest
import shutil
from pathlib import Path
from steps.step1_upload import Step1Upload
from steps.step3_architecture import Step3Architecture
from steps.step5_pim import Step5PIM
from steps.step7_api_mapping import Step7APIMapping
from steps.step8_build import Step8Build
from steps.step13_unsupported import Step13Unsupported

# Setup test workspace
TEST_BASE = Path(__file__).resolve().parent.parent / "workspace" / "test_run"
TEST_BASE.mkdir(parents=True, exist_ok=True)

@pytest.mark.asyncio
async def test_step1_upload_and_metadata():
    step = Step1Upload()
    # Create dummy file to act as APK
    dummy_apk = TEST_BASE / "test_app.apk"
    with open(dummy_apk, "w") as f:
        f.write("dummy content")

    context = {"apk_path": str(dummy_apk)}
    logs = []
    def log_fn(msg):
        logs.append(msg)

    metadata = await step.execute(context, log_fn)
    assert metadata is not None
    assert metadata["app_name"] == "Test App" or "App" in metadata["app_name"]
    assert "package_name" in metadata
    assert context["metadata"] == metadata

@pytest.mark.asyncio
async def test_step3_architecture_recovery():
    step = Step3Architecture()
    context = {"decompile_path": str(TEST_BASE)}
    logs = []
    def log_fn(msg):
        logs.append(msg)

    result = await step.execute(context, log_fn)
    assert "navigation_graph" in result
    assert len(result["navigation_graph"]["nodes"]) > 0
    assert "storage_findings" in result

@pytest.mark.asyncio
async def test_step5_pim_generation():
    step = Step5PIM()
    context = {}
    logs = []
    def log_fn(msg):
        logs.append(msg)

    pim = await step.execute(context, log_fn)
    assert isinstance(pim, list)
    assert len(pim) > 0
    assert pim[0]["screen"] == "LoginActivity"

@pytest.mark.asyncio
async def test_step7_api_mapping():
    step = Step7APIMapping()
    context = {}
    logs = []
    def log_fn(msg):
        logs.append(msg)

    mappings = await step.execute(context, log_fn)
    assert isinstance(mappings, list)
    assert len(mappings) > 0
    # check that SharedPreferences -> UserDefaults mapping exists
    sp_mapping = next(m for m in mappings if m["android"] == "SharedPreferences")
    assert sp_mapping["ios"] == "UserDefaults"

@pytest.mark.asyncio
async def test_step8_build_self_healing_detection():
    step = Step8Build()
    
    # Create a mock sources dir
    sources_dir = TEST_BASE / "Sources" / "iOSApp"
    sources_dir.mkdir(parents=True, exist_ok=True)
    
    login_view_file = sources_dir / "LoginView.swift"
    
    # 1. Write LoginView with spelling error
    code_with_error = """
    struct LoginView {
        private var logError = ""
        var body: some View {
            Text(loginError)
        }
    }
    """
    with open(login_view_file, "w") as f:
        f.write(code_with_error)

    context = {"job_id": "test_job", "ios_project_path": str(TEST_BASE)}
    logs = []
    def log_fn(msg):
        logs.append(msg)

    # Execute build - should fail
    res1 = await step.execute(context, log_fn)
    assert res1["build_success"] is False
    assert len(res1["errors"]) == 1
    assert "cannot find 'loginError' in scope" in res1["errors"][0]

    # 2. Write LoginView with fixed spelling
    code_fixed = """
    struct LoginView {
        private var loginError = ""
        var body: some View {
            Text(loginError)
        }
    }
    """
    with open(login_view_file, "w") as f:
        f.write(code_fixed)

    # Execute build - should pass
    res2 = await step.execute(context, log_fn)
    assert res2["build_success"] is True
    assert len(res2["errors"]) == 0

@pytest.mark.asyncio
async def test_step13_unsupported_detection():
    step = Step13Unsupported()
    context = {}
    logs = []
    def log_fn(msg):
        logs.append(msg)

    res = await step.execute(context, log_fn)
    assert isinstance(res, list)
    # Check that ARM precompiled native library is detected
    native_lib = next(i for i in res if "ARM binary" in i["details"])
    assert native_lib["severity"] == "HIGH"

# Cleanup test workspace after tests complete
@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    if TEST_BASE.exists():
        shutil.rmtree(TEST_BASE)
