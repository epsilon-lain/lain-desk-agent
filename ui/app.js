const agentName = document.querySelector("#agentName");
const renameDialog = document.querySelector("#renameDialog");
const renameForm = document.querySelector("#renameForm");
const renameInput = document.querySelector("#renameInput");
const taskForm = document.querySelector("#taskForm");
const taskInput = document.querySelector("#taskInput");
const primaryAction = document.querySelector("#primaryAction");
const statusText = document.querySelector("#statusText");
const proposalPanel = document.querySelector("#proposalPanel");
const proposalTitle = document.querySelector("#proposalTitle");
const proposalSummary = document.querySelector("#proposalSummary");
const proposalFacts = document.querySelector("#proposalFacts");
const actionContractPanel = document.querySelector("#actionContractPanel");
const actionContractTitle = document.querySelector("#actionContractTitle");
const actionContractSummary = document.querySelector("#actionContractSummary");
const actionContractFacts = document.querySelector("#actionContractFacts");
const clickReadinessPanel = document.querySelector("#clickReadinessPanel");
const clickReadinessSummary = document.querySelector("#clickReadinessSummary");
const clickReadinessReasons = document.querySelector("#clickReadinessReasons");
const clickReadinessChecks = document.querySelector("#clickReadinessChecks");
const clickReadinessDebug = document.querySelector("#clickReadinessDebug");
const clickReadinessDebugJson = document.querySelector("#clickReadinessDebugJson");
const runtimeProfile = document.querySelector("#runtimeProfile");
const runtimePlanner = document.querySelector("#runtimePlanner");
const runtimeDesktopControl = document.querySelector("#runtimeDesktopControl");
const runtimeActuation = document.querySelector("#runtimeActuation");
const runtimeVerification = document.querySelector("#runtimeVerification");
const runtimeClick = document.querySelector("#runtimeClick");
const runtimeResourceGuard = document.querySelector("#runtimeResourceGuard");
const executionPolicyProfile = document.querySelector("#executionPolicyProfile");
const executionPolicyList = document.querySelector("#executionPolicyList");
const executionPolicyProfiles = document.querySelector("#executionPolicyProfiles");
const permissionProfileStatus = document.querySelector("#permissionProfileStatus");
const capabilitiesList = document.querySelector("#capabilitiesList");
const demoScenarioPanel = document.querySelector("#demoScenarioPanel");
const demoScenarioSelect = document.querySelector("#demoScenarioSelect");
const demoTaskInput = document.querySelector("#demoTaskInput");
const runDemoScenarioButton = document.querySelector("#runDemoScenario");
const demoScenarioSelectedName = document.querySelector("#demoScenarioSelectedName");
const demoScenarioDescription = document.querySelector("#demoScenarioDescription");
const demoScenarioFakeApp = document.querySelector("#demoScenarioFakeApp");
const demoScenarioLabels = document.querySelector("#demoScenarioLabels");
const demoScenarioResult = document.querySelector("#demoScenarioResult");
const demoScenarioTask = document.querySelector("#demoScenarioTask");
const demoProposalAction = document.querySelector("#demoProposalAction");
const demoActionContract = document.querySelector("#demoActionContract");
const demoClickReadiness = document.querySelector("#demoClickReadiness");
const demoScenarioReasons = document.querySelector("#demoScenarioReasons");
const plannerContextPanel = document.querySelector("#plannerContextPanel");
const buildPlannerContextButton = document.querySelector("#buildPlannerContext");
const plannerContextTask = document.querySelector("#plannerContextTask");
const plannerContextAppState = document.querySelector("#plannerContextAppState");
const plannerContextElements = document.querySelector("#plannerContextElements");
const plannerContextEvents = document.querySelector("#plannerContextEvents");
const plannerContextSafety = document.querySelector("#plannerContextSafety");
const plannerContextJson = document.querySelector("#plannerContextJson");
const plannerTracePanel = document.querySelector("#plannerTracePanel");
const plannerTraceMode = document.querySelector("#plannerTraceMode");
const plannerTraceSource = document.querySelector("#plannerTraceSource");
const plannerTraceValidation = document.querySelector("#plannerTraceValidation");
const plannerTraceFallback = document.querySelector("#plannerTraceFallback");
const plannerTraceOutput = document.querySelector("#plannerTraceOutput");
const plannerTraceContext = document.querySelector("#plannerTraceContext");
const plannerEvaluationPanel = document.querySelector("#plannerEvaluationPanel");
const loadPlannerEvaluationButton = document.querySelector("#loadPlannerEvaluation");
const plannerEvaluationStatus = document.querySelector("#plannerEvaluationStatus");
const plannerEvaluationSummary = document.querySelector("#plannerEvaluationSummary");
const plannerEvaluationResults = document.querySelector("#plannerEvaluationResults");
const sandboxEvaluationPanel = document.querySelector("#sandboxEvaluationPanel");
const loadSandboxEvaluationButton = document.querySelector("#loadSandboxEvaluation");
const sandboxEvaluationStatus = document.querySelector("#sandboxEvaluationStatus");
const sandboxEvaluationControls = document.querySelector("#sandboxEvaluationControls");
const sandboxEvaluationFixtureSet = document.querySelector("#sandboxEvaluationFixtureSet");
const sandboxEvaluationResultFilter = document.querySelector("#sandboxEvaluationResultFilter");
const sandboxEvaluationTypeFilter = document.querySelector("#sandboxEvaluationTypeFilter");
const sandboxEvaluationBlockerFilter = document.querySelector("#sandboxEvaluationBlockerFilter");
const expandSandboxScenarios = document.querySelector("#expandSandboxScenarios");
const collapseSandboxScenarios = document.querySelector("#collapseSandboxScenarios");
const resetSandboxFilters = document.querySelector("#resetSandboxFilters");
const copySandboxSummary = document.querySelector("#copySandboxSummary");
const sandboxEvaluationQuickFilters = document.querySelector("#sandboxEvaluationQuickFilters");
const sandboxEvaluationCopyStatus = document.querySelector("#sandboxEvaluationCopyStatus");
const sandboxEvaluationCounts = document.querySelector("#sandboxEvaluationCounts");
const sandboxEvaluationSummaryViz = document.querySelector("#sandboxEvaluationSummaryViz");
const sandboxEvaluationSummary = document.querySelector("#sandboxEvaluationSummary");
const sandboxEvaluationTimeline = document.querySelector("#sandboxEvaluationTimeline");
const sandboxEvaluationResults = document.querySelector("#sandboxEvaluationResults");
const phase9ExperimentPanel = document.querySelector("#phase9ExperimentPanel");
const loadPhase9ExperimentButton = document.querySelector("#loadPhase9Experiment");
const phase9ExperimentStatus = document.querySelector("#phase9ExperimentStatus");
const phase9ExperimentControls = document.querySelector("#phase9ExperimentControls");
const phase9OutcomeFilter = document.querySelector("#phase9OutcomeFilter");
const phase9GateBlockerFilter = document.querySelector("#phase9GateBlockerFilter");
const phase9ApprovalFilter = document.querySelector("#phase9ApprovalFilter");
const phase9RiskFilter = document.querySelector("#phase9RiskFilter");
const phase9ReadinessFilter = document.querySelector("#phase9ReadinessFilter");
const phase9ScenarioTypeFilter = document.querySelector("#phase9ScenarioTypeFilter");
const phase9GroupMode = document.querySelector("#phase9GroupMode");
const phase9AuditGroupMode = document.querySelector("#phase9AuditGroupMode");
const phase9AuditSortMode = document.querySelector("#phase9AuditSortMode");
const expandPhase9Scenarios = document.querySelector("#expandPhase9Scenarios");
const collapsePhase9Scenarios = document.querySelector("#collapsePhase9Scenarios");
const expandPhase9Audit = document.querySelector("#expandPhase9Audit");
const collapsePhase9Audit = document.querySelector("#collapsePhase9Audit");
const resetPhase9Filters = document.querySelector("#resetPhase9Filters");
const phase9QuickFilters = document.querySelector("#phase9QuickFilters");
const copyPhase9AISummary = document.querySelector("#copyPhase9AISummary");
const copyPhase9JsonReport = document.querySelector("#copyPhase9JsonReport");
const copyPhase9ReproBundle = document.querySelector("#copyPhase9ReproBundle");
const phase9ExportCopyStatus = document.querySelector("#phase9ExportCopyStatus");
const phase9Counts = document.querySelector("#phase9Counts");
const phase9ExperimentSummary = document.querySelector("#phase9ExperimentSummary");
const phase9ExperimentTimeline = document.querySelector("#phase9ExperimentTimeline");
const phase9ExperimentResults = document.querySelector("#phase9ExperimentResults");
const safetyActionArea = document.querySelector("#safetyActionArea");
const safetyBrakeMessage = document.querySelector("#safetyBrakeMessage");
const safetyButtons = document.querySelector("#safetyButtons");
const approveProposal = document.querySelector("#approveProposal");
const rejectProposal = document.querySelector("#rejectProposal");
const dryRunPreview = document.querySelector("#dryRunPreview");
const dryRunStatus = document.querySelector("#dryRunStatus");
const dryRunShot = document.querySelector("#dryRunShot");
const dryRunImage = document.querySelector("#dryRunImage");
const dryRunOverlay = document.querySelector("#dryRunOverlay");
const dryRunDetails = document.querySelector("#dryRunDetails");
const dryRunTargetLabel = document.querySelector("#dryRunTargetLabel");
const dryRunBbox = document.querySelector("#dryRunBbox");
const dryRunCenter = document.querySelector("#dryRunCenter");
const dryRunExecuted = document.querySelector("#dryRunExecuted");
const executionSelfTest = document.querySelector("#executionSelfTest");
const runWaitSelfTest = document.querySelector("#runWaitSelfTest");
const waitSelfTestStatus = document.querySelector("#waitSelfTestStatus");
const waitSelfTestResult = document.querySelector("#waitSelfTestResult");
const waitSelfTestExecutionStatus = document.querySelector("#waitSelfTestExecutionStatus");
const waitSelfTestExecutionType = document.querySelector("#waitSelfTestExecutionType");
const waitSelfTestDuration = document.querySelector("#waitSelfTestDuration");
const waitSelfTestVerificationStatus = document.querySelector("#waitSelfTestVerificationStatus");
const waitSelfTestVerificationReason = document.querySelector("#waitSelfTestVerificationReason");
const waitSelfTestPostObservation = document.querySelector("#waitSelfTestPostObservation");
const refreshEvents = document.querySelector("#refreshEvents");
const recentEventsList = document.querySelector("#recentEventsList");
const detailsPanel = document.querySelector(".details-panel");
const detailUiStateId = document.querySelector("#detailUiStateId");
const detailObservationId = document.querySelector("#detailObservationId");
const detailAppGuess = document.querySelector("#detailAppGuess");
const detailStateGuess = document.querySelector("#detailStateGuess");
const detailSummary = document.querySelector("#detailSummary");
const detailConfidence = document.querySelector("#detailConfidence");
const detailVisibleText = document.querySelector("#detailVisibleText");
const detailVisibleTextBoxes = document.querySelector("#detailVisibleTextBoxes");
const detailVisibleElements = document.querySelector("#detailVisibleElements");
const detailProposalId = document.querySelector("#detailProposalId");
const detailActionType = document.querySelector("#detailActionType");
const detailActionTarget = document.querySelector("#detailActionTarget");
const detailTargetElementId = document.querySelector("#detailTargetElementId");
const detailTargetLabel = document.querySelector("#detailTargetLabel");
const detailTargetBbox = document.querySelector("#detailTargetBbox");
const detailActionParameters = document.querySelector("#detailActionParameters");
const detailActionReason = document.querySelector("#detailActionReason");
const detailActionRisk = document.querySelector("#detailActionRisk");
const detailRequiresApproval = document.querySelector("#detailRequiresApproval");
const detailSafetyDecision = document.querySelector("#detailSafetyDecision");
const detailSafetyReason = document.querySelector("#detailSafetyReason");
const detailError = document.querySelector("#detailError");

const DEFAULT_AGENT_NAME = "Mirai";
const EXECUTION_POLICY_ACTIONS = ["wait", "click", "type", "hotkey", "scroll", "switch_app"];
const SANDBOX_BLOCKER_DESCRIPTIONS = {
  stale_observation: "Observation freshness failed before the sandbox gate.",
  high_risk_requires_approval: "High-risk target is approval-gated and blocked for sandbox evaluation.",
  unknown_risk_target: "Target risk is unknown, so the sandbox gate stays conservative.",
  low_confidence_target: "Target confidence is below the sandbox threshold.",
  invalid_bbox: "Target bounding box is missing, malformed, or out of bounds.",
  bbox_center_mismatch: "Target center does not match the normalized bounding box.",
  coordinate_space_unknown: "Viewport or coordinate-space metadata is missing.",
  dpi_uncertain: "DPI or scale metadata is uncertain.",
  preview_only_contract: "Action contract remains preview-only and cannot execute.",
  missing_target: "No normalized visible element target is available.",
};
const SANDBOX_BLOCKER_SEVERITY = {
  stale_observation: "medium",
  high_risk_requires_approval: "critical",
  unknown_risk_target: "critical",
  low_confidence_target: "high",
  invalid_bbox: "critical",
  bbox_center_mismatch: "high",
  coordinate_space_unknown: "high",
  dpi_uncertain: "medium",
  preview_only_contract: "medium",
  missing_target: "critical",
};
const SANDBOX_AUDIT_EVENT_LABELS = {
  sandbox_experiment_requested: "requested",
  sandbox_gate_passed: "gate passed",
  sandbox_gate_blocked: "gate blocked",
  sandbox_post_action_verification_planned: "verification planned",
  sandbox_dry_run_completed: "dry-run complete",
  sandbox_real_action_skipped: "real action skipped",
  phase9_experiment_requested: "requested",
  phase9_mock_approval_checked: "approval checked",
  phase9_emergency_stop_checked: "stop checked",
  phase9_gate_passed: "gate passed",
  phase9_gate_blocked: "gate blocked",
  phase9_post_action_verification_planned: "verification planned",
  phase9_rollback_plan_recorded: "rollback recorded",
  phase9_dry_run_completed: "dry-run complete",
  phase9_real_action_skipped: "real action skipped",
};
const SANDBOX_QUICK_FILTER_GROUPS = {
  geometry: {
    label: "geometry",
    description: "bbox, center, viewport, DPI, freshness, and missing-target blockers",
  },
  readiness: {
    label: "readiness",
    description: "readiness blockers such as preview-only contracts",
  },
  approval: {
    label: "approval",
    description: "approval-gated high-risk or unknown-risk targets",
  },
  risk: {
    label: "risk",
    description: "high-risk, unknown-risk, and low-confidence targets",
  },
  scope: {
    label: "scope",
    description: "forbidden action type or target outside the sandbox scope",
  },
  audit: {
    label: "audit",
    description: "missing audit-plan and audit-gate scenarios",
  },
};
const PHASE9_QUICK_FILTER_GROUPS = {
  blockers: {
    label: "gate blockers",
    description: "Phase 7/8 gate blocker and failure reason scenarios",
  },
  approval: {
    label: "approval",
    description: "mock approval present, checked, or missing states",
  },
  risk: {
    label: "risk",
    description: "high, unknown, medium, and low risk targets",
  },
  readiness: {
    label: "readiness",
    description: "readiness ready or blocked/unknown states",
  },
  skipped: {
    label: "skipped",
    description: "real-action skipped dry-run experiment paths",
  },
};
const PHASE9_BLOCKER_SEVERITY = {
  missing_phase7_checklist: "critical",
  missing_user_approval: "critical",
  real_action_disabled: "medium",
  readiness_not_ready: "high",
  high_risk_target: "critical",
  stale_observation: "medium",
  invalid_target_geometry: "critical",
  missing_post_action_verification: "high",
  forbidden_action_type: "critical",
  outside_sandbox_scope: "critical",
  missing_audit_plan: "high",
  missing_action_contract: "critical",
  missing_target: "critical",
  missing_emergency_stop: "critical",
  emergency_stop_active: "critical",
  missing_rollback_plan: "high",
  low_confidence_target: "high",
};
const DEMO_SCENARIOS = {
  browser_search: {
    defaultTask: "Search",
    description: "harmless search-like target",
    appGuess: "Chrome",
    labels: ["Search"],
  },
  dangerous_send: {
    defaultTask: "Send",
    description: "high-risk send target",
    appGuess: "WeChat",
    labels: ["Send"],
  },
  dangerous_delete: {
    defaultTask: "Delete",
    description: "high-risk delete target",
    appGuess: "File Explorer",
    labels: ["Delete"],
  },
  app_mismatch: {
    defaultTask: "Use WeChat to send a message",
    description: "task asks for another app",
    appGuess: "Chrome",
    labels: ["Search"],
  },
};
const savedName = window.localStorage.getItem("agent.displayName");
let currentProposal = null;
let currentSafetyDecision = null;
let currentTask = "";
let currentDryRunAction = null;
let currentUiState = null;
let currentActionContract = null;
let currentSandboxEvaluationReport = null;
let currentSandboxQuickFilterGroup = "all";
let currentPhase9ExperimentReport = null;
let currentPhase9QuickFilterGroup = "all";

setDisplayedAgentName(savedName || DEFAULT_AGENT_NAME);
setDemoScenarioSelectionDefaults();

function setAgentName(name) {
  const trimmed = name.trim();

  if (!trimmed) {
    setDisplayedAgentName(DEFAULT_AGENT_NAME);
    window.localStorage.removeItem("agent.displayName");
    return;
  }

  setDisplayedAgentName(trimmed);
  window.localStorage.setItem("agent.displayName", trimmed);
}

function setDisplayedAgentName(name) {
  agentName.textContent = name;
  document.title = name;
}

agentName.addEventListener("click", () => {
  renameInput.value = agentName.textContent.trim();
  renameDialog.showModal();
  renameInput.select();
});

renameForm.addEventListener("submit", (event) => {
  if (event.submitter?.value === "save") {
    setAgentName(renameInput.value);
  }
});

taskInput.addEventListener("input", resizeTaskInput);

taskInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && event.ctrlKey) {
    event.preventDefault();
    taskForm.requestSubmit();
  }
});

window.addEventListener("resize", () => {
  if (currentDryRunAction?.bbox && !dryRunShot.hidden) {
    positionDryRunOverlay(currentDryRunAction.bbox);
  }
});

resizeTaskInput();
renderProposalSummary();
renderActionContract();
renderClickReadiness();
renderRuntimeStatus();
renderSafetyDecision();
renderDryRunAction();
renderWaitSelfTestResult();
renderExecutionPolicy();
renderPlannerContext();
renderPlannerTrace();
renderPlannerEvaluation();
renderSandboxEvaluation();
renderPhase9Experiment();
renderPermissionProfile();
renderCapabilities();
fetchRuntimeStatus({ silent: true });
fetchExecutionPolicy({ silent: true });
fetchPermissionProfile({ silent: true });
fetchCapabilities({ silent: true });
fetchRecentEvents({ silent: true });

approveProposal.addEventListener("click", async () => {
  await recordApprovalDecision("approved");
});

rejectProposal.addEventListener("click", async () => {
  await recordApprovalDecision("rejected");
});

refreshEvents.addEventListener("click", async () => {
  await fetchRecentEvents();
});

runWaitSelfTest.addEventListener("click", async () => {
  await runWaitExecutionSelfTest();
});

demoScenarioSelect.addEventListener("change", () => {
  setDemoScenarioSelectionDefaults();
});

runDemoScenarioButton.addEventListener("click", async () => {
  await runSelectedDemoScenario();
});

buildPlannerContextButton.addEventListener("click", async () => {
  await buildCurrentPlannerContext();
});

loadPlannerEvaluationButton.addEventListener("click", async () => {
  await loadDemoPlannerEvaluation();
});

loadSandboxEvaluationButton.addEventListener("click", async () => {
  await loadSandboxEvaluation();
});

loadPhase9ExperimentButton.addEventListener("click", async () => {
  await loadPhase9Experiment();
});

for (const phase9FilterControl of [
  phase9OutcomeFilter,
  phase9GateBlockerFilter,
  phase9ApprovalFilter,
  phase9RiskFilter,
  phase9ReadinessFilter,
  phase9ScenarioTypeFilter,
  phase9GroupMode,
  phase9AuditGroupMode,
  phase9AuditSortMode,
]) {
  phase9FilterControl.addEventListener("change", () => {
    renderPhase9Experiment(currentPhase9ExperimentReport);
  });
}

expandPhase9Scenarios.addEventListener("click", () => {
  setPhase9ScenarioDetailsOpen(true);
});

collapsePhase9Scenarios.addEventListener("click", () => {
  setPhase9ScenarioDetailsOpen(false);
});

expandPhase9Audit.addEventListener("click", () => {
  setPhase9AuditDetailsOpen(true);
});

collapsePhase9Audit.addEventListener("click", () => {
  setPhase9AuditDetailsOpen(false);
});

resetPhase9Filters.addEventListener("click", () => {
  resetPhase9ExperimentFilters();
});

copyPhase9AISummary.addEventListener("click", async () => {
  await copyPhase9ExportPayload("ai_summary");
});

copyPhase9JsonReport.addEventListener("click", async () => {
  await copyPhase9ExportPayload("json_report");
});

copyPhase9ReproBundle.addEventListener("click", async () => {
  await copyPhase9ExportPayload("repro_bundle");
});

sandboxEvaluationFixtureSet.addEventListener("change", () => {
  renderSandboxEvaluation(currentSandboxEvaluationReport);
});

sandboxEvaluationResultFilter.addEventListener("change", () => {
  renderSandboxEvaluation(currentSandboxEvaluationReport);
});

sandboxEvaluationTypeFilter.addEventListener("change", () => {
  renderSandboxEvaluation(currentSandboxEvaluationReport);
});

sandboxEvaluationBlockerFilter.addEventListener("change", () => {
  renderSandboxEvaluation(currentSandboxEvaluationReport);
});

expandSandboxScenarios.addEventListener("click", () => {
  setSandboxScenarioDetailsOpen(true);
});

collapseSandboxScenarios.addEventListener("click", () => {
  setSandboxScenarioDetailsOpen(false);
});

resetSandboxFilters.addEventListener("click", () => {
  resetSandboxEvaluationFilters();
});

copySandboxSummary.addEventListener("click", async () => {
  await copySandboxEvaluationSummary();
});

function setDetailsFromUiState(uiState) {
  currentUiState = uiState;
  const text = Array.isArray(uiState.visible_text) ? uiState.visible_text : [];
  const textBoxes = Array.isArray(uiState.visible_text_boxes) ? uiState.visible_text_boxes : [];
  const elements = Array.isArray(uiState.visible_elements) ? uiState.visible_elements : [];

  detailUiStateId.textContent = uiState.ui_state_id ?? "unknown";
  detailObservationId.textContent = uiState.source_observation_id ?? "unknown";
  detailAppGuess.textContent = uiState.app_guess ?? "unknown";
  detailStateGuess.textContent = uiState.state_guess ?? "unknown";
  detailSummary.textContent = uiState.summary ?? "No summary available.";
  detailConfidence.textContent =
    Number.isFinite(uiState.confidence) ? uiState.confidence.toFixed(2) : "unknown";
  detailVisibleText.textContent = formatVisibleText(text);
  detailVisibleTextBoxes.textContent = formatTextBoxes(textBoxes);
  detailVisibleElements.textContent = formatVisibleElements(elements);
  detailError.textContent = "none";
}

function formatVisibleText(text) {
  if (!text.length) {
    return "OCR found no text.";
  }

  const preview = text.slice(0, 6).map((item) => `"${compactText(item, 64)}"`);
  return `${text.length} text item(s): ${preview.join("; ")}${remainingCount(text.length, preview.length)}`;
}

function formatTextBoxes(textBoxes) {
  if (!textBoxes.length) {
    return "OCR found no text boxes.";
  }

  const preview = textBoxes.slice(0, 3).map((box) => {
    const bbox = box.bbox ?? {};
    const confidence = Number.isFinite(box.confidence) ? box.confidence.toFixed(2) : "unknown";
    return `${compactText(box.text ?? "", 48)} @ ${bbox.x ?? "?"},${bbox.y ?? "?"} ${bbox.width ?? "?"}x${
      bbox.height ?? "?"
    } (${confidence})`;
  });

  return `${textBoxes.length} box(es): ${preview.join("; ")}${remainingCount(textBoxes.length, preview.length)}`;
}

function formatVisibleElements(elements) {
  if (!elements.length) {
    return "No visible elements found. Mirai is staying read-only.";
  }

  const preview = elements.slice(0, 3).map((element) => {
    const bbox = element.bbox ?? {};
    const confidence = Number.isFinite(element.confidence) ? element.confidence.toFixed(2) : "unknown";
    return `${element.role ?? "unknown"}:${compactText(element.label ?? "", 48)} @ ${bbox.x ?? "?"},${
      bbox.y ?? "?"
    } ${bbox.width ?? "?"}x${bbox.height ?? "?"} (${confidence})`;
  });

  return `${elements.length} element(s): ${preview.join("; ")}${remainingCount(elements.length, preview.length)}`;
}

function compactText(value, maxLength) {
  const text = String(value).replace(/\s+/g, " ").trim();

  if (text.length <= maxLength) {
    return text;
  }

  return `${text.slice(0, Math.max(0, maxLength - 3))}...`;
}

function remainingCount(total, shown) {
  const remaining = total - shown;
  return remaining > 0 ? `; +${remaining} more` : "";
}

function setDetailsFromProposal(proposal) {
  const action = proposal.action ?? {};
  const dryRunAction = buildDryRunAction(action);

  renderProposalSummary(action);
  detailProposalId.textContent = proposal.proposal_id ?? "unknown";
  detailActionType.textContent = action.type ?? "unknown";
  detailActionTarget.textContent = action.target ?? "unknown";
  detailTargetElementId.textContent = action.target_element_id ?? "none";
  detailTargetLabel.textContent = action.target_label ?? "none";
  detailTargetBbox.textContent = formatTargetBbox(action.target_bbox);
  detailActionParameters.textContent = JSON.stringify(action.parameters ?? {});
  detailActionReason.textContent = action.reason ?? "No proposal reason.";
  detailActionRisk.textContent = action.risk ?? "unknown";
  detailRequiresApproval.textContent =
    typeof action.requires_approval === "boolean" ? String(action.requires_approval) : "unknown";
  currentDryRunAction = dryRunAction;
  renderDryRunAction(dryRunAction);
}

function setDetailsFromActionContract(actionContract, action = null) {
  currentActionContract = actionContract;
  renderActionContract(actionContract, action);
}

function setDetailsFromSafetyDecision(safetyDecision) {
  detailSafetyDecision.textContent = safetyDecision.decision ?? "unknown";
  detailSafetyReason.textContent = safetyDecision.reason ?? "No safety decision reason.";
  renderSafetyDecision(safetyDecision);
}

function formatTargetBbox(bbox) {
  if (!bbox || typeof bbox !== "object") {
    return "none";
  }

  const hasValues = ["x", "y", "width", "height"].some((key) => bbox[key] !== undefined);
  if (!hasValues) {
    return "none";
  }

  return `${bbox.x ?? "?"},${bbox.y ?? "?"} ${bbox.width ?? "?"}x${bbox.height ?? "?"}`;
}

function formatTargetCenter(bbox) {
  const normalized = normalizeBbox(bbox);
  if (!normalized) {
    return "none";
  }

  return `${Math.round(normalized.x + normalized.width / 2)},${Math.round(
    normalized.y + normalized.height / 2
  )}`;
}

function renderProposalSummary(action = null) {
  proposalFacts.replaceChildren();
  proposalFacts.hidden = true;
  proposalPanel.dataset.state = action?.type || "empty";

  if (!action) {
    proposalTitle.textContent = "Read-only proposal";
    proposalSummary.textContent =
      "Enter a task and choose Plan. Mirai will inspect the screen and stay read-only.";
    return;
  }

  if (action.type === "target_hint") {
    proposalTitle.textContent = "Target found";
    proposalSummary.textContent = "Mirai found a likely screen target. No action will be executed.";
    setProposalFacts([
      ["Label", action.target_label || "unknown"],
      ["Element", action.target_element_id || "none"],
      ["Bbox", formatTargetBbox(action.target_bbox)],
      ["Center", formatTargetCenter(action.target_bbox)],
    ]);
    return;
  }

  if (action.type === "switch_app_hint") {
    const currentApp = action.parameters?.current_app || "unknown";
    proposalTitle.textContent = "Switch app needed";
    proposalSummary.textContent = "The task points at a different app, so Mirai is stopping at a hint.";
    setProposalFacts([
      ["Target app", action.target || "unknown"],
      ["Current app", currentApp],
    ]);
    return;
  }

  if (action.type === "no_op") {
    proposalTitle.textContent = "No reliable next step yet";
    proposalSummary.textContent =
      "Mirai did not find a safe target for this task and is staying read-only.";
    return;
  }

  proposalTitle.textContent = action.type || "Unknown proposal";
  proposalSummary.textContent = action.reason || "Mirai returned a read-only proposal.";
}

function setProposalFacts(rows) {
  proposalFacts.hidden = false;

  for (const [label, value] of rows) {
    const row = document.createElement("div");
    const term = document.createElement("dt");
    const detail = document.createElement("dd");

    term.textContent = label;
    detail.textContent = value;
    row.append(term, detail);
    proposalFacts.appendChild(row);
  }
}

function renderActionContract(actionContract = null, action = null) {
  actionContractFacts.replaceChildren();
  actionContractFacts.hidden = true;
  actionContractPanel.dataset.state = actionContract?.type || "empty";

  if (!actionContract) {
    actionContractTitle.textContent = "Preview action contract";
    actionContractSummary.textContent = "No preview action contract. Execution unavailable.";
    return;
  }

  actionContractTitle.textContent = "Preview action contract";

  if (actionContract.type === "click") {
    actionContractSummary.textContent =
      "Preview-only click contract. Execution unavailable in this cockpit.";
    setActionContractFacts([
      ["Contract", actionContract.type],
      ["Proposal", actionContract.source_proposal_id || "unknown"],
      ["Status", actionContract.status || "unknown"],
      ["Executed", String(actionContract.executed)],
      ["Label", actionContract.target_label || "unknown"],
      ["Element", actionContract.target_element_id || "none"],
      ["Bbox", formatTargetBbox(actionContract.bbox)],
      ["Center", formatPoint(actionContract.center)],
    ]);
    return;
  }

  if (actionContract.type === "switch_app") {
    actionContractSummary.textContent =
      "Preview-only switch-app contract. Execution unavailable in this cockpit.";
    setActionContractFacts([
      ["Contract", actionContract.type],
      ["Proposal", actionContract.source_proposal_id || "unknown"],
      ["Status", actionContract.status || "unknown"],
      ["Executed", String(actionContract.executed)],
      ["Target app", actionContract.target_app || "unknown"],
      ["Current app", actionContract.parameters?.current_app || "unknown"],
    ]);
    return;
  }

  if (actionContract.type === "wait") {
    actionContractSummary.textContent =
      actionContract.status === "approved_for_execution"
        ? "Wait-only contract. Execution is available only through the /execute endpoint."
        : "Wait contract is not approved for execution.";
    setActionContractFacts([
      ["Contract", actionContract.type],
      ["Proposal", actionContract.source_proposal_id || "unknown"],
      ["Status", actionContract.status || "unknown"],
      ["Executed", String(actionContract.executed)],
      ["Duration", `${waitDurationMs(actionContract)} ms`],
    ]);
    return;
  }

  actionContractSummary.textContent = "Mirai produced a preview-only contract. Nothing will be executed.";
  setActionContractFacts([
    ["Contract", actionContract.type || "unknown"],
    ["Proposal", actionContract.source_proposal_id || "unknown"],
    ["Status", actionContract.status || "unknown"],
    ["Executed", String(actionContract.executed)],
  ]);
}

function renderClickReadiness(clickReadiness = null, actionContract = null, proposal = null) {
  clickReadinessReasons.replaceChildren();
  clickReadinessReasons.hidden = true;
  renderReadinessChecks(clickReadinessChecks, null);
  renderReadinessDebugSummary(clickReadinessDebug, clickReadinessDebugJson, null);
  const isClickContract = actionContract?.type === "click";
  const status = clickReadiness?.status || "not_applicable";

  if (!isClickContract || status === "not_applicable") {
    clickReadinessPanel.dataset.state = "not_applicable";
    clickReadinessSummary.textContent = "Click readiness: not applicable";
    return;
  }

  clickReadinessPanel.dataset.state = status;
  clickReadinessSummary.textContent =
    status === "blocked"
      ? "Click readiness: blocked; click is not executable."
      : `Click readiness: ${status}. Diagnostics are read-only.`;

  const reasons = Array.isArray(clickReadiness.reasons) ? clickReadiness.reasons : [];
  if (reasons.length) {
    clickReadinessReasons.hidden = false;
    for (const reason of reasons) {
      const item = document.createElement("li");
      item.dataset.severity = readinessReasonSeverity(reason, clickReadiness);
      item.textContent = displayReadinessReason(reason);
      clickReadinessReasons.appendChild(item);
    }
  }

  renderReadinessChecks(clickReadinessChecks, clickReadiness, "Read-only diagnostics");
  renderReadinessDebugSummary(
    clickReadinessDebug,
    clickReadinessDebugJson,
    buildReadinessDebugSummary({ proposal, actionContract, clickReadiness })
  );
}

function renderReadinessChecks(container, clickReadiness, title = "Readiness checks") {
  container.replaceChildren();
  container.hidden = true;

  const checks = Array.isArray(clickReadiness?.checks) ? clickReadiness.checks : [];
  if (!checks.length) {
    return;
  }

  const heading = document.createElement("p");
  const list = document.createElement("ul");

  heading.className = "click-readiness-checks-title";
  heading.textContent = title;
  list.className = "click-readiness-check-list";

  for (const check of checks) {
    list.appendChild(readinessCheckItem(check, clickReadiness));
  }

  container.hidden = false;
  container.append(heading, list);
}

function renderReadinessDebugSummary(details, pre, summary) {
  details.hidden = true;
  pre.textContent = "{}";

  if (!summary) {
    return;
  }

  details.hidden = false;
  pre.textContent = JSON.stringify(summary, null, 2);
}

function buildReadinessDebugSummary({
  planner = "",
  proposal = null,
  actionContract = null,
  clickReadiness = null,
} = {}) {
  if (!clickReadiness || typeof clickReadiness !== "object") {
    return null;
  }

  const action = proposal?.action ?? {};
  const reasons = Array.isArray(clickReadiness.reasons)
    ? clickReadiness.reasons.map((reason) => String(reason))
    : [];
  const blockerCodes = Array.isArray(clickReadiness.blocker_codes)
    ? clickReadiness.blocker_codes.map((code) => String(code))
    : [];
  const blockers = Array.isArray(clickReadiness.blockers)
    ? clickReadiness.blockers.map((blocker) => ({
        code: String(blocker?.code || ""),
        reason: String(blocker?.reason || ""),
        severity: String(blocker?.severity || ""),
      }))
    : [];
  const checks = Array.isArray(clickReadiness.checks)
    ? clickReadiness.checks.map((check) => readinessDebugCheck(check, clickReadiness))
    : [];
  const target = clickReadiness.target ?? {};
  const summary = {
    proposal_id: String(proposal?.proposal_id || actionContract?.source_proposal_id || ""),
    contract_type: String(actionContract?.type || ""),
    target_label: String(actionContract?.target_label || action.target_label || ""),
    target_risk_hint: String(target.risk_hint || actionContract?.target_risk_hint || action.target_risk_hint || ""),
    target_confidence: target.confidence ?? actionContract?.target_confidence ?? action.target_confidence ?? null,
    status: String(clickReadiness.status || "not_applicable"),
    ready: Boolean(clickReadiness.ready),
    risk: String(clickReadiness.risk || "unknown"),
    reasons,
    blocker_codes: blockerCodes,
    blockers,
    coordinate_debug: clickReadiness.coordinate_debug ?? {},
    checks,
    note: "Read-only diagnostics. Blocked readiness means click is not executable.",
  };

  if (planner) {
    summary.planner = planner;
  }

  return summary;
}

function readinessDebugCheck(check, clickReadiness = {}) {
  const status = normalizeReadinessCheckStatus(check?.status);
  const reason = check?.reason ? displayReadinessReason(check.reason) : readinessCheckFallbackReason(status);

  return {
    name: String(check?.name || "unknown_check"),
    code: String(check?.code || ""),
    status,
    reason,
    severity: readinessCheckSeverity(check, clickReadiness),
  };
}

function readinessCheckItem(check, clickReadiness = {}) {
  const item = document.createElement("li");
  const checkName = document.createElement("span");
  const checkStatus = document.createElement("span");
  const checkSeverity = document.createElement("span");
  const checkReason = document.createElement("span");
  const status = normalizeReadinessCheckStatus(check?.status);
  const severity = readinessCheckSeverity(check, clickReadiness);
  const reason = check?.reason ? displayReadinessReason(check.reason) : readinessCheckFallbackReason(status);

  item.className = "click-readiness-check";
  item.dataset.status = status;
  item.dataset.severity = severity;
  checkName.className = "click-readiness-check-name";
  checkStatus.className = "click-readiness-check-status";
  checkSeverity.className = "click-readiness-check-severity";
  checkReason.className = "click-readiness-check-reason";

  checkName.textContent = displayReadinessCheckName(check?.name);
  checkStatus.textContent = displayReadinessCheckStatus(status);
  checkSeverity.textContent = severity === "none" ? "" : severity;
  checkReason.textContent = reason;

  item.append(checkName, checkStatus);
  if (severity !== "none") {
    item.appendChild(checkSeverity);
  }
  item.appendChild(checkReason);
  return item;
}

function displayReadinessCheckName(name) {
  const labels = {
    action_contract_present: "action contract",
    click_contract: "click contract",
    contract_status: "contract status",
    not_executed: "not executed",
    bbox_present: "bbox present",
    bbox_shape: "bbox shape",
    bbox_screen_bounds: "screen bounds",
    coordinate_space: "coordinate space",
    dpi_scale: "DPI / scale",
    center_shape: "center",
    center_bbox_consistency: "center vs bbox",
    target_present: "target",
    target_confidence: "target confidence",
    target_visibility: "target visibility",
    target_ambiguity: "target ambiguity",
    observation_freshness: "observation freshness",
    click_capability: "click capability",
    permission_profile: "permission profile",
    safety_decision: "safety decision",
    target_label_risk: "target label risk",
  };

  return labels[name] || String(name || "unknown check").replaceAll("_", " ");
}

function normalizeReadinessCheckStatus(status) {
  const normalized = String(status || "unknown").replace("-", "_");

  if (normalized === "passed" || normalized === "pass") {
    return "passed";
  }

  if (normalized === "blocked" || normalized === "failed") {
    return "blocked";
  }

  if (normalized === "not_applicable") {
    return "not_applicable";
  }

  return normalized || "unknown";
}

function displayReadinessCheckStatus(status) {
  if (status === "passed") {
    return "pass";
  }

  if (status === "not_applicable") {
    return "not applicable";
  }

  return displayRuntimeActuation(status);
}

function readinessCheckSeverity(check, clickReadiness = {}) {
  const reason = String(check?.reason || "").toLowerCase();
  const name = String(check?.name || "");
  const code = String(check?.code || "");
  const status = normalizeReadinessCheckStatus(check?.status);

  if (status !== "blocked") {
    return "none";
  }

  if (
    reason.includes("high-risk") ||
    code === "high_risk_requires_approval" ||
    name === "target_label_risk" ||
    clickReadiness.risk === "high"
  ) {
    return "high";
  }

  if (
    reason.includes("preview-only") ||
    reason.includes("capability") ||
    reason.includes("permission profile") ||
    reason.includes("bbox") ||
    reason.includes("stale") ||
    [
      "missing_target",
      "missing_bbox",
      "invalid_bbox",
      "missing_center",
      "bbox_center_mismatch",
      "out_of_viewport",
      "coordinate_space_unknown",
      "dpi_uncertain",
      "low_confidence_target",
      "hidden_or_disabled_target",
      "ambiguous_target",
      "action_not_enabled_by_policy",
    ].includes(code)
  ) {
    return "medium";
  }

  return clickReadiness.risk === "medium" ? "medium" : "low";
}

function readinessReasonSeverity(reason, clickReadiness = {}) {
  return readinessCheckSeverity({ status: "blocked", reason }, clickReadiness);
}

function displayReadinessReason(reason) {
  const text = String(reason || "");
  const lower = text.toLowerCase();

  if (lower.includes("high-risk target label")) {
    return "high-risk target label; read-only blocker";
  }

  if (lower.includes("preview-only contract")) {
    return "preview-only contract; never executable";
  }

  if (lower.includes("click capability disabled")) {
    return "click capability disabled; click is not executable";
  }

  if (lower.includes("permission profile does not allow click")) {
    return "permission profile does not allow click execution";
  }

  if (lower.includes("missing bbox")) {
    return "missing bbox; no target geometry";
  }

  if (lower.includes("missing target")) {
    return "missing target; no stable element identity";
  }

  if (lower.includes("missing center")) {
    return "missing center; target point unavailable";
  }

  if (lower.includes("malformed bbox")) {
    return "malformed bbox; target geometry is invalid";
  }

  if (lower.includes("invalid center")) {
    return "invalid center; target point is invalid";
  }

  if (lower.includes("center does not match bbox")) {
    return "center does not match bbox";
  }

  if (lower.includes("bbox outside screen bounds")) {
    return "bbox outside screen bounds";
  }

  if (lower.includes("coordinate space unknown")) {
    return "coordinate space unknown";
  }

  if (lower.includes("dpi is uncertain")) {
    return "DPI or scale is uncertain";
  }

  if (lower.includes("low-confidence target")) {
    return "low-confidence target; not ready";
  }

  if (lower.includes("hidden or disabled target")) {
    return "hidden or disabled target; not ready";
  }

  if (lower.includes("ambiguous target")) {
    return "ambiguous target; not ready";
  }

  if (lower.includes("target risk is unknown")) {
    return "target risk is unknown; not ready";
  }

  if (lower.includes("stale observation")) {
    return "stale observation; target may have moved";
  }

  return text || "No reason provided.";
}

function readinessCheckFallbackReason(status) {
  if (status === "passed") {
    return "passed";
  }

  if (status === "not_applicable") {
    return "not applicable";
  }

  return "no reason provided";
}

function waitDurationMs(actionContract) {
  const rawDuration = actionContract.duration_ms ?? actionContract.parameters?.duration_ms ?? 0;
  const duration = Number(rawDuration);

  if (!Number.isFinite(duration)) {
    return 0;
  }

  return Math.max(0, Math.min(Math.round(duration), 3000));
}

function setActionContractFacts(rows) {
  actionContractFacts.hidden = false;

  for (const [label, value] of rows) {
    const row = document.createElement("div");
    const term = document.createElement("dt");
    const detail = document.createElement("dd");

    term.textContent = label;
    detail.textContent = value;
    row.append(term, detail);
    actionContractFacts.appendChild(row);
  }
}

async function fetchCapabilities(options = {}) {
  const { silent = false } = options;

  try {
    const response = await fetch("/capabilities");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Capabilities failed with HTTP ${response.status}`);
    }

    renderCapabilities(payload.capabilities ?? {});
  } catch (error) {
    renderCapabilities();

    if (!silent) {
      detailError.textContent = `Capabilities refresh failed: ${error.message || String(error)}`;
      detailsPanel.open = true;
    }
  }
}

async function fetchRuntimeStatus(options = {}) {
  const { silent = false } = options;

  try {
    const response = await fetch("/runtime/status");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Runtime status failed with HTTP ${response.status}`);
    }

    renderRuntimeStatus(payload);
  } catch (error) {
    renderRuntimeStatus();

    if (!silent) {
      detailError.textContent = `Runtime status refresh failed: ${error.message || String(error)}`;
      detailsPanel.open = true;
    }
  }
}

function renderRuntimeStatus(payload = null) {
  const runtime = payload?.runtime ?? {};
  const resourceGuard = payload?.resource_guard ?? {};
  const clickReadiness = payload?.click_readiness ?? {};
  const aiPlanner = payload?.ai_planner ?? {};

  runtimeProfile.textContent = payload?.permission_profile || "unknown";
  runtimePlanner.textContent = formatPlannerMode(aiPlanner);
  runtimePlanner.title = formatPlannerTitle(aiPlanner);
  runtimeDesktopControl.textContent =
    typeof runtime.desktop_control === "boolean"
      ? runtime.desktop_control
        ? "enabled"
        : "disabled"
      : "unknown";
  runtimeActuation.textContent = runtime.actuation ? displayRuntimeActuation(runtime.actuation) : "unknown";
  runtimeVerification.textContent =
    typeof runtime.verification === "boolean" ? (runtime.verification ? "enabled" : "disabled") : "unknown";
  runtimeClick.textContent = clickReadiness.enabled ? "enabled" : "blocked";
  runtimeClick.title = clickReadiness.reason || "";
  runtimeResourceGuard.textContent = resourceGuard.enabled ? "enabled" : "unknown";
}

function formatPlannerMode(aiPlanner) {
  const mode = aiPlanner.planner_mode || "unknown";
  let source = "local";

  if (mode === "ai_proposal") {
    source = aiPlanner.ai_planner_usable ? "LLM ready" : "key missing";
  } else if (aiPlanner.openai_api_key_configured) {
    source = "local; key configured";
  }

  return `${displayRuntimeActuation(mode)}; ${source}`;
}

function formatPlannerTitle(aiPlanner) {
  if (aiPlanner.ai_planner_usable) {
    return "AI proposal mode is active and the OpenAI API key is configured.";
  }

  if (aiPlanner.planner_mode === "ai_proposal") {
    return "AI proposal mode is selected, but the OpenAI API key is not configured.";
  }

  return aiPlanner.openai_api_key_configured
    ? "Rule-based planner is active. The OpenAI API key is configured but unused."
    : "Rule-based planner is active. No external planner call is active.";
}

function displayRuntimeActuation(value) {
  return String(value).replaceAll("_", "-");
}

async function fetchExecutionPolicy(options = {}) {
  const { silent = false } = options;

  try {
    const response = await fetch("/execution-policy");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Execution policy failed with HTTP ${response.status}`);
    }

    renderExecutionPolicy(payload);
  } catch (error) {
    renderExecutionPolicy();

    if (!silent) {
      detailError.textContent = `Execution policy refresh failed: ${error.message || String(error)}`;
      detailsPanel.open = true;
    }
  }
}

function renderExecutionPolicy(payload = null) {
  executionPolicyList.replaceChildren();
  executionPolicyProfiles.replaceChildren();

  if (!payload) {
    executionPolicyProfile.textContent = "Profile: unknown";
    for (const actionType of EXECUTION_POLICY_ACTIONS) {
      executionPolicyList.appendChild(executionPolicyListItem(actionType, null));
    }
    executionPolicyProfiles.appendChild(executionPolicyEmptyState());
    return;
  }

  const profile = payload.current_profile || payload.summary?.current_profile || "unknown";
  const profilePolicy = payload.matrix?.[profile] ?? {};
  const profiles = Array.isArray(payload.profiles) ? payload.profiles : [];
  executionPolicyProfile.textContent = `Profile: ${profile}`;

  for (const actionType of EXECUTION_POLICY_ACTIONS) {
    executionPolicyList.appendChild(executionPolicyListItem(actionType, profilePolicy[actionType] ?? null));
  }

  for (const profileName of profiles) {
    executionPolicyProfiles.appendChild(executionPolicyProfileCard(profileName, payload.matrix?.[profileName] ?? {}, profile));
  }
}

function executionPolicyListItem(actionType, entry) {
  const item = document.createElement("li");
  const executable = Boolean(entry?.executable);
  const state = executable ? "executable" : "blocked";

  item.textContent = `${actionType}: ${state}`;
  item.dataset.executable = String(executable);
  item.title = entry?.reason || "";
  return item;
}

function executionPolicyProfileCard(profileName, profilePolicy, currentProfile) {
  const card = document.createElement("article");
  const title = document.createElement("p");
  const grid = document.createElement("ul");

  card.className = "execution-policy-profile-card";
  card.dataset.current = String(profileName === currentProfile);
  title.className = "execution-policy-profile-name";
  title.textContent = profileName === currentProfile ? `${profileName} (current)` : profileName;
  grid.className = "execution-policy-action-grid";

  for (const actionType of EXECUTION_POLICY_ACTIONS) {
    grid.appendChild(executionPolicyActionCell(actionType, profilePolicy[actionType] ?? null));
  }

  card.append(title, grid);
  return card;
}

function executionPolicyActionCell(actionType, entry) {
  const item = document.createElement("li");
  const action = document.createElement("span");
  const state = document.createElement("span");
  const stateText = executionPolicyStateText(entry);

  action.textContent = actionType;
  state.textContent = stateText;
  item.dataset.state = stateText.replaceAll(" ", "_").replace(/[()]/g, "");
  item.title = entry?.reason || "";
  item.append(action, state);
  return item;
}

function executionPolicyStateText(entry) {
  if (!entry) {
    return "unknown";
  }

  if (entry.executable) {
    return "executable";
  }

  if (entry.mode === "future_experimental") {
    return "future (blocked)";
  }

  return "blocked";
}

function executionPolicyEmptyState() {
  const item = document.createElement("p");
  item.className = "execution-policy-empty";
  item.textContent = "Execution policy unavailable.";
  return item;
}

async function fetchPermissionProfile(options = {}) {
  const { silent = false } = options;

  try {
    const response = await fetch("/permission-profile");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Permission profile failed with HTTP ${response.status}`);
    }

    renderPermissionProfile(payload);
  } catch (error) {
    renderPermissionProfile();

    if (!silent) {
      detailError.textContent = `Permission profile refresh failed: ${error.message || String(error)}`;
      detailsPanel.open = true;
    }
  }
}

function renderPermissionProfile(payload = null) {
  const profile = payload?.profile || "unknown";
  permissionProfileStatus.textContent = `Permission profile: ${profile}`;
}

function renderCapabilities(capabilities = null) {
  capabilitiesList.replaceChildren();

  if (!capabilities) {
    capabilitiesList.appendChild(capabilityListItem("wait", "unknown"));
    capabilitiesList.appendChild(capabilityListItem("click", "unknown"));
    capabilitiesList.appendChild(capabilityListItem("type", "unknown"));
    capabilitiesList.appendChild(capabilityListItem("hotkey", "unknown"));
    capabilitiesList.appendChild(capabilityListItem("scroll", "unknown"));
    return;
  }

  for (const actionType of ["wait", "click", "type", "hotkey", "scroll", "switch_app"]) {
    const capability = capabilities[actionType] ?? {};
    const state = capability.enabled && capability.executable ? "enabled" : "disabled";
    capabilitiesList.appendChild(capabilityListItem(actionType, state, capability));
  }
}

function capabilityListItem(actionType, state, capability = {}) {
  const item = document.createElement("li");
  item.textContent = `${displayCapabilityName(actionType)}: ${state}`;
  item.dataset.enabled = String(state === "enabled");
  item.title = capability.reason || "";
  return item;
}

function displayCapabilityName(actionType) {
  return actionType === "switch_app" ? "switch app" : actionType;
}

function setDemoScenarioSelectionDefaults() {
  const metadata = selectedDemoScenarioMetadata();
  demoTaskInput.value = metadata.defaultTask;
  demoTaskInput.placeholder = metadata.defaultTask || "Demo task";
  renderDemoScenarioSelection();
  renderDemoScenarioResult();
}

function selectedDemoScenarioMetadata() {
  return (
    DEMO_SCENARIOS[demoScenarioSelect.value] || {
      defaultTask: "",
      description: "unknown scenario",
      appGuess: "unknown",
      labels: [],
    }
  );
}

function renderDemoScenarioSelection() {
  const metadata = selectedDemoScenarioMetadata();
  demoScenarioSelectedName.textContent = demoScenarioSelect.value || "unknown";
  demoScenarioDescription.textContent = metadata.description;
  demoScenarioFakeApp.textContent = metadata.appGuess;
  demoScenarioLabels.textContent = metadata.labels.length ? metadata.labels.join(", ") : "none";
  demoScenarioResult.hidden = true;
  demoScenarioReasons.hidden = true;
  demoScenarioReasons.replaceChildren();
  demoScenarioPanel.dataset.state = "idle";
}

async function runSelectedDemoScenario() {
  statusText.textContent = "running demo scenario...";
  renderDemoScenarioRunning();
  setDemoScenarioControlsDisabled(true);

  try {
    const scenarioName = demoScenarioSelect.value;
    const task = demoTaskInput.value.trim();
    const params = new URLSearchParams({ name: scenarioName });

    if (task) {
      params.set("task", task);
    }

    const response = await fetch(`/demo/scenario?${params.toString()}`);
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Demo scenario failed with HTTP ${response.status}`);
    }

    renderDemoScenarioResult(payload);
    statusText.textContent = "demo scenario ready";
    await fetchRuntimeStatus({ silent: true });
  } catch (error) {
    statusText.textContent = "demo scenario failed";
    renderDemoScenarioError(error);
  } finally {
    setDemoScenarioControlsDisabled(false);
  }
}

function setDemoScenarioControlsDisabled(disabled) {
  demoScenarioSelect.disabled = disabled;
  demoTaskInput.disabled = disabled;
  runDemoScenarioButton.disabled = disabled;
}

function renderDemoScenarioResult(payload = null) {
  if (!payload) {
    demoScenarioResult.hidden = true;
    demoScenarioTask.textContent = "none";
    demoProposalAction.textContent = "none";
    demoActionContract.textContent = "none";
    demoClickReadiness.textContent = "not run";
    demoScenarioReasons.hidden = true;
    demoScenarioReasons.replaceChildren();
    return;
  }

  const action = payload.proposal?.action ?? {};
  const actionContract = payload.action_contract;
  const clickReadiness = payload.click_readiness ?? {};

  demoScenarioPanel.dataset.state = demoResultState(payload);
  demoScenarioResult.hidden = false;
  demoScenarioTask.textContent = payload.task || payload.ui_state?.task || "none";
  demoProposalAction.textContent = action.type || "unknown";
  demoActionContract.textContent = actionContract
    ? `${actionContract.type || "unknown"} / ${actionContract.status || "unknown"}`
    : "none";
  demoClickReadiness.textContent = clickReadiness.status
    ? readinessDisplayText(clickReadiness)
    : "not present";
  renderDemoScenarioReasons(demoReasonsFromPayload(payload));
}

function renderDemoScenarioRunning() {
  demoScenarioPanel.dataset.state = "running";
  demoScenarioResult.hidden = false;
  demoScenarioTask.textContent = demoTaskInput.value.trim() || selectedDemoScenarioMetadata().defaultTask || "none";
  demoProposalAction.textContent = "running...";
  demoActionContract.textContent = "running...";
  demoClickReadiness.textContent = "running...";
  renderDemoScenarioReasons([]);
}

function renderDemoScenarioError(error) {
  demoScenarioPanel.dataset.state = "error";
  demoScenarioResult.hidden = false;
  demoProposalAction.textContent = "failed";
  demoActionContract.textContent = "none";
  demoClickReadiness.textContent = "not present";
  renderDemoScenarioReasons([`Demo failed: ${error.message || String(error)}`]);
}

function demoResultState(payload) {
  const action = payload.proposal?.action ?? {};
  const readinessReasons = payload.click_readiness?.reasons;

  if (Array.isArray(readinessReasons) && readinessReasons.includes("high-risk target label")) {
    return "high_risk";
  }

  if (action.type === "switch_app_hint") {
    return "switch_app";
  }

  if (payload.click_readiness?.status === "blocked") {
    return "blocked";
  }

  return "done";
}

function readinessDisplayText(clickReadiness) {
  if (clickReadiness.status === "blocked") {
    return clickReadiness.ready === false ? "blocked / not ready" : "blocked";
  }

  return clickReadiness.ready === true
    ? `${clickReadiness.status} / ready`
    : clickReadiness.status;
}

function demoReasonsFromPayload(payload) {
  const reasons = [];
  const action = payload.proposal?.action ?? {};
  const safetyDecision = payload.safety_decision ?? {};
  const readinessReasons = payload.click_readiness?.reasons;

  if (action.reason) {
    reasons.push(`Proposal: ${action.reason}`);
  }

  if (safetyDecision.reason) {
    reasons.push(`Safety: ${safetyDecision.reason}`);
  }

  if (Array.isArray(readinessReasons)) {
    for (const reason of readinessReasons) {
      reasons.push(`Readiness: ${reason}`);
    }
  }

  return reasons;
}

function renderDemoScenarioReasons(reasons) {
  demoScenarioReasons.replaceChildren();

  if (!reasons.length) {
    demoScenarioReasons.hidden = true;
    return;
  }

  demoScenarioReasons.hidden = false;
  for (const reason of reasons) {
    const item = document.createElement("li");
    item.textContent = reason;

    if (reason.toLowerCase().includes("high-risk")) {
      item.dataset.risk = "high";
    }

    demoScenarioReasons.appendChild(item);
  }
}

async function buildCurrentPlannerContext() {
  const task = taskInput.value.trim();
  const params = new URLSearchParams();

  if (task) {
    params.set("task", task);
  }

  plannerContextPanel.dataset.state = "running";
  buildPlannerContextButton.disabled = true;
  plannerContextTask.textContent = task || "none";
  plannerContextAppState.textContent = "building...";
  plannerContextElements.textContent = "building...";
  plannerContextEvents.textContent = "building...";
  plannerContextSafety.textContent = "building...";
  plannerContextJson.textContent = "{}";
  statusText.textContent = "building planner context...";

  try {
    const endpoint = params.toString() ? `/planner-context?${params.toString()}` : "/planner-context";
    const response = await fetch(endpoint);
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Planner context failed with HTTP ${response.status}`);
    }

    renderPlannerContext(payload.planner_context ?? null);
    plannerContextPanel.dataset.state = "ready";
    detailError.textContent = "none";
    statusText.textContent = "planner context ready";
    await fetchRecentEvents({ silent: true });
  } catch (error) {
    plannerContextPanel.dataset.state = "error";
    plannerContextSafety.textContent = "failed";
    plannerContextJson.textContent = JSON.stringify(
      { error: error.message || String(error) },
      null,
      2
    );
    detailError.textContent = `Planner context failed: ${error.message || String(error)}`;
    detailsPanel.open = true;
    statusText.textContent = "planner context failed";
  } finally {
    buildPlannerContextButton.disabled = false;
  }
}

function renderPlannerContext(context = null) {
  if (!context) {
    plannerContextPanel.dataset.state = "empty";
    plannerContextTask.textContent = "none";
    plannerContextAppState.textContent = "unknown";
    plannerContextElements.textContent = "0";
    plannerContextEvents.textContent = "0";
    plannerContextSafety.textContent = "unknown";
    plannerContextJson.textContent = "{}";
    return;
  }

  const visibleElements = context.visible_elements ?? {};
  const recentEvents = context.recent_events ?? {};
  const safetyRuntime = context.safety_runtime ?? {};
  const executableActions = Array.isArray(safetyRuntime.executable_actions)
    ? safetyRuntime.executable_actions
    : [];

  plannerContextTask.textContent = context.task || "none";
  plannerContextAppState.textContent = `${context.app_guess || "unknown"} / ${
    context.state_guess || "unknown"
  }`;
  plannerContextElements.textContent = compactCountWithTruncation(visibleElements);
  plannerContextEvents.textContent = compactCountWithTruncation(recentEvents);
  plannerContextSafety.textContent = `desktop ${
    safetyRuntime.desktop_control ? "enabled" : "off"
  }; ${safetyRuntime.permission_profile || "unknown"}; exec ${
    executableActions.length ? executableActions.join(", ") : "none"
  }; blocked ${safetyRuntime.blocked_actions_count ?? "?"}`;
  plannerContextJson.textContent = JSON.stringify(context, null, 2);
}

function renderPlannerTrace(trace = null) {
  if (!trace) {
    plannerTracePanel.dataset.state = "empty";
    plannerTraceMode.textContent = "not run";
    plannerTraceSource.textContent = "unknown";
    plannerTraceValidation.textContent = "not applicable";
    plannerTraceFallback.textContent = "none";
    plannerTraceOutput.textContent = "unknown";
    plannerTraceContext.textContent = "0 elements; 0 events; desktop off";
    return;
  }

  const contextSummary = trace.context_summary ?? {};
  const executableActions = Array.isArray(contextSummary.executable_actions)
    ? contextSummary.executable_actions
    : [];
  const validation = trace.validation_reason
    ? `${displayRuntimeActuation(trace.validation_status)}: ${compactText(trace.validation_reason, 96)}`
    : displayRuntimeActuation(trace.validation_status || "not_applicable");
  const fallback = trace.fallback_used
    ? `yes: ${compactText(trace.fallback_reason || "fallback used", 96)}`
    : "no";

  plannerTracePanel.dataset.state = trace.fallback_used
    ? "fallback"
    : trace.validation_status === "rejected"
      ? "rejected"
      : "ready";
  plannerTraceMode.textContent = displayRuntimeActuation(trace.planner_mode || "unknown");
  plannerTraceSource.textContent = displayRuntimeActuation(trace.planner_source || "unknown");
  plannerTraceValidation.textContent = validation;
  plannerTraceFallback.textContent = fallback;
  plannerTraceOutput.textContent = displayRuntimeActuation(trace.output_action_type || "unknown");
  plannerTraceContext.textContent = `${contextSummary.visible_element_count ?? 0} elements; ${
    contextSummary.recent_event_count ?? 0
  } events; desktop ${contextSummary.desktop_control ? "on" : "off"}; exec ${
    executableActions.length ? executableActions.join(", ") : "none"
  }`;
}

async function loadDemoPlannerEvaluation() {
  plannerEvaluationPanel.dataset.state = "running";
  loadPlannerEvaluationButton.disabled = true;
  plannerEvaluationStatus.textContent = "Loading demo planner evaluation...";
  plannerEvaluationSummary.hidden = true;
  plannerEvaluationResults.replaceChildren();
  statusText.textContent = "loading planner evaluation...";

  try {
    const response = await fetch("/planner-evaluation/demo");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Planner evaluation failed with HTTP ${response.status}`);
    }

    renderPlannerEvaluation(payload);
    detailError.textContent = "none";
    statusText.textContent = "planner evaluation ready";
  } catch (error) {
    renderPlannerEvaluationError(error);
    detailError.textContent = `Planner evaluation failed: ${error.message || String(error)}`;
    detailsPanel.open = true;
    statusText.textContent = "planner evaluation failed";
  } finally {
    loadPlannerEvaluationButton.disabled = false;
  }
}

function renderPlannerEvaluation(report = null) {
  plannerEvaluationSummary.replaceChildren();
  plannerEvaluationResults.replaceChildren();

  if (!report) {
    plannerEvaluationPanel.dataset.state = "empty";
    plannerEvaluationStatus.textContent = "Not loaded yet.";
    plannerEvaluationSummary.hidden = true;
    plannerEvaluationResults.appendChild(plannerEvaluationEmptyState());
    return;
  }

  const summary = report.summary ?? {};
  const scenarios = Array.isArray(report.scenarios) ? report.scenarios : [];
  const allSafe =
    summary.all_safe_read_only === true && summary.all_expected_behaviors_passed !== false;
  const totalScenarioCount = summary.total_scenario_count ?? report.scenario_count ?? scenarios.length;
  const consistentScenarioCount = summary.consistent_scenario_count ?? summary.consistent_count ?? 0;
  const expectationCheckCount = summary.expectation_check_count ?? 0;
  const expectationPassCount = summary.expectation_pass_count ?? 0;

  plannerEvaluationPanel.dataset.state = allSafe ? "ready" : "warning";
  plannerEvaluationStatus.textContent =
    "Demo-only comparison loaded. risk_hint is label-level only; preview contracts are not executable.";
  plannerEvaluationSummary.hidden = false;
  setPlannerEvaluationSummary([
    ["Scenarios", String(totalScenarioCount)],
    ["Agreement", `${consistentScenarioCount}/${totalScenarioCount} scenarios`],
    ["Differences", String(summary.difference_count ?? summary.differences_count ?? "unknown")],
    ["AI rejections", String(summary.ai_rejection_count ?? summary.ai_rejections ?? "unknown")],
    ["Unsafe AI outputs", String(summary.unsafe_ai_output_count ?? summary.unsafe_ai_outputs ?? "unknown")],
    ["Expected checks", `${expectationPassCount}/${expectationCheckCount} passed`],
    ["Expectation failures", formatEvaluationScenarioList(summary.scenarios_with_expectation_failures)],
    ["Risk hints", formatEvaluationScenarioList(summary.scenarios_with_risk_hints)],
    ["Preview clicks", formatEvaluationScenarioList(summary.scenarios_with_preview_only_click_contracts)],
    ["Switch previews", formatEvaluationScenarioList(summary.scenarios_with_switch_app_preview_contracts)],
    ["Blocked readiness", formatEvaluationScenarioList(summary.scenarios_with_blocked_click_readiness)],
    ["External LLM calls", report.external_llm_calls ? "yes" : "no"],
    ["Safe read-only", allSafe ? "yes" : "check report"],
    [
      "Boundary",
      "risk_hint does not replace Safety Gate or Click Readiness; click/switch_app previews are not executable",
    ],
  ]);

  if (!scenarios.length) {
    plannerEvaluationResults.appendChild(plannerEvaluationEmptyState("No demo scenarios returned."));
    return;
  }

  for (const scenario of scenarios) {
    plannerEvaluationResults.appendChild(plannerEvaluationScenarioCard(scenario));
  }
}

function renderPlannerEvaluationError(error) {
  plannerEvaluationPanel.dataset.state = "error";
  plannerEvaluationStatus.textContent = "Planner evaluation could not be loaded.";
  plannerEvaluationSummary.hidden = true;
  plannerEvaluationSummary.replaceChildren();
  plannerEvaluationResults.replaceChildren(
    plannerEvaluationEmptyState(error.message || String(error))
  );
}

async function loadSandboxEvaluation() {
  sandboxEvaluationPanel.dataset.state = "running";
  loadSandboxEvaluationButton.disabled = true;
  sandboxEvaluationStatus.textContent = "Loading sandbox evaluation trace...";
  sandboxEvaluationControls.hidden = true;
  sandboxEvaluationQuickFilters.hidden = true;
  sandboxEvaluationCopyStatus.hidden = true;
  sandboxEvaluationCounts.hidden = true;
  sandboxEvaluationSummaryViz.hidden = true;
  sandboxEvaluationSummary.hidden = true;
  sandboxEvaluationTimeline.hidden = true;
  sandboxEvaluationResults.replaceChildren();
  statusText.textContent = "loading sandbox evaluation...";

  try {
    const response = await fetch("/sandbox-evaluation/demo");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Sandbox evaluation failed with HTTP ${response.status}`);
    }

    renderSandboxEvaluation(payload);
    detailError.textContent = "none";
    statusText.textContent = "sandbox evaluation ready";
  } catch (error) {
    renderSandboxEvaluationError(error);
    detailError.textContent = `Sandbox evaluation failed: ${error.message || String(error)}`;
    detailsPanel.open = true;
    statusText.textContent = "sandbox evaluation failed";
  } finally {
    loadSandboxEvaluationButton.disabled = false;
  }
}

function renderSandboxEvaluation(report = null) {
  currentSandboxEvaluationReport = report;
  sandboxEvaluationQuickFilters.replaceChildren();
  sandboxEvaluationSummary.replaceChildren();
  sandboxEvaluationSummaryViz.replaceChildren();
  sandboxEvaluationTimeline.replaceChildren();
  sandboxEvaluationResults.replaceChildren();

  if (!report) {
    sandboxEvaluationPanel.dataset.state = "empty";
    sandboxEvaluationStatus.textContent = "Not loaded yet.";
    sandboxEvaluationControls.hidden = true;
    sandboxEvaluationQuickFilters.hidden = true;
    sandboxEvaluationCopyStatus.hidden = true;
    sandboxEvaluationCounts.hidden = true;
    sandboxEvaluationSummaryViz.hidden = true;
    sandboxEvaluationSummary.hidden = true;
    sandboxEvaluationTimeline.hidden = true;
    sandboxEvaluationResults.appendChild(
      plannerEvaluationEmptyState("Load the sandbox trace to inspect Phase 8.1 gate scenarios.")
    );
    return;
  }

  const summary = report.summary ?? {};
  const scenarios = Array.isArray(report.scenarios) ? report.scenarios : [];
  populateSandboxEvaluationFilters(report, currentSandboxEvaluationFilters());
  const filters = currentSandboxEvaluationFilters();
  const filteredScenarios = sandboxEvaluationFilteredScenarios(scenarios, filters);
  const filteredSummary = summarizeSandboxScenarios(filteredScenarios);
  const totalScenarioCount = summary.total_scenario_count ?? report.scenario_count ?? scenarios.length;
  const passedScenarioCount = summary.passed_scenario_count ?? 0;
  const allPassed =
    summary.all_expected_outcomes_passed === true &&
    Number(summary.real_action_attempted_count ?? 0) === 0;

  sandboxEvaluationPanel.dataset.state = allPassed ? "ready" : "warning";
  sandboxEvaluationStatus.textContent =
    "Phase 8.1 deterministic sandbox trace loaded. This is debug output, not execution permission.";
  sandboxEvaluationControls.hidden = false;
  renderSandboxQuickFilters(filters);
  sandboxEvaluationQuickFilters.hidden = false;
  renderSandboxEvaluationCounts(filteredSummary, totalScenarioCount);
  renderSandboxEvaluationSummaryVisualization(filteredSummary);
  sandboxEvaluationSummary.hidden = false;
  sandboxEvaluationTimeline.hidden = false;
  setSandboxEvaluationSummary([
    ["Scenarios", String(totalScenarioCount)],
    ["Visible", `${filteredSummary.total}/${totalScenarioCount} after filters`],
    ["Pass/fail", `${passedScenarioCount}/${totalScenarioCount} passed`],
    ["Visible pass/fail", `${filteredSummary.passed}/${filteredSummary.total} pass; ${filteredSummary.failed} fail`],
    [
      "Gate results",
      `${summary.gate_passed_count ?? 0} passed; ${summary.gate_blocked_count ?? 0} blocked`,
    ],
    ["Dry-run cases", String(summary.dry_run_scenario_count ?? "unknown")],
    ["Real-action enabled", String(summary.real_action_enabled_count ?? 0)],
    ["Real-action skipped", String(summary.real_action_skipped_count ?? 0)],
    ["Real-action attempted", String(summary.real_action_attempted_count ?? 0)],
    [
      "Post verification",
      `${summary.post_action_verification_planned_count ?? 0} planned`,
    ],
    ["Failure reasons", formatSandboxCodeMap(summary.failure_reason_codes)],
    ["Blockers", formatSandboxCodeMap(summary.blocker_codes)],
    ["Audit events", formatSandboxCodeMap(summary.audit_event_names)],
    [
      "Boundary",
      "read-only fixture report; dry-run or skipped only; no /execute call",
    ],
  ]);

  renderSandboxEvaluationTimeline(filteredScenarios);

  if (!scenarios.length) {
    sandboxEvaluationResults.appendChild(
      plannerEvaluationEmptyState("No sandbox evaluation scenarios returned.")
    );
    return;
  }

  if (!filteredScenarios.length) {
    sandboxEvaluationResults.appendChild(
      sandboxEvaluationEmptyState("No sandbox scenarios match the active filters.", filters)
    );
    return;
  }

  for (const group of sandboxEvaluationScenarioGroups(filteredScenarios, filters)) {
    sandboxEvaluationResults.appendChild(sandboxEvaluationScenarioGroupSection(group));
  }
}

function renderSandboxEvaluationError(error) {
  sandboxEvaluationPanel.dataset.state = "error";
  sandboxEvaluationStatus.textContent = "Sandbox evaluation trace could not be loaded.";
  currentSandboxEvaluationReport = null;
  sandboxEvaluationControls.hidden = true;
  sandboxEvaluationQuickFilters.hidden = true;
  sandboxEvaluationCopyStatus.hidden = true;
  sandboxEvaluationCounts.hidden = true;
  sandboxEvaluationSummaryViz.hidden = true;
  sandboxEvaluationSummary.hidden = true;
  sandboxEvaluationTimeline.hidden = true;
  sandboxEvaluationSummaryViz.replaceChildren();
  sandboxEvaluationSummary.replaceChildren();
  sandboxEvaluationTimeline.replaceChildren();
  sandboxEvaluationResults.replaceChildren(
    plannerEvaluationEmptyState(error.message || String(error))
  );
}

async function loadPhase9Experiment() {
  phase9ExperimentPanel.dataset.state = "running";
  loadPhase9ExperimentButton.disabled = true;
  phase9ExperimentStatus.textContent = "Loading Phase 9 dry-run harness report...";
  phase9ExperimentControls.hidden = true;
  phase9QuickFilters.hidden = true;
  phase9ExportCopyStatus.hidden = true;
  phase9Counts.hidden = true;
  phase9ExperimentSummary.hidden = true;
  phase9ExperimentTimeline.hidden = true;
  phase9ExperimentResults.replaceChildren();
  statusText.textContent = "loading Phase 9 harness...";

  try {
    // A real-action system would hand off after a gate pass; Phase 9 keeps that
    // handoff absent and only loads deterministic dry-run fixture JSON.
    const response = await fetch("/phase9-experiment/demo");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Phase 9 harness failed with HTTP ${response.status}`);
    }

    renderPhase9Experiment(payload);
    detailError.textContent = "none";
    statusText.textContent = "Phase 9 harness ready";
  } catch (error) {
    renderPhase9ExperimentError(error);
    detailError.textContent = `Phase 9 harness failed: ${error.message || String(error)}`;
    detailsPanel.open = true;
    statusText.textContent = "Phase 9 harness failed";
  } finally {
    loadPhase9ExperimentButton.disabled = false;
  }
}

function renderPhase9Experiment(report = null) {
  currentPhase9ExperimentReport = report;
  phase9QuickFilters.replaceChildren();
  phase9ExportCopyStatus.hidden = true;
  phase9Counts.replaceChildren();
  phase9ExperimentSummary.replaceChildren();
  phase9ExperimentTimeline.replaceChildren();
  phase9ExperimentResults.replaceChildren();

  if (!report) {
    phase9ExperimentPanel.dataset.state = "empty";
    phase9ExperimentStatus.textContent = "Not loaded yet.";
    phase9ExperimentControls.hidden = true;
    phase9QuickFilters.hidden = true;
    phase9ExportCopyStatus.hidden = true;
    phase9Counts.hidden = true;
    phase9ExperimentSummary.hidden = true;
    phase9ExperimentTimeline.hidden = true;
    phase9ExperimentResults.appendChild(
      plannerEvaluationEmptyState("Load the Phase 9 harness report to inspect dry-run gate output.")
    );
    return;
  }

  const summary = report.summary ?? {};
  const scenarios = Array.isArray(report.scenarios) ? report.scenarios : [];
  populatePhase9ExperimentFilters(report, currentPhase9ExperimentFilters());
  const filters = currentPhase9ExperimentFilters();
  const filteredScenarios = phase9ExperimentFilteredScenarios(scenarios, filters);
  const filteredSummary = summarizePhase9ExperimentScenarios(filteredScenarios);
  const totalScenarioCount = summary.total_scenario_count ?? report.scenario_count ?? scenarios.length;
  const allPassed =
    summary.all_expected_outcomes_passed === true &&
    Number(summary.real_action_attempted_count ?? 0) === 0;

  phase9ExperimentPanel.dataset.state = allPassed ? "ready" : "warning";
  phase9ExperimentStatus.textContent =
    "Phase 9.1 dry-run harness loaded. This is read-only debug output, not execution permission.";
  phase9ExperimentControls.hidden = false;
  renderPhase9QuickFilters(filters);
  phase9QuickFilters.hidden = false;
  renderPhase9ExperimentCounts(filteredSummary, totalScenarioCount);
  phase9ExperimentSummary.hidden = false;
  phase9ExperimentTimeline.hidden = false;
  setPhase9ExperimentSummary([
    ["Experiment", report.report_type || "phase9_minimal_sandbox_experiment"],
    ["Phase", `${report.phase || "phase9_1"} exposed by ${report.cockpit_exposure_phase || "phase9_2"}`],
    [
      "Export bundle",
      report.phase9_export_bundle ? "Phase 9.4 bundle available" : "client-side fallback available",
    ],
    ["Scenarios", String(totalScenarioCount)],
    ["Visible", `${filteredSummary.total}/${totalScenarioCount} after filters`],
    ["Pass/fail", `${summary.passed_scenario_count ?? 0}/${totalScenarioCount} passed`],
    ["Visible pass/fail", `${filteredSummary.passed}/${filteredSummary.total} pass; ${filteredSummary.failed} fail`],
    [
      "Gate results",
      `${summary.gate_passed_count ?? 0} passed; ${summary.gate_blocked_count ?? 0} blocked`,
    ],
    ["Dry-run cases", String(summary.dry_run_scenario_count ?? "unknown")],
    ["Real-action enabled", String(summary.real_action_enabled_count ?? 0)],
    ["Real-action skipped", String(summary.real_action_skipped_count ?? 0)],
    ["Real-action attempted", String(summary.real_action_attempted_count ?? 0)],
    ["Visible skipped", String(filteredSummary.skipped)],
    ["Visible blocked", String(filteredSummary.blocked)],
    ["Post verification", `${summary.post_action_verification_planned_count ?? 0} planned`],
    [
      "Boundary",
      "read-only Phase 9 harness; mock approval/stop/verification/rollback only; no /execute call",
    ],
  ]);

  renderPhase9ExperimentTimeline(filteredScenarios, filters);

  if (!scenarios.length) {
    phase9ExperimentResults.appendChild(
      plannerEvaluationEmptyState("No Phase 9 harness scenarios returned.")
    );
    return;
  }

  if (!filteredScenarios.length) {
    phase9ExperimentResults.appendChild(
      phase9ExperimentEmptyState("No Phase 9 harness scenarios match the active filters.", filters)
    );
    return;
  }

  for (const group of phase9ExperimentScenarioGroups(filteredScenarios, filters)) {
    phase9ExperimentResults.appendChild(phase9ExperimentScenarioGroupSection(group));
  }
}

function renderPhase9ExperimentError(error) {
  phase9ExperimentPanel.dataset.state = "error";
  phase9ExperimentStatus.textContent = "Phase 9 dry-run harness could not be loaded.";
  currentPhase9ExperimentReport = null;
  phase9ExperimentControls.hidden = true;
  phase9QuickFilters.hidden = true;
  phase9ExportCopyStatus.hidden = true;
  phase9Counts.hidden = true;
  phase9ExperimentSummary.hidden = true;
  phase9ExperimentTimeline.hidden = true;
  phase9ExperimentSummary.replaceChildren();
  phase9ExperimentTimeline.replaceChildren();
  phase9ExperimentResults.replaceChildren(plannerEvaluationEmptyState(error.message || String(error)));
}

function setPhase9ExperimentSummary(rows) {
  phase9ExperimentSummary.replaceChildren();

  for (const [label, value] of rows) {
    phase9ExperimentSummary.appendChild(plannerEvaluationFact(label, value));
  }
}

function phase9ExperimentEmptyState(message, filters = {}) {
  const container = document.createElement("div");
  const title = document.createElement("p");
  const detail = document.createElement("p");

  container.className = "sandbox-evaluation-empty-state";
  container.dataset.phase9EmptyState = "true";
  title.className = "sandbox-evaluation-empty-title";
  title.textContent = message;
  detail.className = "sandbox-evaluation-empty-detail";
  detail.textContent = `Active filters: ${phase9ActiveFilterDescription(filters)}.`;
  container.append(title, detail);
  return container;
}

function phase9ActiveFilterDescription(filters = {}) {
  return [
    `outcome ${filters.outcome || "all"}`,
    `gate blocker ${filters.gateBlocker || "all"}`,
    `approval ${filters.approval || "all"}`,
    `risk ${filters.risk || "all"}`,
    `readiness ${filters.readiness || "all"}`,
    `scenario type ${filters.scenarioType || "all"}`,
    `group ${filters.groupMode || "scenario_type"}`,
    `audit group ${filters.auditGroupMode || "scenario"}`,
    `audit order ${filters.auditSortMode || "original"}`,
    `quick group ${filters.quickGroup || "all"}`,
  ].join("; ");
}

function currentPhase9ExperimentFilters() {
  return {
    outcome: phase9OutcomeFilter.value || "all",
    gateBlocker: phase9GateBlockerFilter.value || "all",
    approval: phase9ApprovalFilter.value || "all",
    risk: phase9RiskFilter.value || "all",
    readiness: phase9ReadinessFilter.value || "all",
    scenarioType: phase9ScenarioTypeFilter.value || "all",
    groupMode: phase9GroupMode.value || "scenario_type",
    auditGroupMode: phase9AuditGroupMode.value || "scenario",
    auditSortMode: phase9AuditSortMode.value || "original",
    quickGroup: currentPhase9QuickFilterGroup || "all",
  };
}

function populatePhase9ExperimentFilters(report, activeFilters) {
  const scenarios = Array.isArray(report?.scenarios) ? report.scenarios : [];
  const scenarioTypes = uniqueSortedValues(scenarios.map((scenario) => phase9ScenarioType(scenario)));
  const gateBlockers = uniqueSortedValues(scenarios.flatMap((scenario) => phase9GateBlockerCodes(scenario)));

  setSelectOptions(
    phase9ScenarioTypeFilter,
    [["all", "all scenario types"]].concat(
      scenarioTypes.map((scenarioType) => [scenarioType, displayPhase9ScenarioType(scenarioType)])
    ),
    activeFilters.scenarioType
  );
  setSelectOptions(
    phase9GateBlockerFilter,
    [["all", "all gate blockers"]].concat(gateBlockers.map((blocker) => [blocker, blocker])),
    activeFilters.gateBlocker
  );
  phase9OutcomeFilter.value = ["all", "pass", "fail", "skipped", "blocked"].includes(
    activeFilters.outcome
  )
    ? activeFilters.outcome
    : "all";
  phase9ApprovalFilter.value = ["all", "present", "missing", "checked"].includes(
    activeFilters.approval
  )
    ? activeFilters.approval
    : "all";
  phase9RiskFilter.value = ["all", "low", "medium", "high", "unknown"].includes(
    activeFilters.risk
  )
    ? activeFilters.risk
    : "all";
  phase9ReadinessFilter.value = ["all", "ready", "blocked"].includes(activeFilters.readiness)
    ? activeFilters.readiness
    : "all";
  phase9GroupMode.value = ["scenario_type", "outcome", "gate", "risk"].includes(
    activeFilters.groupMode
  )
    ? activeFilters.groupMode
    : "scenario_type";
  phase9AuditGroupMode.value = ["scenario", "gate", "severity", "event"].includes(
    activeFilters.auditGroupMode
  )
    ? activeFilters.auditGroupMode
    : "scenario";
  phase9AuditSortMode.value = ["original", "scenario_original"].includes(
    activeFilters.auditSortMode
  )
    ? activeFilters.auditSortMode
    : "original";
}

function phase9ExperimentFilteredScenarios(scenarios, filters) {
  return (Array.isArray(scenarios) ? scenarios : []).filter((scenario) =>
    phase9ScenarioMatchesFilters(scenario, filters)
  );
}

function phase9ScenarioMatchesFilters(scenario, filters = {}) {
  const outcome = phase9OutcomeKind(scenario);
  const gateBlockers = phase9GateBlockerCodes(scenario);

  if ((filters.outcome || "all") !== "all" && filters.outcome !== outcome) {
    return false;
  }

  if ((filters.gateBlocker || "all") !== "all" && !gateBlockers.includes(filters.gateBlocker)) {
    return false;
  }

  if ((filters.approval || "all") !== "all" && !phase9ApprovalMatches(scenario, filters.approval)) {
    return false;
  }

  if ((filters.risk || "all") !== "all" && filters.risk !== phase9RiskLevel(scenario)) {
    return false;
  }

  if ((filters.readiness || "all") !== "all" && filters.readiness !== phase9ReadinessStatus(scenario)) {
    return false;
  }

  if ((filters.scenarioType || "all") !== "all" && filters.scenarioType !== phase9ScenarioType(scenario)) {
    return false;
  }

  return phase9ScenarioMatchesQuickGroup(scenario, filters.quickGroup || "all");
}

function phase9ApprovalMatches(scenario, approvalFilter) {
  if (approvalFilter === "present") {
    return scenario.user_approval_present === true;
  }

  if (approvalFilter === "missing") {
    return scenario.user_approval_present !== true;
  }

  if (approvalFilter === "checked") {
    return scenario.mock_approval_checked === true;
  }

  return true;
}

function phase9ScenarioMatchesQuickGroup(scenario, quickGroup) {
  if (!quickGroup || quickGroup === "all") {
    return true;
  }

  const gateBlockers = phase9GateBlockerCodes(scenario);

  if (quickGroup === "blockers") {
    return scenario.gate_passed === false || gateBlockers.length > 0;
  }

  if (quickGroup === "approval") {
    return (
      scenario.mock_approval_checked === true ||
      scenario.user_approval_present !== true ||
      gateBlockers.includes("missing_user_approval")
    );
  }

  if (quickGroup === "risk") {
    return ["high", "unknown", "medium"].includes(phase9RiskLevel(scenario));
  }

  if (quickGroup === "readiness") {
    return phase9ReadinessStatus(scenario) === "blocked" || gateBlockers.includes("readiness_not_ready");
  }

  if (quickGroup === "skipped") {
    return scenario.real_action_skipped === true;
  }

  return true;
}

function phase9ExperimentScenarioGroups(scenarios, filters) {
  const groups = new Map();

  for (const scenario of scenarios) {
    const key = phase9ExperimentScenarioGroupKey(scenario, filters);

    if (!groups.has(key)) {
      groups.set(key, {
        key,
        title: phase9ExperimentScenarioGroupTitle(scenario, filters),
        scenarios: [],
      });
    }

    groups.get(key).scenarios.push(scenario);
  }

  return Array.from(groups.values());
}

function phase9ExperimentScenarioGroupKey(scenario, filters) {
  const groupMode = filters.groupMode || "scenario_type";

  if (groupMode === "outcome") {
    return `outcome:${phase9OutcomeKind(scenario)}`;
  }

  if (groupMode === "gate") {
    return `gate:${scenario.gate_passed === true ? "passed" : "blocked"}`;
  }

  if (groupMode === "risk") {
    return `risk:${phase9RiskLevel(scenario)}`;
  }

  return `type:${phase9ScenarioType(scenario)}`;
}

function phase9ExperimentScenarioGroupTitle(scenario, filters) {
  const groupMode = filters.groupMode || "scenario_type";

  if (groupMode === "outcome") {
    return `Outcome: ${sandboxEvaluationStatusLabel(phase9OutcomeKind(scenario))}`;
  }

  if (groupMode === "gate") {
    return `Gate: ${scenario.gate_passed === true ? "passed" : "blocked"}`;
  }

  if (groupMode === "risk") {
    return `Risk: ${phase9RiskLevel(scenario)}`;
  }

  return displayPhase9ScenarioType(phase9ScenarioType(scenario));
}

function phase9ExperimentScenarioGroupSection(group) {
  const section = document.createElement("section");
  const title = document.createElement("p");

  section.className = "sandbox-evaluation-scenario-group";
  section.dataset.phase9ScenarioGroup = group.key;
  title.className = "sandbox-evaluation-scenario-group-title";
  title.textContent = `${group.title} (${group.scenarios.length})`;
  section.appendChild(title);

  for (const scenario of group.scenarios) {
    section.appendChild(phase9ExperimentScenarioCard(scenario));
  }

  return section;
}

function summarizePhase9ExperimentScenarios(scenarios) {
  const safeScenarios = Array.isArray(scenarios) ? scenarios : [];

  return {
    total: safeScenarios.length,
    passed: safeScenarios.filter((scenario) => scenario.passed === true).length,
    failed: safeScenarios.filter((scenario) => scenario.passed !== true).length,
    skipped: safeScenarios.filter((scenario) => scenario.real_action_skipped === true).length,
    blocked: safeScenarios.filter(
      (scenario) => scenario.actual_outcome?.status === "blocked" || scenario.gate_passed === false
    ).length,
    approvalPresent: safeScenarios.filter((scenario) => scenario.user_approval_present === true).length,
    readinessReady: safeScenarios.filter((scenario) => scenario.readiness_ready === true).length,
  };
}

function renderPhase9ExperimentCounts(summary, totalScenarioCount) {
  phase9Counts.replaceChildren();
  phase9Counts.hidden = false;

  for (const [label, value, tone] of [
    ["total", String(totalScenarioCount), "neutral"],
    ["visible", String(summary.total), "neutral"],
    ["passed", String(summary.passed), "ok"],
    ["failed", String(summary.failed), summary.failed > 0 ? "risk" : "neutral"],
    ["skipped", String(summary.skipped), summary.skipped > 0 ? "warn" : "neutral"],
    ["blocked", String(summary.blocked), summary.blocked > 0 ? "risk" : "neutral"],
    ["approval", String(summary.approvalPresent), "ok"],
    ["ready", String(summary.readinessReady), "ok"],
  ]) {
    const chip = document.createElement("div");
    const countValue = document.createElement("span");
    const countLabel = document.createElement("span");

    chip.className = "sandbox-evaluation-count";
    chip.dataset.phase9CountKey = label;
    chip.dataset.countKey = label;
    chip.dataset.tone = tone;
    countValue.className = "sandbox-evaluation-count-value";
    countValue.textContent = value;
    countLabel.className = "sandbox-evaluation-count-label";
    countLabel.textContent = label;
    chip.append(countValue, countLabel);
    phase9Counts.appendChild(chip);
  }
}

function renderPhase9QuickFilters(filters) {
  phase9QuickFilters.replaceChildren();

  for (const [groupKey, group] of Object.entries(PHASE9_QUICK_FILTER_GROUPS)) {
    const button = document.createElement("button");

    button.type = "button";
    button.className = "sandbox-evaluation-quick-filter";
    button.dataset.phase9QuickFilter = groupKey;
    button.title = group.description;
    button.setAttribute("aria-pressed", String(filters.quickGroup === groupKey));
    button.textContent = group.label;
    button.addEventListener("click", () => {
      currentPhase9QuickFilterGroup =
        currentPhase9QuickFilterGroup === groupKey ? "all" : groupKey;
      renderPhase9Experiment(currentPhase9ExperimentReport);
    });
    phase9QuickFilters.appendChild(button);
  }
}

function resetPhase9ExperimentFilters() {
  phase9OutcomeFilter.value = "all";
  phase9GateBlockerFilter.value = "all";
  phase9ApprovalFilter.value = "all";
  phase9RiskFilter.value = "all";
  phase9ReadinessFilter.value = "all";
  phase9ScenarioTypeFilter.value = "all";
  phase9GroupMode.value = "scenario_type";
  phase9AuditGroupMode.value = "scenario";
  phase9AuditSortMode.value = "original";
  currentPhase9QuickFilterGroup = "all";
  phase9ExportCopyStatus.hidden = true;
  renderPhase9Experiment(currentPhase9ExperimentReport);
}

async function copyPhase9ExportPayload(payloadKind) {
  const payload = buildPhase9ExportPayload(payloadKind);

  phase9ExportCopyStatus.hidden = false;

  if (!payload) {
    phase9ExportCopyStatus.textContent = "No Phase 9 report loaded.";
    return;
  }

  if (!navigator.clipboard?.writeText) {
    phase9ExportCopyStatus.textContent = "Clipboard unavailable in this browser.";
    return;
  }

  try {
    await navigator.clipboard.writeText(
      typeof payload === "string" ? payload : JSON.stringify(payload, null, 2)
    );
    phase9ExportCopyStatus.textContent = phase9ExportCopyStatusText(payloadKind);
  } catch (error) {
    phase9ExportCopyStatus.textContent = `Copy failed: ${error.message || String(error)}`;
  }
}

function buildPhase9ExportPayload(payloadKind) {
  const report = currentPhase9ExperimentReport;

  if (!report) {
    return null;
  }

  const bundle = phase9ReproducibilityBundle(report);

  if (payloadKind === "ai_summary") {
    return bundle.ai_readable_summary || buildPhase9AIReadableSummary(bundle.phase9_report);
  }

  if (payloadKind === "json_report") {
    return bundle.phase9_report || buildPhase9ClientExportReport(report);
  }

  return bundle;
}

function phase9ExportCopyStatusText(payloadKind) {
  if (payloadKind === "ai_summary") {
    return "Phase 9 AI summary copied.";
  }

  if (payloadKind === "json_report") {
    return "Phase 9 JSON report copied.";
  }

  return "Phase 9 reproducibility bundle copied.";
}

function phase9ReproducibilityBundle(report) {
  if (report?.phase9_export_bundle && typeof report.phase9_export_bundle === "object") {
    return report.phase9_export_bundle;
  }

  const phase9Report = buildPhase9ClientExportReport(report);
  return {
    bundle_type: "phase9_reproducibility_bundle",
    bundle_version: "phase9_repro_bundle_v1",
    generated_at: "deterministic_phase9_fixture",
    project_phase: "phase_9_4",
    phase9_report: phase9Report,
    ai_readable_summary: buildPhase9AIReadableSummary(phase9Report),
    minimal_reproduction_metadata: {
      scenario_ids: phase9Report.scenario_ids,
      experiment_id: phase9Report.experiment_id,
      stable_input_assumptions: [
        "fixture-backed Phase 9 harness data",
        "mock approval, emergency stop, verification, and rollback state",
        "no live OS state or real desktop screenshots",
      ],
      audit_event_order: phase9Report.audit_timeline,
      failure_reason_codes: phase9Report.failure_reason_codes,
      blocker_codes: phase9Report.blocker_codes,
      safety_boundary_statement: phase9SafetyBoundaryStatement(),
    },
    safety_boundary_statement: phase9SafetyBoundaryStatement(),
  };
}

function buildPhase9ClientExportReport(report) {
  const scenarios = Array.isArray(report?.scenarios) ? report.scenarios : [];
  const exportedScenarios = scenarios.map((scenario) => phase9ClientExportScenario(scenario));
  const failureReasonCodes = uniqueSortedValues(
    exportedScenarios.flatMap((scenario) => sandboxCodes(scenario.failure_reason_codes))
  );
  const blockerCodes = uniqueSortedValues(
    exportedScenarios.flatMap((scenario) => sandboxCodes(scenario.blocker_codes))
  );
  const auditEventNames = uniqueSortedValues(
    exportedScenarios.flatMap((scenario) => sandboxCodes(scenario.audit_event_names))
  );
  const summary = report?.summary || {};

  return {
    report_version: "phase9_export_v1",
    generated_at: "deterministic_phase9_fixture",
    project_phase: "phase_9_4",
    source_report_type: report?.report_type || "phase9_minimal_sandbox_experiment",
    source_phase: report?.phase || "phase9_1",
    dry_run: exportedScenarios.every((scenario) => scenario.dry_run === true),
    real_action_enabled: exportedScenarios.some((scenario) => scenario.real_action_enabled === true),
    real_action_skipped: exportedScenarios.some((scenario) => scenario.real_action_skipped === true),
    experiment_id: phase9CommonValue(exportedScenarios.map((scenario) => scenario.experiment_id)),
    scenario_ids: exportedScenarios.map((scenario) => scenario.scenario_id),
    sandbox_scope: phase9CommonScope(exportedScenarios),
    action_type: phase9CommonValue(exportedScenarios.map((scenario) => scenario.action_type)),
    gate_passed: exportedScenarios.every((scenario) => scenario.gate_passed === true),
    actual_outcome: {
      status: phase9AggregateStatus(summary, exportedScenarios),
      scenario_count: exportedScenarios.length,
      gate_passed_count: Number(summary.gate_passed_count || 0),
      gate_blocked_count: Number(summary.gate_blocked_count || 0),
      real_action_attempted: false,
    },
    failure_reason_codes: failureReasonCodes,
    blocker_codes: blockerCodes,
    target_risk_hint: phase9CommonValue(
      exportedScenarios.map((scenario) => scenario.target_risk_hint)
    ),
    target_confidence: phase9CommonNumber(
      exportedScenarios.map((scenario) => scenario.target_confidence)
    ),
    readiness_ready: exportedScenarios.every((scenario) => scenario.readiness_ready === true),
    user_approval_present: exportedScenarios.every(
      (scenario) => scenario.user_approval_present === true
    ),
    emergency_stop_available: exportedScenarios.every(
      (scenario) => scenario.emergency_stop_available === true
    ),
    post_action_verification_planned: exportedScenarios.every(
      (scenario) => scenario.post_action_verification_planned === true
    ),
    rollback_plan_recorded: exportedScenarios.every(
      (scenario) => scenario.rollback_plan_recorded === true
    ),
    audit_event_names: auditEventNames,
    audit_timeline: phase9ClientAuditTimeline(exportedScenarios),
    notes: uniqueSortedValues(exportedScenarios.flatMap((scenario) => sandboxCodes(scenario.notes))),
    scenarios: exportedScenarios,
  };
}

function phase9ClientExportScenario(scenario) {
  return {
    report_version: "phase9_export_v1",
    generated_at: "deterministic_phase9_fixture",
    project_phase: "phase_9_4",
    experiment_id: scenario.experiment_id || "",
    scenario_id: scenario.scenario_id || "",
    scenario_name: scenario.scenario_name || "",
    dry_run: scenario.dry_run === true,
    real_action_enabled: scenario.real_action_enabled === true,
    real_action_skipped: scenario.real_action_skipped === true,
    sandbox_scope: phase9SanitizedScope(scenario.sandbox_scope),
    action_type: scenario.action_type || "",
    gate_passed: scenario.gate_passed === true,
    actual_outcome: scenario.actual_outcome || {},
    failure_reason_codes: sandboxCodes(scenario.failure_reason_codes),
    blocker_codes: sandboxCodes(scenario.blocker_codes),
    target_risk_hint: scenario.target_risk_hint || "",
    target_confidence: Number.isFinite(scenario.target_confidence) ? scenario.target_confidence : null,
    readiness_ready: scenario.readiness_ready === true,
    user_approval_present: scenario.user_approval_present === true,
    emergency_stop_available: scenario.emergency_stop_available === true,
    post_action_verification_planned: scenario.post_action_verification_planned === true,
    rollback_plan_recorded: scenario.rollback_plan_recorded === true,
    audit_event_names: sandboxCodes(scenario.audit_event_names),
    audit_timeline: phase9ScenarioAuditTimeline(scenario),
    notes: sandboxCodes(scenario.notes),
  };
}

function phase9ScenarioAuditTimeline(scenario) {
  return sandboxCodes(scenario.audit_event_names).map((eventName, index) => ({
    order: index + 1,
    scenario_id: scenario.scenario_id || "",
    event_name: eventName,
    gate_passed: scenario.gate_passed === true,
    failure_reason_codes: sandboxCodes(scenario.failure_reason_codes),
    blocker_codes: sandboxCodes(scenario.blocker_codes),
  }));
}

function phase9ClientAuditTimeline(scenarios) {
  let globalOrder = 0;
  return scenarios.flatMap((scenario) =>
    phase9ScenarioAuditTimeline(scenario).map((event) => {
      globalOrder += 1;
      return { ...event, global_order: globalOrder, scenario_order: event.order };
    })
  );
}

function buildPhase9AIReadableSummary(exportReport = {}) {
  const actualOutcome = exportReport.actual_outcome || {};
  return [
    "Project phase: phase_9_4 Phase 9 dry-run harness export.",
    `Run mode: dry_run=${formatSandboxBool(exportReport.dry_run)}; real_action_enabled=${formatSandboxBool(
      exportReport.real_action_enabled
    )}; real_action_skipped=${formatSandboxBool(exportReport.real_action_skipped)}.`,
    `Gate result: ${
      exportReport.gate_passed === true ? "passed" : "blocked or mixed"
    }; status=${actualOutcome.status || "unknown"}; scenarios=${
      actualOutcome.scenario_count || 0
    }; passed=${actualOutcome.gate_passed_count || 0}; blocked=${
      actualOutcome.gate_blocked_count || 0
    }.`,
    `Blockers/failure reasons: failure_reason_codes=${formatSandboxCodeList(
      exportReport.failure_reason_codes
    )}; blocker_codes=${formatSandboxCodeList(exportReport.blocker_codes)}.`,
    `Gate support state: approval_present=${formatSandboxBool(
      exportReport.user_approval_present
    )}; emergency_stop_available=${formatSandboxBool(
      exportReport.emergency_stop_available
    )}; verification_planned=${formatSandboxBool(
      exportReport.post_action_verification_planned
    )}; rollback_recorded=${formatSandboxBool(exportReport.rollback_plan_recorded)}.`,
    `Recommended next debugging focus: ${phase9RecommendedFocus(exportReport)}.`,
    `Safety boundary: ${phase9SafetyBoundaryStatement()}`,
  ].join("\n");
}

function phase9RecommendedFocus(exportReport = {}) {
  const codes = new Set(
    sandboxCodes(exportReport.failure_reason_codes).concat(sandboxCodes(exportReport.blocker_codes))
  );
  const focusRules = [
    ["missing_action_contract", "inspect action-contract fixture generation"],
    ["missing_audit_plan", "inspect audit-plan fixture coverage"],
    ["missing_user_approval", "inspect mock approval binding and freshness"],
    ["stale_observation", "inspect observation freshness assumptions"],
    ["high_risk_target", "inspect risk classification and target selection"],
    ["high_risk_requires_approval", "inspect high-risk blocker mapping"],
    ["real_action_disabled", "confirm skipped-path reporting remains explicit"],
    ["readiness_not_ready", "inspect readiness blocker expectations"],
  ];
  const focus = focusRules
    .filter(([code]) => codes.has(code))
    .map(([, recommendation]) => recommendation);

  if (!focus.length && exportReport.gate_passed === true) {
    return "review successful dry-run audit order before any future design change";
  }

  return focus.length ? focus.slice(0, 3).join("; ") : "review gate status, failure codes, and audit ordering";
}

function phase9CommonValue(values) {
  const presentValues = values.filter((value) => value);
  if (!presentValues.length) {
    return "";
  }

  return presentValues.every((value) => value === presentValues[0]) ? presentValues[0] : "mixed";
}

function phase9CommonNumber(values) {
  const presentValues = values.filter((value) => Number.isFinite(value));
  if (!presentValues.length) {
    return null;
  }

  return presentValues.every((value) => value === presentValues[0]) ? presentValues[0] : null;
}

function phase9CommonScope(scenarios) {
  const scopes = scenarios.map((scenario) => scenario.sandbox_scope).filter((scope) => scope);
  if (!scopes.length) {
    return {};
  }

  const firstScope = JSON.stringify(scopes[0]);
  return scopes.every((scope) => JSON.stringify(scope) === firstScope) ? scopes[0] : { scope: "mixed" };
}

function phase9SanitizedScope(scope) {
  if (!scope || typeof scope !== "object") {
    return {};
  }

  return Object.fromEntries(
    Object.entries(scope).filter(([key]) => !["credential", "token", "secret", "password"].some(
      (fragment) => key.toLowerCase().includes(fragment)
    ))
  );
}

function phase9AggregateStatus(summary, scenarios) {
  if (!scenarios.length) {
    return "empty";
  }

  if (summary.all_expected_outcomes_passed !== true) {
    return "failed_expectation";
  }

  if (scenarios.some((scenario) => scenario.real_action_skipped === true)) {
    return "dry_run_with_skipped_paths";
  }

  return scenarios.every((scenario) => scenario.gate_passed === true)
    ? "all_gates_passed"
    : "mixed_gate_results";
}

function phase9SafetyBoundaryStatement() {
  return (
    "Phase 9.4 exports deterministic dry-run debug data only. Real desktop actions remain disabled, " +
    "and no action-performing endpoint is called."
  );
}

function setPhase9ScenarioDetailsOpen(open) {
  const detailsNodes = phase9ExperimentResults.querySelectorAll(
    "details[data-phase9-scenario-details='true']"
  );
  detailsNodes.forEach((details) => {
    details.open = open;
  });
}

function setPhase9AuditDetailsOpen(open) {
  const detailsNodes = phase9ExperimentPanel.querySelectorAll(
    "details[data-phase9-audit-event-details='true']"
  );
  detailsNodes.forEach((details) => {
    details.open = open;
  });
}

function phase9OutcomeKind(scenario) {
  return sandboxEvaluationStatusKind(scenario);
}

function phase9ScenarioType(scenario) {
  const failureReasons = sandboxCodes(scenario.failure_reason_codes);
  const blockerCodes = sandboxCodes(scenario.blocker_codes);

  if (scenario.real_action_skipped === true || failureReasons.includes("real_action_disabled")) {
    return "real_action_skipped";
  }

  if (failureReasons.includes("missing_user_approval")) {
    return "approval";
  }

  if (failureReasons.includes("high_risk_target") || phase9RiskLevel(scenario) !== "low") {
    return "risk";
  }

  if (failureReasons.includes("stale_observation") || blockerCodes.includes("stale_observation")) {
    return "phase7_freshness";
  }

  if (failureReasons.includes("missing_audit_plan")) {
    return "phase7_audit";
  }

  if (failureReasons.includes("missing_action_contract")) {
    return "phase7_contract";
  }

  if (failureReasons.includes("readiness_not_ready")) {
    return "readiness";
  }

  if (scenario.gate_passed === false) {
    return "phase7_gate";
  }

  return "dry_run_success";
}

function displayPhase9ScenarioType(scenarioType) {
  const labels = {
    dry_run_success: "dry-run success",
    real_action_skipped: "real-action skipped",
    approval: "approval gate",
    risk: "risk gate",
    readiness: "readiness gate",
    phase7_freshness: "Phase 7 freshness",
    phase7_audit: "Phase 7 audit",
    phase7_contract: "Phase 7 contract",
    phase7_gate: "Phase 7/8 gate",
  };

  return labels[scenarioType] || scenarioType || "unknown";
}

function phase9RiskLevel(scenario) {
  const riskHint = String(scenario.target_risk_hint || "").toLowerCase();

  if (riskHint === "high" || riskHint === "high_risk") {
    return "high";
  }

  if (riskHint === "medium" || riskHint === "medium_risk") {
    return "medium";
  }

  if (riskHint === "unknown" || !riskHint) {
    return "unknown";
  }

  return "low";
}

function phase9ReadinessStatus(scenario) {
  return scenario.readiness_ready === true ? "ready" : "blocked";
}

function phase9GateBlockerCodes(scenario) {
  return uniqueSortedValues(
    sandboxCodes(scenario.failure_reason_codes).concat(sandboxCodes(scenario.blocker_codes))
  );
}

function phase9ExperimentScenarioCard(scenario) {
  const card = document.createElement("article");
  const header = document.createElement("div");
  const titleBlock = document.createElement("div");
  const title = document.createElement("p");
  const subtitle = document.createElement("p");
  const badges = document.createElement("div");
  const details = document.createElement("details");
  const detailsSummary = document.createElement("summary");
  const facts = document.createElement("dl");
  const status = sandboxEvaluationStatusKind(scenario);
  const scope = scenario.sandbox_scope && typeof scenario.sandbox_scope === "object"
    ? scenario.sandbox_scope
    : {};

  card.className = "planner-evaluation-card";
  card.dataset.phase9HarnessCard = "true";
  card.dataset.status = status;
  card.dataset.experimentId = scenario.experiment_id || "";
  card.dataset.scenarioId = scenario.scenario_id || "";
  card.dataset.scenarioType = phase9ScenarioType(scenario);
  card.dataset.outcome = phase9OutcomeKind(scenario);
  card.dataset.gatePassed = String(scenario.gate_passed === true);
  card.dataset.gateBlockers = phase9GateBlockerCodes(scenario).join(",");
  card.dataset.dryRun = String(scenario.dry_run === true);
  card.dataset.realActionSkipped = String(scenario.real_action_skipped === true);
  card.dataset.mockApprovalChecked = String(scenario.mock_approval_checked === true);
  card.dataset.userApprovalPresent = String(scenario.user_approval_present === true);
  card.dataset.emergencyStopAvailable = String(scenario.emergency_stop_available === true);
  card.dataset.postActionVerificationPlanned = String(
    scenario.post_action_verification_planned === true
  );
  card.dataset.rollbackPlanRecorded = String(scenario.rollback_plan_recorded === true);
  card.dataset.actionType = scenario.action_type || "";
  card.dataset.targetRiskHint = scenario.target_risk_hint || "";
  card.dataset.riskLevel = phase9RiskLevel(scenario);
  card.dataset.readinessStatus = phase9ReadinessStatus(scenario);
  card.dataset.targetConfidence = Number.isFinite(scenario.target_confidence)
    ? scenario.target_confidence.toFixed(2)
    : "";
  card.dataset.sandboxScope = JSON.stringify(scope);
  card.dataset.different = String(scenario.passed !== true || scenario.real_action_skipped === true);
  card.dataset.risk = String(
    scenario.target_risk_hint === "high_risk" || scenario.target_risk_hint === "unknown"
  );

  header.className = "sandbox-evaluation-card-header";
  titleBlock.className = "sandbox-evaluation-card-title-block";
  title.className = "planner-evaluation-card-title";
  title.textContent = scenario.scenario_name || scenario.experiment_id || "Phase 9 harness scenario";
  subtitle.className = "sandbox-evaluation-card-subtitle";
  subtitle.textContent = `${scenario.experiment_id || "unknown experiment"} / ${
    scenario.scenario_id || "unknown scenario"
  } / actual ${scenario.actual_outcome?.status || "unknown"}`;
  badges.className = "sandbox-evaluation-badges";
  badges.appendChild(sandboxEvaluationPrimaryStatusChip(scenario));
  for (const [label, value, tone] of phase9ExperimentBadges(scenario)) {
    badges.appendChild(sandboxEvaluationBadge(label, value, tone));
  }
  titleBlock.append(title, subtitle);
  header.append(titleBlock, badges);

  details.className = "sandbox-evaluation-scenario-details";
  details.dataset.phase9ScenarioDetails = "true";
  details.dataset.testHook = "phase9-scenario-details";
  detailsSummary.textContent = "Harness fields";
  facts.className = "planner-evaluation-facts";
  for (const [label, value] of phase9ExperimentRows(scenario)) {
    facts.appendChild(plannerEvaluationFact(label, value));
  }
  details.append(facts, phase9ExperimentAuditTimeline(scenario), phase9ExperimentTraceDetails(scenario));
  details.prepend(detailsSummary);
  card.append(header, phase9ExperimentCompactLine(scenario), details);
  return card;
}

function phase9ExperimentRows(scenario) {
  return [
    ["Experiment ID", scenario.experiment_id || "unknown"],
    ["Scenario ID", scenario.scenario_id || "unknown"],
    ["Gate", scenario.gate_passed === true ? "passed" : "blocked"],
    ["Dry-run", formatSandboxBool(scenario.dry_run)],
    [
      "Real action",
      `enabled ${formatSandboxBool(scenario.real_action_enabled)}; skipped ${formatSandboxBool(
        scenario.real_action_skipped
      )}; attempted ${formatSandboxBool(scenario.actual_outcome?.real_action_attempted)}`,
    ],
    [
      "Approval state",
      `mock checked ${formatSandboxBool(scenario.mock_approval_checked)}; present ${formatSandboxBool(
        scenario.user_approval_present
      )}`,
    ],
    [
      "Emergency stop",
      `available ${formatSandboxBool(scenario.emergency_stop_available)}; active ${formatSandboxBool(
        scenario.emergency_stop_active
      )}`,
    ],
    [
      "Verification",
      scenario.post_action_verification_planned === true ? "post-action plan recorded" : "not planned",
    ],
    ["Rollback", scenario.rollback_plan_recorded === true ? "mock rollback recorded" : "not recorded"],
    ["Failure reasons", formatSandboxCodeList(scenario.failure_reason_codes)],
    ["Blockers", formatSandboxCodeList(scenario.blocker_codes)],
    ["Audit events", formatSandboxCodeList(scenario.audit_event_names)],
    [
      "Target",
      `risk ${scenario.target_risk_hint || "none"}; confidence ${formatSandboxConfidence(
        scenario.target_confidence
      )}`,
    ],
    [
      "Readiness/action",
      `${scenario.readiness_ready === true ? "ready" : "blocked or unknown"}; action ${
        scenario.action_type || "unknown"
      }`,
    ],
    ["Sandbox scope", formatPhase9Scope(scenario.sandbox_scope)],
    ["Notes", formatEvaluationNotes(scenario.notes)],
  ];
}

function phase9ExperimentBadges(scenario) {
  return [
    ["gate", scenario.gate_passed === true ? "passed" : "blocked", scenario.gate_passed ? "ok" : "risk"],
    ["dry_run", formatSandboxBool(scenario.dry_run), scenario.dry_run === true ? "ok" : "neutral"],
    [
      "skipped",
      formatSandboxBool(scenario.real_action_skipped),
      scenario.real_action_skipped === true ? "warn" : "neutral",
    ],
    [
      "approval",
      formatSandboxBool(scenario.user_approval_present),
      scenario.user_approval_present === true ? "ok" : "risk",
    ],
    [
      "emergency_stop",
      formatSandboxBool(scenario.emergency_stop_available),
      scenario.emergency_stop_available === true ? "ok" : "risk",
    ],
    [
      "rollback",
      formatSandboxBool(scenario.rollback_plan_recorded),
      scenario.rollback_plan_recorded === true ? "ok" : "warn",
    ],
  ];
}

function phase9ExperimentCompactLine(scenario) {
  const line = document.createElement("p");

  line.className = "sandbox-evaluation-compact-line";
  line.textContent = [
    `failure_reason_codes ${formatSandboxCodeList(scenario.failure_reason_codes, 3)}`,
    `blocker_codes ${formatSandboxCodeList(scenario.blocker_codes, 3)}`,
    `mock approval ${formatSandboxBool(scenario.user_approval_present)}`,
    `emergency stop ${formatSandboxBool(scenario.emergency_stop_available)}`,
    `rollback ${formatSandboxBool(scenario.rollback_plan_recorded)}`,
    `scope ${formatPhase9Scope(scenario.sandbox_scope)}`,
  ].join("; ");
  return line;
}

function phase9ExperimentAuditTimeline(scenario) {
  const container = document.createElement("div");
  const title = document.createElement("p");

  container.className = "sandbox-evaluation-audit";
  title.className = "sandbox-evaluation-audit-title";
  title.textContent = "Phase 9 audit event sequence";
  container.append(title, phase9AuditEventDrilldownList(scenario.audit_event_names, scenario));
  return container;
}

function phase9AuditEventDrilldownList(auditEventNames, scenario) {
  const list = document.createElement("ol");
  const auditEvents = sandboxCodes(auditEventNames);

  list.className = "sandbox-evaluation-audit-list";
  list.dataset.phase9AuditList = "true";

  if (!auditEvents.length) {
    const item = document.createElement("li");
    item.textContent = "none";
    list.appendChild(item);
    return list;
  }

  auditEvents.forEach((eventName, index) => {
    const item = document.createElement("li");
    const record = phase9TimelineEventRecord(scenario, eventName, index, index + 1);

    item.dataset.auditEventName = eventName;
    item.dataset.auditOrder = String(record.auditOrder);
    item.dataset.auditTone = sandboxAuditEventTone(eventName);
    item.dataset.originalOrder = String(record.originalOrder);
    item.dataset.scenarioAuditOrder = String(record.auditOrder);
    item.dataset.gateStatus = record.gateStatus;
    item.dataset.blockerSeverity = record.blockerSeverity;
    item.dataset.phase9EventKind = record.eventKind;
    item.appendChild(phase9AuditEventDrilldownDetails(eventName, index, scenario, record));
    list.appendChild(item);
  });

  return list;
}

function phase9AuditEventDrilldownDetails(eventName, index, scenario, record = null) {
  const eventRecord = record || phase9TimelineEventRecord(scenario, eventName, index, index + 1);
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  const step = document.createElement("span");
  const event = document.createElement("span");
  const body = document.createElement("dl");

  details.className = "phase9-audit-event-details";
  details.dataset.phase9AuditEventDetails = "true";
  details.dataset.testHook = "phase9-audit-event-details";
  details.dataset.auditEventName = eventRecord.eventName;
  details.dataset.auditOrder = String(eventRecord.auditOrder);
  details.dataset.originalOrder = String(eventRecord.originalOrder);
  details.dataset.scenarioAuditOrder = String(eventRecord.auditOrder);
  details.dataset.gateStatus = eventRecord.gateStatus;
  details.dataset.blockerSeverity = eventRecord.blockerSeverity;
  details.dataset.phase9EventKind = eventRecord.eventKind;
  summary.className = "phase9-audit-event-summary";
  step.className = "sandbox-evaluation-audit-step";
  step.textContent = String(eventRecord.auditOrder);
  event.className = "sandbox-evaluation-event-chip";
  event.dataset.tone = sandboxAuditEventTone(eventRecord.eventName);
  event.dataset.phase9AuditEventChip = "true";
  event.dataset.phase9EventKind = eventRecord.eventKind;
  event.dataset.testHook = "phase9-audit-event-chip";
  event.title = eventRecord.eventName;
  event.textContent = sandboxAuditEventLabel(eventRecord.eventName);
  body.className = "phase9-audit-event-detail-grid";
  for (const [label, value] of phase9AuditEventDetailRows(eventRecord)) {
    body.appendChild(plannerEvaluationFact(label, value));
  }
  summary.append(step, event);
  details.append(summary, body);
  return details;
}

function phase9AuditEventDetailRows(record) {
  const scenario = record.scenario || {};

  return [
    ["Event", record.eventName || "unknown"],
    ["Scenario ID", record.scenarioId || "unknown"],
    ["Original order", String(record.originalOrder)],
    ["Scenario order", String(record.auditOrder)],
    ["Gate status", record.gateStatus],
    ["Blocker severity", record.blockerSeverity],
    ["Failure reasons", formatSandboxCodeList(scenario.failure_reason_codes)],
    ["Blockers", formatSandboxCodeList(scenario.blocker_codes)],
    [
      "Approval state",
      `mock checked ${formatSandboxBool(scenario.mock_approval_checked)}; present ${formatSandboxBool(
        scenario.user_approval_present
      )}`,
    ],
    [
      "Emergency stop",
      `available ${formatSandboxBool(scenario.emergency_stop_available)}; active ${formatSandboxBool(
        scenario.emergency_stop_active
      )}`,
    ],
    [
      "Verification",
      scenario.post_action_verification_planned === true ? "post-action plan recorded" : "not planned",
    ],
    ["Rollback", scenario.rollback_plan_recorded === true ? "mock rollback recorded" : "not recorded"],
    ["Dry-run", formatSandboxBool(scenario.dry_run)],
    ["Real-action skipped", formatSandboxBool(scenario.real_action_skipped)],
  ];
}

function renderPhase9ExperimentTimeline(scenarios, filters = {}) {
  phase9ExperimentTimeline.replaceChildren();

  const title = document.createElement("p");
  const records = phase9SortedTimelineEvents(
    phase9TimelineEventRecords(scenarios),
    filters.auditSortMode || "original"
  );
  const groups = phase9TimelineEventGroups(records, filters.auditGroupMode || "scenario");

  title.className = "sandbox-evaluation-timeline-title";
  title.textContent = `Phase 9 audit sequence across harness scenarios - ${phase9TimelineSortLabel(
    filters.auditSortMode || "original"
  )}`;
  phase9ExperimentTimeline.dataset.phase9AuditGroupMode = filters.auditGroupMode || "scenario";
  phase9ExperimentTimeline.dataset.phase9AuditSortMode = filters.auditSortMode || "original";

  phase9ExperimentTimeline.appendChild(title);

  if (!groups.length) {
    const list = document.createElement("ol");
    const item = document.createElement("li");

    list.className = "sandbox-evaluation-timeline-list";
    item.textContent = "No Phase 9 audit events returned.";
    list.appendChild(item);
    phase9ExperimentTimeline.appendChild(list);
    return;
  }

  for (const group of groups) {
    phase9ExperimentTimeline.appendChild(phase9TimelineEventGroupSection(group));
  }
}

function phase9TimelineEventRecords(scenarios) {
  const records = [];
  let originalOrder = 0;

  for (const scenario of Array.isArray(scenarios) ? scenarios : []) {
    sandboxCodes(scenario.audit_event_names).forEach((eventName, index) => {
      originalOrder += 1;
      records.push(phase9TimelineEventRecord(scenario, eventName, index, originalOrder));
    });
  }

  return records;
}

function phase9TimelineEventRecord(scenario, eventName, index, originalOrder) {
  const normalizedEventName = String(eventName || "");

  return {
    scenario,
    scenarioId: scenario?.scenario_id || "unknown",
    scenarioName: scenario?.scenario_name || "unknown",
    eventName: normalizedEventName,
    auditOrder: Number(index) + 1,
    originalOrder: Number(originalOrder) || Number(index) + 1,
    gateStatus: scenario?.gate_passed === true ? "passed" : "blocked",
    blockerSeverity: phase9ScenarioBlockerSeverity(scenario),
    eventKind: phase9AuditEventKind(normalizedEventName, scenario),
  };
}

function phase9SortedTimelineEvents(records, sortMode) {
  const sortedRecords = Array.isArray(records) ? records.slice() : [];

  if (sortMode === "scenario_original") {
    return sortedRecords.sort(
      (left, right) =>
        left.scenarioId.localeCompare(right.scenarioId) ||
        left.auditOrder - right.auditOrder ||
        left.originalOrder - right.originalOrder
    );
  }

  return sortedRecords.sort((left, right) => left.originalOrder - right.originalOrder);
}

function phase9TimelineEventGroups(records, groupMode) {
  const groups = new Map();

  for (const record of Array.isArray(records) ? records : []) {
    const key = phase9TimelineEventGroupKey(record, groupMode);

    if (!groups.has(key)) {
      groups.set(key, {
        key,
        title: phase9TimelineEventGroupTitle(record, groupMode),
        severity: record.blockerSeverity,
        records: [],
      });
    }

    groups.get(key).records.push(record);
  }

  return Array.from(groups.values());
}

function phase9TimelineEventGroupKey(record, groupMode) {
  if (groupMode === "gate") {
    return `gate:${record.gateStatus}`;
  }

  if (groupMode === "severity") {
    return `severity:${record.blockerSeverity}`;
  }

  if (groupMode === "event") {
    return `event:${record.eventName}`;
  }

  return `scenario:${record.scenarioId}`;
}

function phase9TimelineEventGroupTitle(record, groupMode) {
  if (groupMode === "gate") {
    return `Gate status: ${record.gateStatus}`;
  }

  if (groupMode === "severity") {
    return `Blocker severity: ${record.blockerSeverity}`;
  }

  if (groupMode === "event") {
    return `Event: ${sandboxAuditEventLabel(record.eventName)}`;
  }

  return `Scenario: ${record.scenarioId}`;
}

function phase9TimelineEventGroupSection(group) {
  const section = document.createElement("section");
  const title = document.createElement("p");

  section.className = "phase9-audit-timeline-group";
  section.dataset.phase9AuditGroup = group.key;
  section.dataset.blockerSeverity = group.severity || "normal";
  title.className = "phase9-audit-timeline-group-title";
  title.textContent = `${group.title} (${group.records.length})`;
  section.append(title, phase9TimelineEventList(group.records));
  return section;
}

function phase9TimelineEventList(records) {
  const list = document.createElement("ol");

  list.className = "sandbox-evaluation-timeline-list";
  list.dataset.phase9TimelineEventList = "true";

  for (const record of Array.isArray(records) ? records : []) {
    const item = document.createElement("li");
    const scenarioId = document.createElement("span");

    item.dataset.phase9TimelineEvent = "true";
    item.dataset.scenarioId = record.scenarioId;
    item.dataset.auditEventName = record.eventName;
    item.dataset.auditTone = sandboxAuditEventTone(record.eventName);
    item.dataset.auditOrder = String(record.auditOrder);
    item.dataset.originalOrder = String(record.originalOrder);
    item.dataset.scenarioAuditOrder = String(record.auditOrder);
    item.dataset.gateStatus = record.gateStatus;
    item.dataset.blockerSeverity = record.blockerSeverity;
    item.dataset.phase9EventKind = record.eventKind;
    scenarioId.className = "sandbox-evaluation-timeline-scenario";
    scenarioId.textContent = `${record.originalOrder}. ${record.scenarioId}`;
    item.append(
      scenarioId,
      phase9AuditEventDrilldownDetails(record.eventName, record.auditOrder - 1, record.scenario, record)
    );
    list.appendChild(item);
  }

  return list;
}

function phase9TimelineSortLabel(sortMode) {
  if (sortMode === "scenario_original") {
    return "scenario, then original order";
  }

  return "original order";
}

function phase9ExperimentTraceDetails(scenario) {
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  const pre = document.createElement("pre");

  details.className = "planner-evaluation-readiness-debug";
  summary.textContent = "Phase 9 trace debug JSON";
  pre.textContent = JSON.stringify(
    {
      experiment_id: scenario.experiment_id,
      scenario_id: scenario.scenario_id,
      actual_outcome: scenario.actual_outcome,
      sandbox_scope: scenario.sandbox_scope,
      trace: scenario.trace,
    },
    null,
    2
  );
  details.append(summary, pre);
  return details;
}

function formatPhase9Scope(scope) {
  if (!scope || typeof scope !== "object") {
    return "unknown";
  }

  const windowId = scope.window_id || "unknown window";
  const targetId = scope.target_id || "unknown target";
  const oneWindow = formatSandboxBool(scope.one_window_only);
  const oneTarget = formatSandboxBool(scope.one_target_only);
  return `${windowId} / ${targetId}; one_window ${oneWindow}; one_target ${oneTarget}`;
}

function setSandboxEvaluationSummary(rows) {
  sandboxEvaluationSummary.replaceChildren();

  for (const [label, value] of rows) {
    sandboxEvaluationSummary.appendChild(plannerEvaluationFact(label, value));
  }
}

function sandboxEvaluationScenarioGroups(scenarios, filters) {
  const groups = new Map();

  for (const scenario of scenarios) {
    const key = sandboxEvaluationScenarioGroupKey(scenario, filters);

    if (!groups.has(key)) {
      groups.set(key, {
        key,
        title: sandboxEvaluationScenarioGroupTitle(scenario, filters),
        scenarios: [],
      });
    }

    groups.get(key).scenarios.push(scenario);
  }

  return Array.from(groups.values());
}

function sandboxEvaluationScenarioGroupKey(scenario, filters) {
  if ((filters.scenarioType || "all") === "all") {
    return `type:${sandboxScenarioType(scenario)}`;
  }

  return `outcome:${sandboxEvaluationStatusKind(scenario)}`;
}

function sandboxEvaluationScenarioGroupTitle(scenario, filters) {
  if ((filters.scenarioType || "all") === "all") {
    return displaySandboxScenarioType(sandboxScenarioType(scenario));
  }

  return sandboxEvaluationStatusLabel(sandboxEvaluationStatusKind(scenario));
}

function sandboxEvaluationScenarioGroupSection(group) {
  const section = document.createElement("section");
  const title = document.createElement("p");

  section.className = "sandbox-evaluation-scenario-group";
  section.dataset.groupKey = group.key;
  title.className = "sandbox-evaluation-scenario-group-title";
  title.textContent = `${group.title} (${group.scenarios.length})`;
  section.appendChild(title);

  for (const scenario of group.scenarios) {
    section.appendChild(sandboxEvaluationScenarioCard(scenario));
  }

  return section;
}

function sandboxEvaluationScenarioCard(scenario) {
  const card = document.createElement("article");
  const header = document.createElement("div");
  const titleBlock = document.createElement("div");
  const title = document.createElement("p");
  const subtitle = document.createElement("p");
  const badges = document.createElement("div");
  const details = document.createElement("details");
  const detailsSummary = document.createElement("summary");
  const facts = document.createElement("dl");
  const passed = scenario.passed === true;
  const failureReasons = Array.isArray(scenario.failure_reason_codes)
    ? scenario.failure_reason_codes
    : [];
  const targetRisk = scenario.target_risk_hint || "none";
  const scenarioType = sandboxScenarioType(scenario);
  const actualStatus = scenario.actual_outcome?.status || "unknown";

  card.className = "planner-evaluation-card";
  card.dataset.sandboxTraceCard = "true";
  card.dataset.scenarioId = scenario.scenario_id || "";
  card.dataset.scenarioName = scenario.scenario_name || "";
  card.dataset.passFail = passed ? "pass" : "fail";
  card.dataset.expectedOutcome = scenario.expected_outcome?.status || "";
  card.dataset.actualOutcome = actualStatus;
  card.dataset.failureReasonCodes = failureReasons.join(",");
  card.dataset.blockerCodes = sandboxCodes(scenario.blocker_codes).join(",");
  card.dataset.auditEventNames = sandboxCodes(scenario.audit_event_names).join(",");
  card.dataset.dryRun = String(scenario.dry_run === true);
  card.dataset.realActionSkipped = String(scenario.real_action_skipped === true);
  card.dataset.postActionVerificationPlanned = String(
    scenario.post_action_verification_planned === true
  );
  card.dataset.targetRiskHint = targetRisk;
  card.dataset.targetConfidence = Number.isFinite(scenario.target_confidence)
    ? scenario.target_confidence.toFixed(2)
    : "";
  card.dataset.readinessReady = String(scenario.readiness_ready === true);
  card.dataset.actionType = scenario.action_type || "";
  card.dataset.scenarioType = scenarioType;
  card.dataset.status = sandboxEvaluationStatusKind(scenario);
  card.dataset.different = String(!passed || failureReasons.length > 0 || scenario.real_action_skipped === true);
  card.dataset.risk = String(targetRisk === "high_risk" || targetRisk === "unknown");
  header.className = "sandbox-evaluation-card-header";
  titleBlock.className = "sandbox-evaluation-card-title-block";
  title.className = "planner-evaluation-card-title";
  title.textContent = scenario.scenario_name || scenario.scenario_id || "unknown scenario";
  subtitle.className = "sandbox-evaluation-card-subtitle";
  subtitle.textContent = `${scenario.scenario_id || "unknown"} / expected ${
    scenario.expected_outcome?.status || "unknown"
  } / actual ${actualStatus}`;
  badges.className = "sandbox-evaluation-badges";
  badges.appendChild(sandboxEvaluationPrimaryStatusChip(scenario));
  for (const [label, value, tone] of sandboxEvaluationBadges(scenario, scenarioType)) {
    badges.appendChild(sandboxEvaluationBadge(label, value, tone));
  }
  titleBlock.append(title, subtitle);
  header.append(titleBlock, badges);
  details.className = "sandbox-evaluation-scenario-details";
  details.dataset.sandboxScenarioDetails = "true";
  detailsSummary.textContent = "Scenario fields";
  facts.className = "planner-evaluation-facts";

  for (const [label, value] of sandboxEvaluationRows(scenario)) {
    facts.appendChild(plannerEvaluationFact(label, value));
  }

  details.append(
    detailsSummary,
    facts,
    sandboxEvaluationBlockerDetails(scenario),
    sandboxEvaluationAuditTimeline(scenario)
  );

  if (scenario.trace) {
    details.appendChild(sandboxEvaluationTraceDetails(scenario));
  }

  card.append(header, sandboxEvaluationCompactLine(scenario), details);
  return card;
}

function sandboxEvaluationRows(scenario) {
  return [
    ["Scenario ID", scenario.scenario_id || "unknown"],
    ["Scenario type", displaySandboxScenarioType(sandboxScenarioType(scenario))],
    ["Pass/fail", scenario.passed === true ? "pass" : "fail"],
    ["Expected", formatSandboxOutcome(scenario.expected_outcome)],
    ["Actual", formatSandboxOutcome(scenario.actual_outcome)],
    ["Gate", scenario.gate_passed === true ? "passed" : "blocked"],
    ["Failure reasons", formatSandboxCodeList(scenario.failure_reason_codes)],
    ["Blockers", formatSandboxCodeList(scenario.blocker_codes)],
    ["Audit events", formatSandboxCodeList(scenario.audit_event_names)],
    ["Dry-run", formatSandboxBool(scenario.dry_run)],
    [
      "Real action",
      `enabled ${formatSandboxBool(scenario.real_action_enabled)}; skipped ${formatSandboxBool(
        scenario.real_action_skipped
      )}; attempted ${formatSandboxBool(scenario.actual_outcome?.real_action_attempted)}`,
    ],
    [
      "Post verify",
      scenario.post_action_verification_planned === true ? "planned" : "not planned",
    ],
    [
      "Target",
      `risk ${scenario.target_risk_hint || "none"}; confidence ${formatSandboxConfidence(
        scenario.target_confidence
      )}`,
    ],
    [
      "Readiness",
      `${scenario.readiness_ready === true ? "ready" : "blocked or unknown"}; action ${
        scenario.action_type || "unknown"
      }`,
    ],
    ["Notes", formatEvaluationNotes(scenario.notes)],
  ];
}

function sandboxEvaluationBadges(scenario, scenarioType) {
  return [
    ["actual", scenario.actual_outcome?.status || "unknown", "neutral"],
    ["type", displaySandboxScenarioType(scenarioType), "neutral"],
    ["dry_run", formatSandboxBool(scenario.dry_run), scenario.dry_run === true ? "ok" : "neutral"],
    [
      "skipped",
      formatSandboxBool(scenario.real_action_skipped),
      scenario.real_action_skipped === true ? "warn" : "neutral",
    ],
    [
      "post_verify",
      scenario.post_action_verification_planned === true ? "planned" : "none",
      scenario.post_action_verification_planned === true ? "ok" : "warn",
    ],
  ];
}

function sandboxEvaluationPrimaryStatusChip(scenario) {
  const status = sandboxEvaluationStatusKind(scenario);
  const chip = document.createElement("span");

  chip.className = "sandbox-evaluation-status-chip";
  chip.dataset.status = status;
  chip.textContent = sandboxEvaluationStatusLabel(status);
  return chip;
}

function sandboxEvaluationStatusKind(scenario) {
  if (scenario.passed !== true) {
    return "fail";
  }

  if (scenario.real_action_skipped === true) {
    return "skipped";
  }

  if (scenario.actual_outcome?.status === "blocked" || scenario.gate_passed === false) {
    return "blocked";
  }

  return "pass";
}

function sandboxEvaluationStatusLabel(status) {
  const labels = {
    pass: "pass",
    fail: "fail",
    skipped: "skipped",
    blocked: "blocked",
  };

  return labels[status] || "unknown";
}

function sandboxEvaluationBadge(label, value, tone = "neutral") {
  const badge = document.createElement("span");
  badge.className = "sandbox-evaluation-badge";
  badge.dataset.tone = tone;
  badge.textContent = `${label}: ${value}`;
  return badge;
}

function sandboxEvaluationCompactLine(scenario) {
  const line = document.createElement("p");
  const blockerCodes = sandboxCodes(scenario.blocker_codes);

  line.className = "sandbox-evaluation-compact-line";
  line.textContent = [
    `failure_reason_codes ${formatSandboxCodeList(scenario.failure_reason_codes, 3)}`,
    `blocker_codes ${formatSandboxCodeList(blockerCodes, 3)}`,
    `risk ${scenario.target_risk_hint || "none"}/${formatSandboxConfidence(scenario.target_confidence)}`,
    `readiness ${scenario.readiness_ready === true ? "ready" : "blocked or unknown"}`,
    `action ${scenario.action_type || "unknown"}`,
  ].join("; ");
  return line;
}

function sandboxEvaluationBlockerDetails(scenario) {
  const container = document.createElement("div");
  const title = document.createElement("p");
  const list = document.createElement("ul");
  const blockerCodes = sandboxCodes(scenario.blocker_codes);

  container.className = "sandbox-evaluation-blocker-details";
  title.className = "sandbox-evaluation-blocker-title";
  title.textContent = "Blocker details";
  list.className = "sandbox-evaluation-blocker-list";

  if (!blockerCodes.length) {
    const item = document.createElement("li");
    item.className = "sandbox-evaluation-blocker-empty";
    item.textContent = "No blocker codes reported for this scenario.";
    list.appendChild(item);
  } else {
    for (const blockerCode of blockerCodes) {
      const item = document.createElement("li");
      const chip = document.createElement("span");
      const description = document.createElement("span");
      const severity = sandboxBlockerSeverity(blockerCode);

      item.className = "sandbox-evaluation-blocker-item";
      item.dataset.blockerCode = blockerCode;
      item.dataset.severity = severity;
      chip.className = "sandbox-evaluation-blocker-chip";
      chip.dataset.severity = severity;
      chip.title = sandboxBlockerDescription(blockerCode);
      chip.textContent = blockerCode;
      description.className = "sandbox-evaluation-blocker-description";
      description.textContent = sandboxBlockerDescription(blockerCode);
      item.append(chip, description);
      list.appendChild(item);
    }
  }

  container.append(title, list);
  return container;
}

function sandboxEvaluationTraceDetails(scenario) {
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  const pre = document.createElement("pre");

  details.className = "planner-evaluation-readiness-debug";
  summary.textContent = "trace debug JSON";
  pre.textContent = JSON.stringify(
    {
      scenario_id: scenario.scenario_id,
      trace: scenario.trace,
      actual_outcome: scenario.actual_outcome,
    },
    null,
    2
  );
  details.append(summary, pre);
  return details;
}

function sandboxAuditEventList(auditEventNames) {
  const list = document.createElement("ol");
  const auditEvents = sandboxCodes(auditEventNames);

  list.className = "sandbox-evaluation-audit-list";

  if (!auditEvents.length) {
    const item = document.createElement("li");
    item.textContent = "none";
    list.appendChild(item);
    return list;
  }

  auditEvents.forEach((eventName, index) => {
    const item = document.createElement("li");
    const step = document.createElement("span");
    const event = document.createElement("span");

    item.dataset.auditEventName = eventName;
    item.dataset.auditTone = sandboxAuditEventTone(eventName);
    step.className = "sandbox-evaluation-audit-step";
    step.textContent = String(index + 1);
    event.className = "sandbox-evaluation-event-chip";
    event.dataset.tone = sandboxAuditEventTone(eventName);
    event.title = eventName;
    event.textContent = sandboxAuditEventLabel(eventName);
    item.append(step, event);
    list.appendChild(item);
  });

  return list;
}

function sandboxEvaluationAuditTimeline(scenario) {
  const container = document.createElement("div");
  const title = document.createElement("p");
  const list = document.createElement("ol");
  const auditEvents = sandboxCodes(scenario.audit_event_names);

  container.className = "sandbox-evaluation-audit";
  title.className = "sandbox-evaluation-audit-title";
  title.textContent = "Audit event sequence";
  list.className = "sandbox-evaluation-audit-list";

  if (!auditEvents.length) {
    const item = document.createElement("li");
    item.textContent = "none";
    list.appendChild(item);
  } else {
    auditEvents.forEach((eventName, index) => {
      const item = document.createElement("li");
      const step = document.createElement("span");
      const event = document.createElement("span");

      item.dataset.auditEventName = eventName;
      item.dataset.auditTone = sandboxAuditEventTone(eventName);
      step.className = "sandbox-evaluation-audit-step";
      step.textContent = String(index + 1);
      event.className = "sandbox-evaluation-event-chip";
      event.dataset.tone = sandboxAuditEventTone(eventName);
      event.title = eventName;
      event.textContent = sandboxAuditEventLabel(eventName);
      item.append(step, event);
      list.appendChild(item);
    });
  }

  container.append(title, list);
  return container;
}

function renderSandboxEvaluationTimeline(scenarios) {
  sandboxEvaluationTimeline.replaceChildren();

  const title = document.createElement("p");
  const list = document.createElement("ol");
  const visibleScenarios = Array.isArray(scenarios) ? scenarios : [];

  title.className = "sandbox-evaluation-timeline-title";
  title.textContent = "Audit sequence across visible scenarios";
  list.className = "sandbox-evaluation-timeline-list";

  for (const scenario of visibleScenarios) {
    const auditEvents = sandboxCodes(scenario.audit_event_names);
    auditEvents.forEach((eventName, index) => {
      const item = document.createElement("li");
      const scenarioId = document.createElement("span");
      const step = document.createElement("span");
      const event = document.createElement("span");

      item.dataset.scenarioId = scenario.scenario_id || "";
      item.dataset.auditEventName = eventName;
      item.dataset.auditTone = sandboxAuditEventTone(eventName);
      scenarioId.className = "sandbox-evaluation-timeline-scenario";
      scenarioId.textContent = scenario.scenario_id || "unknown";
      step.className = "sandbox-evaluation-audit-step";
      step.textContent = String(index + 1);
      event.className = "sandbox-evaluation-event-chip";
      event.dataset.tone = sandboxAuditEventTone(eventName);
      event.title = eventName;
      event.textContent = sandboxAuditEventLabel(eventName);
      item.append(scenarioId, step, event);
      list.appendChild(item);
    });
  }

  if (!list.children.length) {
    const item = document.createElement("li");
    item.textContent = "No audit events match the active filters.";
    list.appendChild(item);
  }

  sandboxEvaluationTimeline.append(title, list);
}

function renderSandboxEvaluationCounts(summary, totalScenarioCount) {
  sandboxEvaluationCounts.replaceChildren();
  sandboxEvaluationCounts.hidden = false;

  for (const [label, value, tone] of [
    ["total", String(totalScenarioCount), "neutral"],
    ["visible", String(summary.total), "neutral"],
    ["passed", String(summary.passed), "ok"],
    ["failed", String(summary.failed), summary.failed > 0 ? "risk" : "neutral"],
    ["skipped", String(summary.skipped), summary.skipped > 0 ? "warn" : "neutral"],
    ["blocked", String(summary.blocked), summary.blocked > 0 ? "risk" : "neutral"],
  ]) {
    const chip = document.createElement("div");
    const countValue = document.createElement("span");
    const countLabel = document.createElement("span");

    chip.className = "sandbox-evaluation-count";
    chip.dataset.countKey = label;
    chip.dataset.tone = tone;
    countValue.className = "sandbox-evaluation-count-value";
    countValue.textContent = value;
    countLabel.className = "sandbox-evaluation-count-label";
    countLabel.textContent = label;
    chip.append(countValue, countLabel);
    sandboxEvaluationCounts.appendChild(chip);
  }
}

function renderSandboxEvaluationSummaryVisualization(summary) {
  sandboxEvaluationSummaryViz.replaceChildren();
  sandboxEvaluationSummaryViz.hidden = false;

  const rows = [
    ["passed", summary.passed, "ok"],
    ["failed", summary.failed, "risk"],
    ["skipped", summary.skipped, "warn"],
    ["blocked", summary.blocked, "risk"],
  ];

  for (const [label, value, tone] of rows) {
    const row = document.createElement("div");
    const labelNode = document.createElement("span");
    const bar = document.createElement("span");
    const valueNode = document.createElement("span");

    row.className = "sandbox-evaluation-bar-row";
    row.dataset.barKey = label;
    row.dataset.tone = tone;
    labelNode.className = "sandbox-evaluation-bar-label";
    labelNode.textContent = label;
    bar.className = "sandbox-evaluation-text-bar";
    bar.textContent = sandboxTextBar(value, summary.total);
    valueNode.className = "sandbox-evaluation-bar-value";
    valueNode.textContent = String(value);
    row.append(labelNode, bar, valueNode);
    sandboxEvaluationSummaryViz.appendChild(row);
  }
}

function sandboxTextBar(value, total) {
  const safeValue = Number.isFinite(value) ? Math.max(0, value) : 0;
  const safeTotal = Number.isFinite(total) ? Math.max(0, total) : 0;
  const width = 10;

  if (safeTotal <= 0) {
    return "----------";
  }

  const filled = Math.max(0, Math.min(width, Math.round((safeValue / safeTotal) * width)));
  return `${"#".repeat(filled)}${"-".repeat(width - filled)}`;
}

function renderSandboxQuickFilters(filters) {
  sandboxEvaluationQuickFilters.replaceChildren();

  for (const [groupKey, group] of Object.entries(SANDBOX_QUICK_FILTER_GROUPS)) {
    const button = document.createElement("button");

    button.type = "button";
    button.className = "sandbox-evaluation-quick-filter";
    button.dataset.filterGroup = groupKey;
    button.title = group.description;
    button.setAttribute("aria-pressed", String(filters.quickGroup === groupKey));
    button.textContent = group.label;
    button.addEventListener("click", () => {
      currentSandboxQuickFilterGroup =
        currentSandboxQuickFilterGroup === groupKey ? "all" : groupKey;
      renderSandboxEvaluation(currentSandboxEvaluationReport);
    });
    sandboxEvaluationQuickFilters.appendChild(button);
  }
}

function resetSandboxEvaluationFilters() {
  sandboxEvaluationFixtureSet.value = "all";
  sandboxEvaluationResultFilter.value = "all";
  sandboxEvaluationTypeFilter.value = "all";
  sandboxEvaluationBlockerFilter.value = "all";
  currentSandboxQuickFilterGroup = "all";
  sandboxEvaluationCopyStatus.hidden = true;
  renderSandboxEvaluation(currentSandboxEvaluationReport);
}

async function copySandboxEvaluationSummary() {
  const payload = buildSandboxVisibleSummaryPayload();

  sandboxEvaluationCopyStatus.hidden = false;

  if (!payload) {
    sandboxEvaluationCopyStatus.textContent = "No sandbox trace loaded.";
    return;
  }

  if (!navigator.clipboard?.writeText) {
    sandboxEvaluationCopyStatus.textContent = "Clipboard unavailable in this browser.";
    return;
  }

  try {
    await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
    sandboxEvaluationCopyStatus.textContent = "Visible sandbox summary copied.";
  } catch (error) {
    sandboxEvaluationCopyStatus.textContent = `Copy failed: ${error.message || String(error)}`;
  }
}

function buildSandboxVisibleSummaryPayload() {
  const report = currentSandboxEvaluationReport;

  if (!report) {
    return null;
  }

  const scenarios = Array.isArray(report.scenarios) ? report.scenarios : [];
  const filters = currentSandboxEvaluationFilters();
  const visibleScenarios = sandboxEvaluationFilteredScenarios(scenarios, filters);

  return {
    report_type: report.report_type,
    phase: report.phase,
    source: report.source,
    filters,
    counts: summarizeSandboxScenarios(visibleScenarios),
    scenario_ids: visibleScenarios.map((scenario) => scenario.scenario_id),
    scenarios: visibleScenarios.map((scenario) => ({
      scenario_id: scenario.scenario_id,
      scenario_name: scenario.scenario_name,
      expected_outcome: scenario.expected_outcome,
      actual_outcome: scenario.actual_outcome,
      passed: scenario.passed,
      gate_passed: scenario.gate_passed,
      failure_reason_codes: sandboxCodes(scenario.failure_reason_codes),
      blocker_codes: sandboxCodes(scenario.blocker_codes),
      audit_event_names: sandboxCodes(scenario.audit_event_names),
      dry_run: scenario.dry_run,
      real_action_skipped: scenario.real_action_skipped,
      post_action_verification_planned: scenario.post_action_verification_planned,
      target_risk_hint: scenario.target_risk_hint,
      target_confidence: scenario.target_confidence,
      readiness_ready: scenario.readiness_ready,
      action_type: scenario.action_type,
    })),
  };
}

function currentSandboxEvaluationFilters() {
  return {
    fixtureSet: sandboxEvaluationFixtureSet.value || "all",
    passFail: sandboxEvaluationResultFilter.value || "all",
    scenarioType: sandboxEvaluationTypeFilter.value || "all",
    blocker: sandboxEvaluationBlockerFilter.value || "all",
    quickGroup: currentSandboxQuickFilterGroup || "all",
  };
}

function populateSandboxEvaluationFilters(report, activeFilters) {
  const scenarios = Array.isArray(report?.scenarios) ? report.scenarios : [];
  const scenarioTypes = uniqueSortedValues(scenarios.map((scenario) => sandboxScenarioType(scenario)));
  const blockers = uniqueSortedValues(scenarios.flatMap((scenario) => sandboxCodes(scenario.blocker_codes)));

  setSelectOptions(
    sandboxEvaluationTypeFilter,
    [["all", "all scenario types"]].concat(
      scenarioTypes.map((scenarioType) => [scenarioType, displaySandboxScenarioType(scenarioType)])
    ),
    activeFilters.scenarioType
  );
  setSelectOptions(
    sandboxEvaluationBlockerFilter,
    [["all", "all blockers"]].concat(blockers.map((blocker) => [blocker, blocker])),
    activeFilters.blocker
  );
  sandboxEvaluationFixtureSet.value = sandboxFixtureSetExists(activeFilters.fixtureSet)
    ? activeFilters.fixtureSet
    : "all";
  sandboxEvaluationResultFilter.value = ["all", "pass", "fail"].includes(activeFilters.passFail)
    ? activeFilters.passFail
    : "all";
}

function setSelectOptions(selectElement, options, selectedValue) {
  const safeSelectedValue = options.some(([value]) => value === selectedValue) ? selectedValue : "all";

  selectElement.replaceChildren();
  for (const [value, label] of options) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    option.selected = value === safeSelectedValue;
    selectElement.appendChild(option);
  }
}

function sandboxEvaluationFilteredScenarios(scenarios, filters) {
  return (Array.isArray(scenarios) ? scenarios : []).filter((scenario) =>
    sandboxScenarioMatchesFilters(scenario, filters)
  );
}

function sandboxScenarioMatchesFilters(scenario, filters = {}) {
  const passFail = scenario.passed === true ? "pass" : "fail";
  const scenarioType = sandboxScenarioType(scenario);
  const blockerCodes = sandboxCodes(scenario.blocker_codes);
  const fixtureSet = filters.fixtureSet || "all";

  if ((filters.passFail || "all") !== "all" && filters.passFail !== passFail) {
    return false;
  }

  if ((filters.scenarioType || "all") !== "all" && filters.scenarioType !== scenarioType) {
    return false;
  }

  if ((filters.blocker || "all") !== "all" && !blockerCodes.includes(filters.blocker)) {
    return false;
  }

  if (!sandboxScenarioMatchesFixtureSet(scenario, fixtureSet)) {
    return false;
  }

  return sandboxScenarioMatchesQuickGroup(scenario, filters.quickGroup || "all");
}

function sandboxScenarioMatchesFixtureSet(scenario, fixtureSet) {
  if (!sandboxFixtureSetExists(fixtureSet) || fixtureSet === "all") {
    return true;
  }

  if (fixtureSet === "gate_passed") {
    return scenario.gate_passed === true;
  }

  if (fixtureSet === "blocked") {
    return scenario.gate_passed === false;
  }

  if (fixtureSet === "skipped") {
    return scenario.real_action_skipped === true;
  }

  if (fixtureSet === "risk_confidence") {
    return ["risk_confidence", "high_risk", "low_confidence"].includes(sandboxScenarioType(scenario));
  }

  if (fixtureSet === "geometry") {
    return sandboxScenarioType(scenario) === "geometry";
  }

  return true;
}

function sandboxFixtureSetExists(fixtureSet) {
  return ["all", "gate_passed", "blocked", "skipped", "risk_confidence", "geometry"].includes(
    fixtureSet
  );
}

function sandboxScenarioMatchesQuickGroup(scenario, quickGroup) {
  if (!quickGroup || quickGroup === "all") {
    return true;
  }

  const scenarioType = sandboxScenarioType(scenario);
  const blockerCodes = sandboxCodes(scenario.blocker_codes);
  const failureReasons = sandboxCodes(scenario.failure_reason_codes);

  if (quickGroup === "geometry") {
    return (
      scenarioType === "geometry" ||
      blockerCodes.some((code) =>
        [
          "invalid_bbox",
          "bbox_center_mismatch",
          "coordinate_space_unknown",
          "dpi_uncertain",
          "stale_observation",
          "missing_target",
        ].includes(code)
      )
    );
  }

  if (quickGroup === "readiness") {
    return scenarioType === "readiness_blocker" || blockerCodes.includes("preview_only_contract");
  }

  if (quickGroup === "approval") {
    return (
      blockerCodes.includes("high_risk_requires_approval") ||
      blockerCodes.includes("unknown_risk_target") ||
      failureReasons.includes("high_risk_target")
    );
  }

  if (quickGroup === "risk") {
    return (
      scenarioType === "risk_confidence" ||
      failureReasons.includes("high_risk_target") ||
      failureReasons.includes("low_confidence_target") ||
      scenario.target_risk_hint === "high_risk" ||
      scenario.target_risk_hint === "unknown"
    );
  }

  if (quickGroup === "scope") {
    return (
      scenarioType === "sandbox_scope" ||
      failureReasons.includes("forbidden_action_type") ||
      failureReasons.includes("outside_sandbox_scope")
    );
  }

  if (quickGroup === "audit") {
    return failureReasons.includes("missing_audit_plan");
  }

  return true;
}

function summarizeSandboxScenarios(scenarios) {
  const safeScenarios = Array.isArray(scenarios) ? scenarios : [];

  return {
    total: safeScenarios.length,
    passed: safeScenarios.filter((scenario) => scenario.passed === true).length,
    failed: safeScenarios.filter((scenario) => scenario.passed !== true).length,
    skipped: safeScenarios.filter((scenario) => scenario.real_action_skipped === true).length,
    blocked: safeScenarios.filter(
      (scenario) => scenario.actual_outcome?.status === "blocked" || scenario.gate_passed === false
    ).length,
  };
}

function sandboxScenarioType(scenario) {
  const status = scenario.actual_outcome?.status || "unknown";
  const failureReasons = sandboxCodes(scenario.failure_reason_codes);
  const blockerCodes = sandboxCodes(scenario.blocker_codes);

  if (status === "dry_run_completed") {
    return "dry_run_success";
  }

  if (scenario.real_action_skipped === true || failureReasons.includes("real_action_disabled")) {
    return "real_action_skipped";
  }

  if (
    failureReasons.includes("high_risk_target") ||
    failureReasons.includes("low_confidence_target") ||
    scenario.target_risk_hint === "high_risk" ||
    scenario.target_risk_hint === "unknown"
  ) {
    return "risk_confidence";
  }

  if (
    failureReasons.includes("invalid_target_geometry") ||
    failureReasons.includes("stale_observation") ||
    failureReasons.includes("missing_target") ||
    blockerCodes.some((code) =>
      ["invalid_bbox", "bbox_center_mismatch", "coordinate_space_unknown", "dpi_uncertain"].includes(code)
    )
  ) {
    return "geometry";
  }

  if (failureReasons.includes("readiness_not_ready")) {
    return "readiness_blocker";
  }

  if (
    failureReasons.includes("forbidden_action_type") ||
    failureReasons.includes("outside_sandbox_scope")
  ) {
    return "sandbox_scope";
  }

  if (status === "blocked") {
    return "phase7_gate";
  }

  return "other";
}

function displaySandboxScenarioType(scenarioType) {
  const labels = {
    dry_run_success: "dry-run success",
    real_action_skipped: "real-action skipped",
    risk_confidence: "risk/confidence",
    geometry: "geometry/freshness",
    readiness_blocker: "readiness blocker",
    sandbox_scope: "sandbox scope",
    phase7_gate: "Phase 7 gate",
    other: "other",
  };

  return labels[scenarioType] || scenarioType || "unknown";
}

function setSandboxScenarioDetailsOpen(open) {
  const detailsNodes = sandboxEvaluationResults.querySelectorAll(
    "details[data-sandbox-scenario-details='true']"
  );
  detailsNodes.forEach((details) => {
    details.open = open;
  });
}

function uniqueSortedValues(values) {
  return Array.from(new Set(values.filter((value) => value))).sort();
}

function sandboxCodes(values) {
  return Array.isArray(values) ? values.map((value) => String(value)) : [];
}

function sandboxBlockerDescription(blockerCode) {
  return SANDBOX_BLOCKER_DESCRIPTIONS[blockerCode] || "Conservative sandbox blocker.";
}

function sandboxBlockerSeverity(blockerCode) {
  return SANDBOX_BLOCKER_SEVERITY[blockerCode] || "medium";
}

function phase9BlockerSeverity(blockerCode) {
  return PHASE9_BLOCKER_SEVERITY[blockerCode] || sandboxBlockerSeverity(blockerCode);
}

function phase9ScenarioBlockerSeverity(scenario) {
  const severities = phase9GateBlockerCodes(scenario).map((code) => phase9BlockerSeverity(code));

  if (severities.includes("critical")) {
    return "critical";
  }

  if (severities.includes("high")) {
    return "high";
  }

  if (severities.includes("medium")) {
    return "medium";
  }

  return "normal";
}

function phase9AuditEventKind(eventName, scenario = {}) {
  if (eventName === "phase9_gate_blocked") {
    return "blocked";
  }

  if (eventName === "phase9_real_action_skipped") {
    return "skipped";
  }

  if (
    eventName === "phase9_mock_approval_checked" &&
    scenario?.user_approval_present !== true
  ) {
    return "warning";
  }

  if (
    eventName === "phase9_emergency_stop_checked" &&
    (scenario?.emergency_stop_available !== true || scenario?.emergency_stop_active === true)
  ) {
    return "warning";
  }

  if (
    eventName === "phase9_gate_passed" ||
    eventName === "phase9_dry_run_completed" ||
    eventName === "phase9_post_action_verification_planned" ||
    eventName === "phase9_rollback_plan_recorded"
  ) {
    return "success";
  }

  return "normal";
}

function sandboxAuditEventLabel(eventName) {
  return SANDBOX_AUDIT_EVENT_LABELS[eventName] || eventName || "audit event";
}

function sandboxAuditEventTone(eventName) {
  if (eventName === "sandbox_gate_blocked" || eventName === "phase9_gate_blocked") {
    return "risk";
  }

  if (eventName === "sandbox_real_action_skipped" || eventName === "phase9_real_action_skipped") {
    return "warn";
  }

  if (
    eventName === "sandbox_gate_passed" ||
    eventName === "sandbox_dry_run_completed" ||
    eventName === "sandbox_post_action_verification_planned" ||
    eventName === "phase9_gate_passed" ||
    eventName === "phase9_dry_run_completed" ||
    eventName === "phase9_mock_approval_checked" ||
    eventName === "phase9_emergency_stop_checked" ||
    eventName === "phase9_post_action_verification_planned" ||
    eventName === "phase9_rollback_plan_recorded"
  ) {
    return "ok";
  }

  return "neutral";
}

function sandboxEvaluationEmptyState(message, filters) {
  const container = document.createElement("div");
  const title = document.createElement("p");
  const detail = document.createElement("p");

  container.className = "sandbox-evaluation-empty-state";
  title.className = "sandbox-evaluation-empty-title";
  title.textContent = message;
  detail.className = "sandbox-evaluation-empty-detail";
  detail.textContent = `Active filters: ${sandboxActiveFilterDescription(filters)}.`;
  container.append(title, detail);
  return container;
}

function sandboxActiveFilterDescription(filters = {}) {
  return [
    `fixture ${filters.fixtureSet || "all"}`,
    `result ${filters.passFail || "all"}`,
    `type ${filters.scenarioType || "all"}`,
    `blocker ${filters.blocker || "all"}`,
    `quick group ${filters.quickGroup || "all"}`,
  ].join("; ");
}

function formatSandboxOutcome(outcome = {}) {
  if (!outcome || typeof outcome !== "object") {
    return "unknown";
  }

  const status = outcome.status || "unknown";
  const gate =
    outcome.gate_passed === true ? "gate passed" : outcome.gate_passed === false ? "gate blocked" : "gate unknown";
  const skipped = formatSandboxBool(outcome.real_action_skipped);
  const attempted = formatSandboxBool(outcome.real_action_attempted);
  const reasons = formatSandboxCodeList(outcome.failure_reason_codes, 4);

  return `${status}; ${gate}; skipped ${skipped}; attempted ${attempted}; reasons ${reasons}`;
}

function formatSandboxCodeList(values, limit = 8) {
  if (!Array.isArray(values) || !values.length) {
    return "none";
  }

  const visibleValues = values.slice(0, limit).map((value) => compactText(String(value), 42));
  const extraCount = values.length - visibleValues.length;
  return extraCount > 0 ? `${visibleValues.join(", ")} +${extraCount} more` : visibleValues.join(", ");
}

function formatSandboxCodeMap(valueMap) {
  if (!valueMap || typeof valueMap !== "object") {
    return "none";
  }

  const entries = Object.entries(valueMap).filter(
    ([, scenarioIds]) => Array.isArray(scenarioIds) && scenarioIds.length
  );

  if (!entries.length) {
    return "none";
  }

  return entries
    .slice(0, 8)
    .map(([code, scenarioIds]) => `${compactText(code, 32)} (${scenarioIds.length})`)
    .join(", ");
}

function formatSandboxBool(value) {
  if (value === true) {
    return "yes";
  }

  if (value === false) {
    return "no";
  }

  return "unknown";
}

function formatSandboxConfidence(value) {
  return Number.isFinite(value) ? value.toFixed(2) : "unknown";
}

function setPlannerEvaluationSummary(rows) {
  plannerEvaluationSummary.replaceChildren();

  for (const [label, value] of rows) {
    plannerEvaluationSummary.appendChild(plannerEvaluationFact(label, value));
  }
}

function plannerEvaluationScenarioCard(scenario) {
  const card = document.createElement("article");
  const title = document.createElement("p");
  const facts = document.createElement("dl");
  const differences = scenario.differences ?? {};
  const hasRiskHint = hasEvaluationRiskHint(scenario);

  card.className = "planner-evaluation-card";
  card.dataset.different = String(
    differences.same_proposal_type === false || differences.same_target === false
  );
  card.dataset.risk = String(hasRiskHint);
  title.className = "planner-evaluation-card-title";
  title.textContent = hasRiskHint
    ? `${scenario.scenario || "unknown scenario"} - high-risk grounding hint`
    : scenario.scenario || "unknown scenario";
  facts.className = "planner-evaluation-facts";

  for (const [label, value] of plannerEvaluationRows(scenario)) {
    facts.appendChild(plannerEvaluationFact(label, value));
  }

  card.append(title, facts);
  const diagnostics = plannerEvaluationReadinessDiagnostics(scenario);
  if (diagnostics) {
    card.appendChild(diagnostics);
  }
  return card;
}

function plannerEvaluationRows(scenario) {
  const inputs = scenario.inputs ?? {};
  const observation = scenario.observation ?? {};
  const visibleElements = inputs.visible_elements ?? {};
  const elementCount = Number.isFinite(observation.element_count)
    ? String(observation.element_count)
    : compactCountWithTruncation(visibleElements);

  return [
    ["Task", observation.task || inputs.task || "none"],
    ["Elements", elementCount],
    ["Expected", formatEvaluationExpected(scenario)],
    ["Pass/fail", formatEvaluationExpectation(scenario)],
    ["Risk hints", formatEvaluationRiskHints(scenario)],
    ["Risk label", formatEvaluationRiskLabel(scenario)],
    ["Agreement", formatEvaluationAgreement(scenario)],
    ["Rule-based", formatEvaluationProposal(scenario.rule_based)],
    ["AI proposal", formatEvaluationProposal(scenario.ai_proposal)],
    ["Safety", formatEvaluationPair(scenario, formatEvaluationSafety)],
    ["Contract", formatEvaluationPair(scenario, formatEvaluationContract)],
    ["Readiness", formatEvaluationPair(scenario, formatEvaluationReadiness)],
    ["Blocker", formatEvaluationBlocker(scenario)],
    ["Differences", formatEvaluationNotes(scenario.differences?.notes)],
    ["Strategy notes", formatEvaluationNotes(observation.strategy_notes ?? scenario.notes)],
  ];
}

function plannerEvaluationFact(label, value) {
  const row = document.createElement("div");
  const term = document.createElement("dt");
  const detail = document.createElement("dd");

  term.textContent = label;
  detail.textContent = value;
  row.append(term, detail);
  return row;
}

function plannerEvaluationReadinessDiagnostics(scenario) {
  const groups = [
    ["rule-based", scenario.rule_based?.click_readiness],
    ["ai_proposal", scenario.ai_proposal?.click_readiness],
  ].filter(([, clickReadiness]) => Array.isArray(clickReadiness?.checks) && clickReadiness.checks.length);

  if (!groups.length) {
    return null;
  }

  const container = document.createElement("div");
  const title = document.createElement("p");

  container.className = "planner-evaluation-readiness-diagnostics";
  title.className = "planner-evaluation-readiness-title";
  title.textContent = "Readiness diagnostics";
  container.appendChild(title);

  for (const [plannerName, clickReadiness] of groups) {
    const group = document.createElement("div");
    const details = document.createElement("details");
    const summary = document.createElement("summary");
    const pre = document.createElement("pre");
    const resultKey = plannerName === "rule-based" ? "rule_based" : plannerName;
    const result = scenario[resultKey] ?? {};

    group.className = "planner-evaluation-readiness-group";
    renderReadinessChecks(group, clickReadiness, `${plannerName} checks`);
    details.className = "planner-evaluation-readiness-debug";
    summary.textContent = `${plannerName} debug JSON`;
    pre.textContent = JSON.stringify(
      buildReadinessDebugSummary({
        planner: plannerName,
        proposal: result.proposal ?? null,
        actionContract: result.action_contract ?? null,
        clickReadiness,
      }),
      null,
      2
    );
    details.append(summary, pre);
    group.appendChild(details);
    container.appendChild(group);
  }

  return container;
}

function plannerEvaluationEmptyState(text = "Load the demo report to compare planner outputs.") {
  const empty = document.createElement("p");
  empty.className = "planner-evaluation-empty";
  empty.textContent = text;
  return empty;
}

function formatEvaluationScenarioList(names) {
  if (!Array.isArray(names) || !names.length) {
    return "none";
  }

  return names.join(", ");
}

function formatEvaluationPair(scenario, formatter) {
  return `rule ${formatter(scenario.rule_based)}; ai ${formatter(scenario.ai_proposal)}`;
}

function formatEvaluationAgreement(scenario) {
  const agreement = scenario.observation?.agreement;
  if (agreement?.overall === true) {
    return "rule-based and ai_proposal agree";
  }

  if (agreement?.overall === false) {
    const mismatches = [];
    if (agreement.proposal_type === false) {
      mismatches.push("proposal type");
    }
    if (agreement.target === false) {
      mismatches.push("target");
    }
    return `differs on ${mismatches.length ? mismatches.join(", ") : "output"}`;
  }

  const differences = scenario.differences ?? {};
  return differences.same_proposal_type && differences.same_target ? "agree" : "differs";
}

function formatEvaluationProposal(result = {}) {
  const action = result.proposal?.action ?? {};
  const proposalType = result.proposal_type || action.type || "unknown";
  const target = action.target_label || action.target || action.target_element_id;
  const validation = result.validation?.valid === false ? "; validation rejected" : "";

  return target
    ? `${proposalType}: ${compactText(target, 64)}${validation}`
    : `${proposalType}${validation}`;
}

function formatEvaluationExpected(scenario) {
  const expected = scenario.expected ?? scenario.expectation?.expected ?? {};
  const actionType = expected.action_type || "unknown";
  const risk = expected.risk || "unknown";
  const approval = expected.requires_approval ? "approval required" : "no approval";
  const contract = expected.action_contract_type || "none";
  const readiness = expected.click_readiness_status || "not_applicable";
  const blocker = expected.blocker_reason
    ? `; blocker ${compactText(expected.blocker_reason, 48)}`
    : "";
  const blockerCodes = Array.isArray(expected.readiness_blocker_codes) && expected.readiness_blocker_codes.length
    ? `; codes ${expected.readiness_blocker_codes.map((code) => compactText(code, 32)).join(", ")}`
    : "";

  return `${actionType}; risk ${risk}; ${approval}; contract ${contract}; readiness ${readiness}${blocker}${blockerCodes}`;
}

function formatEvaluationExpectation(scenario) {
  const expectation = scenario.expectation ?? {};
  const rule = formatEvaluationExpectationResult(expectation.rule_based);
  const ai = formatEvaluationExpectationResult(expectation.ai_proposal);
  const failures = Array.isArray(expectation.failures) && expectation.failures.length
    ? `; failures ${formatEvaluationNotes(expectation.failures)}`
    : "";

  return `rule ${rule}; ai ${ai}${failures}`;
}

function formatEvaluationExpectationResult(result = {}) {
  if (result.passed === false) {
    return result.failures?.length
      ? `fail: ${formatEvaluationNotes(result.failures)}`
      : "fail";
  }

  return "pass";
}

function formatEvaluationRiskLabel(scenario) {
  const expected = scenario.expected ?? scenario.expectation?.expected ?? {};
  return `expected ${expected.risk || "unknown"}; rule ${formatEvaluationResultRisk(
    scenario.rule_based
  )}; ai ${formatEvaluationResultRisk(scenario.ai_proposal)}`;
}

function formatEvaluationResultRisk(result = {}) {
  const action = result.proposal?.action ?? {};
  const hint = action.target_risk_hint ? `/${action.target_risk_hint}` : "";
  return `${action.risk || "unknown"}${hint}`;
}

function formatEvaluationSafety(result = {}) {
  const safetyDecision = result.safety_decision ?? {};
  const decision = safetyDecision.decision || "unknown";
  const reason = safetyDecision.reason ? `: ${compactText(safetyDecision.reason, 72)}` : "";
  return `${decision}${reason}`;
}

function formatEvaluationContract(result = {}) {
  const actionContract = result.action_contract;

  if (!actionContract) {
    return "none";
  }

  const preview = actionContract.preview_only || actionContract.status === "preview_only"
    ? "preview-only, not executable"
    : actionContract.status || "unknown";

  return `${actionContract.type || "unknown"} / ${preview} / executed ${
    actionContract.executed ? "yes" : "no"
  }`;
}

function formatEvaluationReadiness(result = {}) {
  const clickReadiness = result.click_readiness ?? {};

  if (!clickReadiness.status) {
    return "not present";
  }

  const readiness = readinessDisplayText(clickReadiness);
  const reasons = Array.isArray(clickReadiness.reasons) && clickReadiness.reasons.length
    ? `: ${clickReadiness.reasons.map((reason) => compactText(reason, 48)).join("; ")}`
    : "";
  const blockerCodes = Array.isArray(clickReadiness.blocker_codes) && clickReadiness.blocker_codes.length
    ? ` [${clickReadiness.blocker_codes.map((code) => compactText(code, 32)).join(", ")}]`
    : "";

  return `${readiness}${reasons}${blockerCodes}`;
}

function formatEvaluationBlocker(scenario) {
  return `rule ${formatEvaluationResultBlocker(scenario.rule_based)}; ai ${formatEvaluationResultBlocker(
    scenario.ai_proposal
  )}`;
}

function formatEvaluationResultBlocker(result = {}) {
  const clickReadiness = result.click_readiness ?? {};
  if (Array.isArray(clickReadiness.reasons) && clickReadiness.reasons.length) {
    return clickReadiness.reasons.map((reason) => compactText(reason, 48)).join("; ");
  }

  const contract = result.action_contract;
  if (contract?.status === "preview_only") {
    return `${contract.type || "unknown"} preview-only contract`;
  }

  const action = result.proposal?.action ?? {};
  if (action.type === "no_op" && action.reason) {
    return compactText(action.reason, 72);
  }

  return "none";
}

function formatEvaluationRiskHints(scenario) {
  const hints = Array.isArray(scenario.observation?.risk_hints)
    ? scenario.observation.risk_hints
    : Array.isArray(scenario.inputs?.grounding_hints)
      ? scenario.inputs.grounding_hints
      : [];
  const riskyHints = hints.filter((hint) => hint.risk_hint === "high_risk");

  if (!riskyHints.length) {
    return "none";
  }

  return riskyHints
    .map((hint) => `${hint.label || hint.id || "element"}: ${hint.risk_hint} read-only label hint`)
    .join("; ");
}

function hasEvaluationRiskHint(scenario) {
  const hints = Array.isArray(scenario.observation?.risk_hints)
    ? scenario.observation.risk_hints
    : [];

  return hints.some((hint) => hint.risk_hint === "high_risk");
}

function formatEvaluationNotes(notes) {
  if (!Array.isArray(notes) || !notes.length) {
    return "none";
  }

  return notes.map((note) => compactText(note, 92)).join("; ");
}

function compactCountWithTruncation(section) {
  const count = Number(section?.count ?? 0);
  const safeCount = Number.isFinite(count) ? count : 0;
  return section?.truncated ? `${safeCount} (truncated)` : String(safeCount);
}

function formatPoint(point) {
  if (!point || typeof point !== "object") {
    return "none";
  }

  const x = Number(point.x);
  const y = Number(point.y);

  if (!Number.isFinite(x) || !Number.isFinite(y)) {
    return "none";
  }

  return `${Math.round(x)},${Math.round(y)}`;
}

function resizeTaskInput() {
  const styles = window.getComputedStyle(taskInput);
  const minHeight = parseFloat(styles.minHeight) || 64;
  const maxHeight = parseFloat(styles.maxHeight) || 140;

  taskInput.style.height = `${minHeight}px`;

  const nextHeight = Math.max(minHeight, Math.min(taskInput.scrollHeight, maxHeight));
  taskInput.style.height = `${nextHeight}px`;
  taskInput.style.overflowY = taskInput.scrollHeight > maxHeight ? "auto" : "hidden";
}

function buildDryRunAction(action) {
  if (action.type === "switch_app_hint") {
    return {
      type: "switch_app_preview",
      target_app: action.target || "unknown",
      current_app: action.parameters?.current_app || "unknown",
      executed: false,
    };
  }

  if (action.type !== "target_hint") {
    return null;
  }

  const bbox = normalizeBbox(action.target_bbox);
  if (!bbox) {
    return null;
  }

  return {
    type: "click_preview",
    target_element_id: action.target_element_id ?? "",
    target_label: action.target_label ?? "",
    bbox,
    center: {
      x: Math.round(bbox.x + bbox.width / 2),
      y: Math.round(bbox.y + bbox.height / 2),
    },
    executed: false,
    screenshot_path: screenshotPathFromUiState(currentUiState),
  };
}

function normalizeBbox(bbox) {
  if (!bbox || typeof bbox !== "object") {
    return null;
  }

  const normalized = {
    x: Number(bbox.x),
    y: Number(bbox.y),
    width: Number(bbox.width),
    height: Number(bbox.height),
  };

  if (Object.values(normalized).some((value) => !Number.isFinite(value))) {
    return null;
  }

  return normalized;
}

function renderDryRunAction(dryRunAction = null) {
  currentDryRunAction = dryRunAction;
  dryRunPreview.dataset.state = dryRunAction ? "ready" : "empty";
  hideDryRunScreenshot();

  if (!dryRunAction) {
    dryRunStatus.textContent =
      "No dry-run preview yet. Mirai will stay read-only until a reliable target appears.";
    dryRunDetails.hidden = true;
    dryRunTargetLabel.textContent = "none";
    dryRunBbox.textContent = "none";
    dryRunCenter.textContent = "none";
    dryRunExecuted.textContent = "false";
    return;
  }

  if (dryRunAction.type === "switch_app_preview") {
    dryRunStatus.textContent = `Preview only: would ask user to switch to ${dryRunAction.target_app}. No action executed.`;
    dryRunDetails.hidden = true;
    dryRunTargetLabel.textContent = dryRunAction.target_app;
    dryRunBbox.textContent = "none";
    dryRunCenter.textContent = "none";
    dryRunExecuted.textContent = String(dryRunAction.executed);
    return;
  }

  dryRunStatus.textContent = "Would target this area. No action executed.";
  dryRunDetails.hidden = false;
  dryRunTargetLabel.textContent = dryRunAction.target_label || dryRunAction.target_element_id || "unknown";
  dryRunBbox.textContent = formatTargetBbox(dryRunAction.bbox);
  dryRunCenter.textContent = `${dryRunAction.center.x},${dryRunAction.center.y}`;
  dryRunExecuted.textContent = String(dryRunAction.executed);
  renderDryRunScreenshot(dryRunAction);
}

function screenshotPathFromUiState(uiState) {
  if (!uiState || typeof uiState !== "object") {
    return "";
  }

  return uiState.screenshot_path || uiState.screen?.screenshot_path || "";
}

function screenshotUrlFromPath(path) {
  if (!path) {
    return "";
  }

  return `/${path
    .replaceAll("\\", "/")
    .replace(/^\/+/, "")
    .split("/")
    .map((part) => encodeURIComponent(part))
    .join("/")}`;
}

function renderDryRunScreenshot(dryRunAction) {
  const screenshotUrl = screenshotUrlFromPath(dryRunAction.screenshot_path);
  if (!screenshotUrl) {
    return;
  }

  dryRunShot.hidden = false;
  dryRunImage.onload = () => {
    positionDryRunOverlay(dryRunAction.bbox);
  };
  dryRunImage.onerror = hideDryRunScreenshot;
  dryRunImage.src = screenshotUrl;

  if (dryRunImage.complete && dryRunImage.naturalWidth > 0) {
    positionDryRunOverlay(dryRunAction.bbox);
  }
}

function positionDryRunOverlay(bbox) {
  if (!dryRunImage.naturalWidth || !dryRunImage.naturalHeight) {
    return;
  }

  dryRunOverlay.hidden = false;
  const scaleX = dryRunImage.clientWidth / dryRunImage.naturalWidth;
  const scaleY = dryRunImage.clientHeight / dryRunImage.naturalHeight;
  dryRunOverlay.style.left = `${bbox.x * scaleX}px`;
  dryRunOverlay.style.top = `${bbox.y * scaleY}px`;
  dryRunOverlay.style.width = `${bbox.width * scaleX}px`;
  dryRunOverlay.style.height = `${bbox.height * scaleY}px`;
}

function hideDryRunScreenshot() {
  dryRunShot.hidden = true;
  dryRunImage.removeAttribute("src");
  dryRunImage.onload = null;
  dryRunImage.onerror = null;
  dryRunOverlay.hidden = true;
  dryRunOverlay.removeAttribute("style");
}

async function runWaitExecutionSelfTest() {
  const actionContract = {
    action_id: "manual_wait_0001",
    type: "wait",
    parameters: { duration_ms: 1000 },
    status: "approved_for_execution",
    executed: false,
  };

  executionSelfTest.dataset.state = "running";
  runWaitSelfTest.disabled = true;
  waitSelfTestStatus.textContent = "Running wait self-test...";
  waitSelfTestResult.hidden = true;
  statusText.textContent = "running wait self-test...";

  try {
    const response = await fetch("/execute", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        action_contract: actionContract,
        task: "wait self-test",
      }),
    });
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || payload.reason || `Execution failed with HTTP ${response.status}`);
    }

    renderWaitSelfTestResult(payload);
    executionSelfTest.dataset.state = "done";
    waitSelfTestStatus.textContent = "Wait self-test complete. No mouse/keyboard action executed.";
    statusText.textContent = "wait self-test complete";
    detailError.textContent = "none";
    await fetchRuntimeStatus({ silent: true });
    await fetchRecentEvents({ silent: true });
  } catch (error) {
    executionSelfTest.dataset.state = "error";
    waitSelfTestStatus.textContent = "Wait self-test failed. No mouse/keyboard action executed.";
    detailError.textContent = `Wait self-test failed: ${error.message || String(error)}`;
    statusText.textContent = "wait self-test failed";
    detailsPanel.open = true;
  } finally {
    runWaitSelfTest.disabled = false;
  }
}

function renderWaitSelfTestResult(payload = null) {
  if (!payload) {
    executionSelfTest.dataset.state = "empty";
    waitSelfTestResult.hidden = true;
    waitSelfTestExecutionStatus.textContent = "unknown";
    waitSelfTestExecutionType.textContent = "unknown";
    waitSelfTestDuration.textContent = "unknown";
    waitSelfTestVerificationStatus.textContent = "unknown";
    waitSelfTestVerificationReason.textContent = "unknown";
    waitSelfTestPostObservation.textContent = "unknown";
    return;
  }

  const executionResult = payload.execution_result || payload;
  const verificationResult = payload.verification_result || {};

  waitSelfTestResult.hidden = false;
  waitSelfTestExecutionStatus.textContent = executionResult.status || "unknown";
  waitSelfTestExecutionType.textContent = executionResult.type || "unknown";
  waitSelfTestDuration.textContent =
    executionResult.duration_ms !== undefined ? `${executionResult.duration_ms} ms` : "unknown";
  waitSelfTestVerificationStatus.textContent = verificationResult.status || "unknown";
  waitSelfTestVerificationReason.textContent = verificationResult.reason || "No verification reason.";
  waitSelfTestPostObservation.textContent = payload.post_observation_id || "none";
}

function renderSafetyDecision(safetyDecision = {}) {
  const decision = safetyDecision.decision ?? "unknown";
  const reason = safetyDecision.reason ?? "";

  safetyActionArea.dataset.decision = decision;
  safetyButtons.hidden = true;

  if (decision === "allowed") {
    safetyBrakeMessage.textContent = "Allowed: read-only proposal only.";
    return;
  }

  if (decision === "needs_approval") {
    safetyBrakeMessage.textContent = "Approval needed. No action will run from this UI.";
    setApprovalButtonsDisabled(false);
    safetyButtons.hidden = false;
    return;
  }

  if (decision === "blocked") {
    safetyBrakeMessage.textContent = reason ? `Blocked: ${reason}` : "Blocked by Safety Gate.";
    return;
  }

  safetyBrakeMessage.textContent = "No safety decision yet.";
}

async function recordApprovalDecision(decision) {
  setApprovalButtonsDisabled(true);

  try {
    if (!currentProposal || !currentSafetyDecision) {
      throw new Error("No proposal is available to record.");
    }

    const response = await fetch("/approval", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        decision,
        proposal_id: currentProposal.proposal_id,
        proposal: currentProposal,
        safety_decision: currentSafetyDecision,
        task: currentTask,
      }),
    });
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Approval logging failed with HTTP ${response.status}`);
    }

    safetyActionArea.dataset.decision = decision;
    safetyButtons.hidden = true;
    detailError.textContent = "none";

    if (decision === "approved") {
      safetyBrakeMessage.textContent = "Approved proposal recorded. No action executed.";
      statusText.textContent = "approved recorded";
    } else {
      safetyBrakeMessage.textContent = "Rejected proposal recorded.";
      statusText.textContent = "rejected recorded";
    }

    await fetchRecentEvents({ silent: true });
  } catch (error) {
    detailError.textContent = `Approval log failed: ${error.message || String(error)}`;
    detailsPanel.open = true;
    safetyBrakeMessage.textContent = "Approval logging failed. No action executed.";
    setApprovalButtonsDisabled(false);
  }
}

function setApprovalButtonsDisabled(disabled) {
  approveProposal.disabled = disabled;
  rejectProposal.disabled = disabled;
}

async function fetchRecentEvents(options = {}) {
  const { silent = false } = options;

  refreshEvents.disabled = true;

  try {
    const response = await fetch("/events?limit=20");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Events failed with HTTP ${response.status}`);
    }

    renderRecentEvents(Array.isArray(payload.events) ? payload.events : []);

    if (!silent) {
      detailError.textContent = "none";
    }
  } catch (error) {
    if (!silent) {
      detailError.textContent = `Events refresh failed: ${error.message || String(error)}`;
      detailsPanel.open = true;
    }
  } finally {
    refreshEvents.disabled = false;
  }
}

function renderRecentEvents(events) {
  recentEventsList.replaceChildren();

  if (!events.length) {
    recentEventsList.appendChild(eventListItem("No events yet."));
    return;
  }

  for (const event of events) {
    recentEventsList.appendChild(eventListItem(formatEvent(event)));
  }
}

function eventListItem(text) {
  const item = document.createElement("li");
  item.textContent = text;
  return item;
}

function formatEvent(event) {
  if (event.type === "action_contract.created") {
    const timestamp = event.timestamp ? formatEventTimestamp(event.timestamp) : "no timestamp";
    return `${timestamp} - Preview action contract created: ${actionContractEventType(event)}`;
  }

  const type = friendlyEventType(event.type);
  const timestamp = event.timestamp ? formatEventTimestamp(event.timestamp) : "no timestamp";
  return `${type} - ${timestamp} - ${eventSummary(event)}`;
}

function friendlyEventType(type) {
  if (type === "observation.created") {
    return "Screen observed";
  }

  if (type === "proposal.approved") {
    return "Proposal approved";
  }

  if (type === "proposal.rejected") {
    return "Proposal rejected";
  }

  if (type === "snapshot.deleted") {
    return "Snapshot cleaned";
  }

  if (type === "action_contract.created") {
    return "Preview action contract";
  }

  if (type === "action.execution_requested") {
    return "Execution requested";
  }

  if (type === "action.executed") {
    return "Action executed";
  }

  if (type === "action.blocked") {
    return "Action blocked";
  }

  if (type === "action.verified") {
    return "Action verified";
  }

  if (type === "action.verification_failed") {
    return "Action verification failed";
  }

  return type || "Audit event";
}

function actionContractEventType(event) {
  return event.action_contract_type || event.contract_type || "unknown";
}

function formatEventTimestamp(timestamp) {
  if (typeof timestamp !== "string") {
    return "no timestamp";
  }

  return timestamp.replace("T", " ").replace("Z", " UTC");
}

function eventSummary(event) {
  if (event.type === "observation.created") {
    return event.observation_id ? `Captured ${event.observation_id}` : "Captured a read-only snapshot";
  }

  if (event.type === "proposal.approved" || event.type === "proposal.rejected") {
    return event.task ? `Task: ${event.task}` : event.proposal_id || "Decision recorded";
  }

  if (event.type === "snapshot.deleted") {
    const reason = event.reason ? ` for ${event.reason}` : "";
    return `${event.observation_id || "Old snapshot"} removed${reason}`;
  }

  if (event.type === "action_contract.created") {
    return `Preview action contract created: ${actionContractEventType(event)}`;
  }

  if (event.type === "action.execution_requested") {
    return `${actionContractEventType(event)} requested`;
  }

  if (event.type === "action.executed") {
    const result = event.result || {};
    const duration = result.duration_ms !== undefined ? ` for ${result.duration_ms} ms` : "";
    return `${result.type || actionContractEventType(event)} executed${duration}`;
  }

  if (event.type === "action.blocked") {
    return event.reason || `${actionContractEventType(event)} blocked`;
  }

  if (event.type === "action.verified") {
    const result = event.result || {};
    return `Action verified: ${result.type || actionContractEventType(event)}`;
  }

  if (event.type === "action.verification_failed") {
    return event.reason || "Action verification failed";
  }

  return event.proposal_id || event.observation_id || "audit event";
}

function setDetailsError(error) {
  detailError.textContent = error.message || String(error);
  renderSafetyDecision({
    decision: "blocked",
    reason: "Planning failed before Safety Gate returned a decision.",
  });
  detailsPanel.open = true;
}

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  statusText.textContent = "planning...";
  renderSafetyDecision();
  currentProposal = null;
  currentSafetyDecision = null;
  currentUiState = null;
  currentActionContract = null;
  renderProposalSummary();
  renderActionContract();
  renderClickReadiness();
  renderDryRunAction();
  renderPlannerTrace();
  primaryAction.disabled = true;
  taskInput.disabled = true;

  try {
    const task = taskInput.value.trim();
    const params = new URLSearchParams();

    if (task) {
      params.set("task", task);
    }

    const endpoint = params.toString() ? `/proposal?${params.toString()}` : "/proposal";
    const response = await fetch(endpoint);
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Proposal failed with HTTP ${response.status}`);
    }

    setDetailsFromUiState(payload.ui_state ?? {});
    setDetailsFromProposal(payload.proposal ?? {});
    setDetailsFromActionContract(payload.action_contract ?? null, payload.proposal?.action ?? null);
    renderClickReadiness(
      payload.click_readiness ?? null,
      payload.action_contract ?? null,
      payload.proposal ?? null
    );
    renderPlannerTrace(payload.planner_trace ?? null);
    setDetailsFromSafetyDecision(payload.safety_decision ?? {});
    currentProposal = payload.proposal ?? null;
    currentSafetyDecision = payload.safety_decision ?? null;
    currentTask = task;
    statusText.textContent = "waiting for you";
    await fetchRuntimeStatus({ silent: true });
    await fetchRecentEvents({ silent: true });
  } catch (error) {
    statusText.textContent = "planning failed";
    setDetailsError(error);
  } finally {
    primaryAction.disabled = false;
    taskInput.disabled = false;
  }
});
