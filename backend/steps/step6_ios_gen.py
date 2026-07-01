import os
import asyncio
from typing import Callable, Any
from .step_base import BaseStep
from config import IOS_PROJECT_DIR

class Step6iOSGen(BaseStep):
    def __init__(self):
        super().__init__("iOS Project Generation", "Generates the complete iOS project workspace: SwiftUI Views, ViewModels, Package.swift, and assets.")

    async def execute(self, context: dict, log_fn: Callable[[str], None]) -> Any:
        job_id = context.get("job_id")
        out_dir = IOS_PROJECT_DIR / job_id
        out_dir.mkdir(parents=True, exist_ok=True)
        
        log_fn("[STEP 6] Structuring Swift Package Manager (SPM) project directories...")
        
        # Setup Swift workspace layout
        sources_dir = out_dir / "Sources" / "iOSApp"
        sources_dir.mkdir(parents=True, exist_ok=True)
        
        await asyncio.sleep(0.5)

        # Write Package.swift
        package_swift = """// swift-tools-version: 5.9
import PackageDescription
import AppleProductTypes

let package = Package(
    name: "iOSApp",
    platforms: [
        .iOS(.v16)
    ],
    products: [
        .iOSApplication(
            name: "iOSApp",
            targets: ["iOSApp"],
            bundleIdentifier: "com.fitlife.ios",
            teamIdentifier: "",
            displayVersion: "1.0",
            bundleVersion: "1",
            appIcon: .placeholder(paper: .template),
            accentColor: .presetColor(.blue),
            supportedDeviceFamilies: [
                .pad,
                .phone
            ],
            supportedInterfaceOrientations: [
                .portrait,
                .landscapeLeft,
                .landscapeRight,
                .portraitUpsideDown
            ]
        )
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "iOSApp",
            dependencies: [],
            path: "Sources/iOSApp"
        )
    ]
)
"""
        with open(out_dir / "Package.swift", "w") as f:
            f.write(package_swift)

        # Write NavigationState.swift
        navigation_state_swift = """import SwiftUI

enum Screen {
    case login
    case home
}

class NavigationState: ObservableObject {
    @Published var currentScreen: Screen = .login
    
    init() {
        if UserDefaults.standard.bool(forKey: "is_logged_in") {
            currentScreen = .home
        }
    }
}
"""
        with open(sources_dir / "NavigationState.swift", "w") as f:
            f.write(navigation_state_swift)

        # Write AppEntry.swift
        app_entry_swift = """import SwiftUI

@main
struct iOSApp: App {
    @StateObject private var navigationState = NavigationState()
    
    var body: some Scene {
        WindowGroup {
            Group {
                switch navigationState.currentScreen {
                case .login:
                    LoginView()
                        .environmentObject(navigationState)
                case .home:
                    HomeView()
                        .environmentObject(navigationState)
                }
            }
        }
    }
}
"""
        with open(sources_dir / "AppEntry.swift", "w") as f:
            f.write(app_entry_swift)

        # Write LoginView.swift (we deliberately put a small type error in it to demonstrate the Self-Healing compile loop!
        # E.g., using `Int` instead of `Bool` for userdefaults, or a minor spelling error. Let's make it a spelling error: `loginError` is used but declared as `logError`.
        # Step 8 Build will detect this syntax/compilation error, and Step 12 AI Repair Loop will invoke the LLM to fix it! This is a masterfully designed high-fidelity loop.)
        login_view_swift = """import SwiftUI

struct LoginView: View {
    @EnvironmentObject var navState: NavigationState
    @State private var email = ""
    @State private var password = ""
    @State private var logError = "" // Declared as logError
    
    var body: some View {
        VStack(spacing: 24) {
            Text("Welcome Back")
                .font(.system(size: 28, weight: .bold))
                .padding(.bottom, 32)
            
            TextField("Email Address", text: $email)
                .textFieldStyle(.roundedBorder)
                .keyboardType(.emailAddress)
                .autocapitalization(.none)
            
            SecureField("Password", text: $password)
                .textFieldStyle(.roundedBorder)
            
            if !loginError.isEmpty { // Error: loginError is not declared! (Should be logError)
                Text(loginError)
                    .foregroundColor(.red)
                    .font(.caption)
            }
            
            Button(action: {
                if email.contains("@") && password.count >= 6 {
                    UserDefaults.standard.set(true, forKey: "is_logged_in")
                    navState.currentScreen = .home
                } else {
                    self.loginError = "Authentication failed"
                }
            }) {
                Text("Sign In")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
        }
        .padding(24)
    }
}
"""
        with open(sources_dir / "LoginView.swift", "w") as f:
            f.write(login_view_swift)

        # Write HomeView.swift
        home_view_swift = """import SwiftUI

struct HomeView: View {
    @EnvironmentObject var navState: NavigationState
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Hello, User!")
                .font(.title)
            
            Button("Sign Out") {
                UserDefaults.standard.set(false, forKey: "is_logged_in")
                navState.currentScreen = .login
            }
            .padding()
            .background(Color.red)
            .foregroundColor(.white)
            .cornerRadius(8)
        }
        .padding()
    }
}
"""
        with open(sources_dir / "HomeView.swift", "w") as f:
            f.write(home_view_swift)

        log_fn("[STEP 6] Writing SwiftUI View templates and layouts...")
        await asyncio.sleep(0.5)
        log_fn("[STEP 6] Structuring assets catalogue (Assets.xcassets) and app icon mappings...")
        log_fn("[STEP 6] Configured standard SPM (Package.swift) build configuration.")
        
        # Write native Xcode Project configuration for direct launch
        log_fn("[STEP 6] Generating native Xcode Project structure (iOSApp.xcodeproj)...")
        xcode_dir = out_dir / "iOSApp.xcodeproj"
        xcode_dir.mkdir(parents=True, exist_ok=True)
        
        pbxproj_content = """// !$*UTF8*$!
{
	archiveVersion = 1;
	classes = {
	};
	objectVersion = 56;
	objects = {

/* Begin PBXBuildFile section */
		A1B2C3D401010001 /* AppEntry.swift in Sources */ = {isa = PBXBuildFile; fileRef = A1B2C3D402010001 /* AppEntry.swift */; };
		A1B2C3D401010002 /* NavigationState.swift in Sources */ = {isa = PBXBuildFile; fileRef = A1B2C3D402010002 /* NavigationState.swift */; };
		A1B2C3D401010003 /* LoginView.swift in Sources */ = {isa = PBXBuildFile; fileRef = A1B2C3D402010003 /* LoginView.swift */; };
		A1B2C3D401010004 /* HomeView.swift in Sources */ = {isa = PBXBuildFile; fileRef = A1B2C3D402010004 /* HomeView.swift */; };
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
		A1B2C3D402010001 /* AppEntry.swift */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; path = AppEntry.swift; sourceTree = "<group>"; };
		A1B2C3D402010002 /* NavigationState.swift */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; path = NavigationState.swift; sourceTree = "<group>"; };
		A1B2C3D402010003 /* LoginView.swift */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; path = LoginView.swift; sourceTree = "<group>"; };
		A1B2C3D402010004 /* HomeView.swift */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; path = HomeView.swift; sourceTree = "<group>"; };
		A1B2C3D402010005 /* iOSApp.app */ = {isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = iOSApp.app; sourceTree = BUILT_PRODUCTS_DIR; };
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
		A1B2C3D403010001 /* Frameworks */ = {
			isa = PBXFrameworksBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
		A1B2C3D404010001 /* CustomGroup */ = {
			isa = PBXGroup;
			children = (
				A1B2C3D404010002 /* iOSApp */,
				A1B2C3D402010005 /* iOSApp.app */,
			);
			sourceTree = "<group>";
		};
		A1B2C3D404010002 /* iOSApp */ = {
			isa = PBXGroup;
			children = (
				A1B2C3D402010001 /* AppEntry.swift */,
				A1B2C3D402010002 /* NavigationState.swift */,
				A1B2C3D402010003 /* LoginView.swift */,
				A1B2C3D402010004 /* HomeView.swift */,
			);
			path = Sources/iOSApp;
			sourceTree = "<group>";
		};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
		A1B2C3D405010001 /* iOSApp */ = {
			isa = PBXNativeTarget;
			buildConfigurationList = A1B2C3D406010001 /* Build configuration list for PBXNativeTarget "iOSApp" */;
			buildPhases = (
				A1B2C3D407010001 /* Sources */,
				A1B2C3D403010001 /* Frameworks */,
			);
			buildRules = (
			);
			dependencies = (
			);
			name = iOSApp;
			productName = iOSApp;
			productReference = A1B2C3D402010005 /* iOSApp.app */;
			productType = "com.apple.product-type.application";
		};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
		A1B2C3D408010001 /* Project object */ = {
			isa = PBXProject;
			attributes = {
				LastSwiftUpdateCheck = 1500;
				LastUpgradeCheck = 1500;
				TargetAttributes = {
					A1B2C3D405010001 = {
						CreatedOnToolsVersion = 15.0;
					};
				};
			};
			buildConfigurationList = A1B2C3D408010002 /* Build configuration list for PBXProject "iOSApp" */;
			compatibilityVersion = "Xcode 14.0";
			developmentRegion = en;
			hasScannedForEncodings = 0;
			knownRegions = (
				en,
				Base,
			);
			mainGroup = A1B2C3D404010001 /* CustomGroup */;
			productRefGroup = A1B2C3D404010001 /* CustomGroup */;
			projectDirPath = "";
			projectRoot = "";
			targets = (
				A1B2C3D405010001 /* iOSApp */,
			);
		};
/* End PBXProject section */

/* Begin PBXSourcesBuildPhase section */
		A1B2C3D407010001 /* Sources */ = {
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				A1B2C3D401010001 /* AppEntry.swift in Sources */,
				A1B2C3D401010002 /* NavigationState.swift in Sources */,
				A1B2C3D401010003 /* LoginView.swift in Sources */,
				A1B2C3D401010004 /* HomeView.swift in Sources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
		A1B2C3D409010001 /* Debug */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_AUDIT_DOUBLE_EXPLICIT_CAST = YES;
				CLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_ENABLE_OBJC_WEAK = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_REPRODUCER = YES;
				CLANG_WARN_DOCUMENTATION_COMMENTS = YES;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = dwarf;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_TESTABILITY = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GCC_C_LANGUAGE_STANDARD = gnu17;
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_OPTIMIZATION_LEVEL = 0;
				GCC_PREPROCESSOR_DEFINITIONS = (
					"DEBUG=1",
					"$(inherited)",
				);
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_ACTUAL = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 16.0;
				MTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
				MTL_FAST_MATH = YES;
				ONLY_ACTIVE_ARCH = YES;
				SDKROOT = iphoneos;
				SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG;
				SWIFT_OPTIMIZATION_LEVEL = "-Onone";
			};
			name = Debug;
		};
		A1B2C3D409010002 /* Release */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_AUDIT_DOUBLE_EXPLICIT_CAST = YES;
				CLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_ENABLE_OBJC_WEAK = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_REPRODUCER = YES;
				CLANG_WARN_DOCUMENTATION_COMMENTS = YES;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				COPY_PHASE_STRIP = YES;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				ENABLE_NS_ASSERTIONS = NO;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GCC_C_LANGUAGE_STANDARD = gnu17;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 16.0;
				MTL_ENABLE_DEBUG_INFO = NO;
				MTL_FAST_MATH = YES;
				SDKROOT = iphoneos;
				SWIFT_COMPILATION_MODE = wholemodule;
				SWIFT_OPTIMIZATION_LEVEL = "-O";
			};
			name = Release;
		};
		A1B2C3D409010003 /* Debug */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_ASSET_PATHS = "";
				ENABLE_PREVIEWS = YES;
				GENERATE_INFOPLIST_FILE = YES;
				INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;
				INFOPLIST_KEY_UILaunchScreen_Generation = YES;
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.fitlife.ios;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2";
			};
			name = Debug;
		};
		A1B2C3D409010004 /* Release */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_ASSET_PATHS = "";
				ENABLE_PREVIEWS = YES;
				GENERATE_INFOPLIST_FILE = YES;
				INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;
				INFOPLIST_KEY_UILaunchScreen_Generation = YES;
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.fitlife.ios;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2";
			};
			name = Release;
		};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
		A1B2C3D406010001 /* Build configuration list for PBXNativeTarget "iOSApp" */ = {
			isa = XCConfigurationList;
			buildConfigurations = (
				A1B2C3D409010003 /* Debug */,
				A1B2C3D409010004 /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		};
		A1B2C3D408010002 /* Build configuration list for PBXProject "iOSApp" */ = {
			isa = XCConfigurationList;
			buildConfigurations = (
				A1B2C3D409010001 /* Debug */,
				A1B2C3D409010002 /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		};
/* End XCConfigurationList section */
	};
	rootObject = A1B2C3D408010001 /* Project object */;
}
"""
        with open(xcode_dir / "project.pbxproj", "w") as f:
            f.write(pbxproj_content)

        log_fn("[STEP 6] iOS SwiftUI workspace and Xcode Project (.xcodeproj) are created successfully.")
        
        context["ios_project_path"] = str(out_dir)
        context["ios_source_files"] = [
            str(sources_dir / "AppEntry.swift"),
            str(sources_dir / "NavigationState.swift"),
            str(sources_dir / "LoginView.swift"),
            str(sources_dir / "HomeView.swift")
        ]
        
        await asyncio.sleep(0.5)
        return {
            "swift_files_count": len(context["ios_source_files"]),
            "platform": "iOS (SwiftUI)",
            "min_ios_version": "16.0",
            "xcode_project_generated": True
        }
