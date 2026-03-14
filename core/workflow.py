"""
Influencer Factory — LangGraph Workflow

Pipeline: Context Builder → Stratejist → Görsel+Video Prompter → Copywriter → Kalite Kontrol → Derleyici

Sistemdeki yeri: main.py tarafından compile edilir ve çalıştırılır.
Etkilediği dosyalar: Tüm agents/*.py (node'lar), core/state.py (state tipi)
"""
import logging
from langgraph.graph import StateGraph, END, START

from core.state import InfluencerState
from agents.context_builder import context_builder_node
from agents.strategist import strategist_node
from agents.visual_prompter import visual_prompter_node
from agents.copywriter import copywriter_node
from agents.quality_controller import quality_controller_node
from agents.compiler import compiler_node

logger = logging.getLogger(__name__)

MAX_RETRY = 2


def quality_decision(state: InfluencerState):
    """
    Kalite Kontrol kararına göre akışı yönlendirir.
    Onay → compiler (derleyici)
    Ret + retry limiti aşılmamış → visual_prompter (yeniden üret)
    Ret + retry limiti aşılmış → compiler (zorla ilerle)
    """
    report = state.get("quality_report")
    retry_count = state.get("retry_count", 0)

    if not report:
        logger.warning("[WORKFLOW] Kalite raporu yok → compiler'a gönderiliyor")
        return "compiler"

    if report.approved:
        logger.info(f"[WORKFLOW] ✅ Kalite onayı (puan: {report.score})")
        return "compiler"
    elif retry_count >= MAX_RETRY:
        logger.warning(f"[WORKFLOW] ⚠️ Retry limiti aşıldı ({retry_count}/{MAX_RETRY}). Derleyiciye ilerliyor.")
        return "compiler"
    else:
        logger.info(f"[WORKFLOW] 🔄 Kalite reddetti (puan: {report.score}). Yeniden üretim (retry {retry_count}/{MAX_RETRY})")
        return "visual_prompter"


def context_needed(state: InfluencerState):
    """
    Persona cache varsa Context Builder atlanır.
    """
    persona = state.get("persona")
    if persona:
        logger.info("[WORKFLOW] Persona cache'den yüklendi → Context Builder atlanıyor")
        return "strategist"
    else:
        return "context_builder"


def compile_workflow():
    """
    Ana pipeline'ı derler ve döndürür.

    Akış:
    [START] → context_needed → Context Builder → Stratejist
                             ↘ (cache varsa) → Stratejist
    Stratejist → Visual+Video Prompter → Copywriter → Kalite Kontrol
    Kalite Kontrol → (Onay) → Compiler → [END]
                   → (Ret) → Visual+Video Prompter (retry)
    """
    workflow = StateGraph(InfluencerState)

    # Node'ları ekle
    workflow.add_node("context_builder", context_builder_node)
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("visual_prompter", visual_prompter_node)
    workflow.add_node("copywriter", copywriter_node)
    workflow.add_node("quality_controller", quality_controller_node)
    workflow.add_node("compiler", compiler_node)

    # Giriş noktası: START → conditional → context_builder veya strategist
    workflow.add_conditional_edges(
        START,
        context_needed,
        {
            "context_builder": "context_builder",
            "strategist": "strategist",
        }
    )

    # Sabit edge'ler
    workflow.add_edge("context_builder", "strategist")
    workflow.add_edge("strategist", "visual_prompter")
    workflow.add_edge("visual_prompter", "copywriter")
    workflow.add_edge("copywriter", "quality_controller")
    workflow.add_edge("compiler", END)

    # Conditional edge: Kalite Kontrol kararı
    workflow.add_conditional_edges(
        "quality_controller",
        quality_decision,
        {
            "compiler": "compiler",
            "visual_prompter": "visual_prompter",
        }
    )

    app = workflow.compile()
    logger.info("[WORKFLOW] ✅ Pipeline derlendi.")
    return app
