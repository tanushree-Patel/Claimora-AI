from langgraph.graph import END, StateGraph

from app.graph.checkpointer import get_checkpointer
from app.graph.nodes_extraction import extract_data, validate_compliance
from app.graph.nodes_review import finalize, human_review, retrieve_codes
from app.graph.state import ClaimGraphState


def _after_extract(state: ClaimGraphState) -> str:
    return "failed" if state.get("status") == "EXTRACTION_FAILED" else "continue"


def _after_validate(state: ClaimGraphState) -> str:
    return "failed" if state.get("status") == "VALIDATION_FAILED" else "continue"


def build_claim_graph():
    graph = StateGraph(ClaimGraphState)

    graph.add_node("extract_data", extract_data)
    graph.add_node("validate_compliance", validate_compliance)
    graph.add_node("retrieve_codes", retrieve_codes)
    graph.add_node("human_review", human_review)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("extract_data")
    graph.add_conditional_edges("extract_data", _after_extract, {"failed": END, "continue": "validate_compliance"})
    graph.add_conditional_edges("validate_compliance", _after_validate, {"failed": END, "continue": "retrieve_codes"})
    graph.add_edge("retrieve_codes", "human_review")
    graph.add_edge("human_review", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile(checkpointer=get_checkpointer())