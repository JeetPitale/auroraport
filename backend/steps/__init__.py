from .step_base import BaseStep
from .step1_upload import Step1Upload
from .step2_decompile import Step2Decompile
from .step3_architecture import Step3Architecture
from .step4_semantic import Step4Semantic
from .step5_pim import Step5PIM
from .step6_ios_gen import Step6iOSGen
from .step7_api_mapping import Step7APIMapping
from .step8_build import Step8Build
from .step9_testing import Step9Testing
from .step10_visual_comp import Step10VisualComp
from .step11_func_comp import Step11FuncComp
from .step12_repair_loop import Step12RepairLoop
from .step13_unsupported import Step13Unsupported
from .step14_deliverables import Step14Deliverables

ALL_STEPS = [
    Step1Upload(),
    Step2Decompile(),
    Step3Architecture(),
    Step4Semantic(),
    Step5PIM(),
    Step6iOSGen(),
    Step7APIMapping(),
    Step8Build(),
    Step9Testing(),
    Step10VisualComp(),
    Step11FuncComp(),
    Step12RepairLoop(),
    Step13Unsupported(),
    Step14Deliverables()
]
