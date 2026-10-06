from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal, Any
from datetime import datetime
from enum import Enum

# --- Agent States ---
class AgentState(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    RETRIEVING = "retrieving"
    EXTRACTING_EVIDENCE = "extracting_evidence"
    ANALYZING_CONFLICTS = "analyzing_conflicts"
    VERIFYING = "verifying"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"

# --- Research Plan ---
class SubQuestion(BaseModel):
    id: str = Field(description="Unique identifier e.g., 'sub-1'")
    question: str = Field(description="Decomposed research sub-question")
    purpose: str = Field(description="Why answering this is crucial for the main question")
    suggested_queries: List[str] = Field(description="Suggested search engine queries")

class ResearchPlan(BaseModel):
    main_question: str = Field(description="The original user research question")
    clarified_scope: str = Field(description="Clarified scope, domains, and key dimensions to investigate")
    information_required: List[str] = Field(description="Key pieces of empirical or factual information needed")
    sub_questions: List[SubQuestion] = Field(description="List of 3 to 5 focused sub-questions")
    search_strategy: str = Field(description="Overall retrieval and search strategy")
    estimated_iterations: int = Field(default=3, description="Estimated tool iterations needed (bounded)")

# --- Tool Execution & Search ---
class SearchResult(BaseModel):
    id: str = Field(description="Unique ID for this result")
    title: str = Field(description="Web page title")
    url: str = Field(description="Web page URL")
    snippet: str = Field(description="Short text snippet from search engine")
    content: Optional[str] = Field(default=None, description="Full extracted text content")
    query: str = Field(description="Query that produced this result")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ToolCallLog(BaseModel):
    id: str = Field(description="Unique tool call ID")
    iteration: int = Field(description="Research loop iteration index")
    tool_name: str = Field(description="Name of tool: web_search | extract_page_content | summarize_source")
    arguments: Dict[str, Any] = Field(description="Arguments passed to the tool")
    summary_result: str = Field(description="Summary of tool execution output")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# --- Evidence Extraction ---
class EvidenceItem(BaseModel):
    id: str = Field(description="Unique evidence ID e.g., 'ev-1'")
    sub_question_id: str = Field(description="ID of the sub-question this evidence addresses")
    claim: str = Field(description="Atomic factual claim or finding extracted from the source")
    verbatim_quote: str = Field(description="Direct quotation or snippet from source establishing provenance")
    source_url: str = Field(description="URL of source")
    source_title: str = Field(description="Title of source document")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in accuracy and clarity (0.0 to 1.0)")
    contradiction_potential: bool = Field(default=False, description="Whether this finding diverges from or contradicts other sources")

class Claim(BaseModel):
    id: str = Field(description="Unique claim ID e.g., 'cl-1'")
    claim_text: str = Field(description="Synthesized claim statement")
    supporting_evidence_ids: List[str] = Field(description="List of EvidenceItem IDs supporting this claim")
    source_urls: List[str] = Field(description="List of source URLs backing this claim")
    consensus_status: Literal["consensus", "conflicting", "unverified", "single_source"] = Field(
        default="consensus", description="Degree of agreement across retrieved evidence"
    )
    notes: Optional[str] = Field(default=None, description="Additional context or caveats")

# --- Conflict Detection ---
class ConflictItem(BaseModel):
    id: str = Field(description="Unique conflict ID e.g., 'conf-1'")
    topic: str = Field(description="The specific sub-topic or empirical claim under dispute")
    claim_a: str = Field(description="First perspective or claimed figure/finding")
    source_a_title: str = Field(description="Title of Source A")
    source_a_url: str = Field(description="Source URL for claim A")
    claim_b: str = Field(description="Competing perspective or claimed figure/finding")
    source_b_title: str = Field(description="Title of Source B")
    source_b_url: str = Field(description="Source URL for claim B")
    possible_reason: str = Field(description="Explanation for divergence (e.g., benchmark methodology, publication date, differing metrics)")
    severity: Literal["minor_nuance", "moderate_divergence", "direct_contradiction"] = Field(
        description="Severity level of the conflict"
    )

# --- Verification & Reflection ---
class ClaimVerification(BaseModel):
    claim_text: str = Field(description="Claim evaluated during reflection")
    supporting_evidence_ids: List[str] = Field(description="Evidence IDs checked")
    is_grounded: bool = Field(description="True if claim has concrete grounding in retrieved evidence quotes")
    verification_notes: str = Field(description="Auditor critique: checks for overstatements or extrapolation")
    grounding_score: float = Field(ge=0.0, le=1.0, description="Verification confidence score (0.0 to 1.0)")

class VerificationResult(BaseModel):
    claims_evaluated: List[ClaimVerification] = Field(description="List of verified claims with grounding status")
    overall_grounding_score: float = Field(ge=0.0, le=1.0, description="Average factual grounding score")
    unsupported_claims_removed_or_flagged: List[str] = Field(
        default_factory=list, description="Claims filtered out or flagged for insufficient source support"
    )
    verification_passed: bool = Field(description="Whether the research dataset meets quality thresholds")
    reflection_critique: str = Field(description="Self-reflective critique of evidence gaps and remaining uncertainties")

# --- Final Synthesis ---
class ComparisonRow(BaseModel):
    dimension: str = Field(description="Dimension, metric, or feature being compared")
    values: Dict[str, str] = Field(description="Mapping of entity/option name to value or description")

class ComparisonTable(BaseModel):
    title: str = Field(description="Table title")
    headers: List[str] = Field(description="Column headers (e.g., ['Metric', 'Option A', 'Option B'])")
    rows: List[ComparisonRow] = Field(description="Comparison table rows")

class KeyFinding(BaseModel):
    headline: str = Field(description="Crisp headline of the finding")
    detailed_explanation: str = Field(description="Thorough explanation with inline citations e.g. [1]")
    evidence_ids: List[str] = Field(description="Associated evidence IDs")
    source_citations: List[str] = Field(description="List of citation tags e.g. ['[1]', '[2]']")
    confidence: Literal["high", "moderate", "low"] = Field(description="Confidence rating based on evidence")

class ReferenceItem(BaseModel):
    citation_index: int = Field(description="Citation index number e.g., 1 for [1]")
    title: str = Field(description="Document or article title")
    url: str = Field(description="Direct URL to source")
    key_contribution: str = Field(description="What specific factual point this reference establishes")

class FinalResearchReport(BaseModel):
    title: str = Field(description="Comprehensive report title")
    executive_summary: str = Field(description="High-level synthesis addressing the core user question")
    research_methodology: str = Field(description="How evidence was decomposed, searched, and verified")
    key_findings: List[KeyFinding] = Field(description="The primary factual conclusions")
    comparison_tables: List[ComparisonTable] = Field(default_factory=list, description="Structured comparative matrices")
    conflicting_information: List[ConflictItem] = Field(default_factory=list, description="Identified disputes and divergence analysis")
    limitations: List[str] = Field(description="Known gaps, scope boundaries, or missing data points")
    conclusion: str = Field(description="Definitive concluding analysis and strategic takeaway")
    references: List[ReferenceItem] = Field(description="Exhaustive list of cited sources with indices matching inline tags")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# --- Real-Time Timeline & API Transfer Schemas ---
class TimelineEvent(BaseModel):
    id: str = Field(description="Unique event ID")
    stage: AgentState = Field(description="Agent lifecycle state")
    message: str = Field(description="Human-readable event message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Optional[Dict[str, Any]] = Field(default=None, description="Optional payload details")

class ResearchSessionState(BaseModel):
    session_id: str
    question: str
    status: AgentState
    progress_percentage: int = 0
    plan: Optional[ResearchPlan] = None
    sources: List[SearchResult] = []
    evidence: List[EvidenceItem] = []
    conflicts: List[ConflictItem] = []
    verification: Optional[VerificationResult] = None
    report: Optional[FinalResearchReport] = None
    timeline: List[TimelineEvent] = []
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StartResearchRequest(BaseModel):
    question: str = Field(min_length=5, description="The complex research question to investigate")
    deep_mode: bool = Field(default=False, description="Enable deeper search iterations if true")

class VerifyClaimRequest(BaseModel):
    claim_text: str = Field(description="Claim text to verify against existing evidence")
    session_id: str = Field(description="Session ID providing evidence context")
