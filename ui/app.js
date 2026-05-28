const agentName = document.querySelector("#agentName");
const renameDialog = document.querySelector("#renameDialog");
const renameForm = document.querySelector("#renameForm");
const renameInput = document.querySelector("#renameInput");
const taskForm = document.querySelector("#taskForm");
const taskInput = document.querySelector("#taskInput");
const primaryAction = document.querySelector("#primaryAction");
const statusText = document.querySelector("#statusText");
const safetyActionArea = document.querySelector("#safetyActionArea");
const safetyBrakeMessage = document.querySelector("#safetyBrakeMessage");
const safetyButtons = document.querySelector("#safetyButtons");
const approveProposal = document.querySelector("#approveProposal");
const rejectProposal = document.querySelector("#rejectProposal");
const dryRunPreview = document.querySelector("#dryRunPreview");
const dryRunStatus = document.querySelector("#dryRunStatus");
const dryRunDetails = document.querySelector("#dryRunDetails");
const dryRunTargetLabel = document.querySelector("#dryRunTargetLabel");
const dryRunBbox = document.querySelector("#dryRunBbox");
const dryRunCenter = document.querySelector("#dryRunCenter");
const dryRunExecuted = document.querySelector("#dryRunExecuted");
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
const savedName = window.localStorage.getItem("agent.displayName");
let currentProposal = null;
let currentSafetyDecision = null;
let currentTask = "";
let currentDryRunAction = null;

setDisplayedAgentName(savedName || DEFAULT_AGENT_NAME);

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

resizeTaskInput();
renderSafetyDecision();
renderDryRunAction();

approveProposal.addEventListener("click", async () => {
  await recordApprovalDecision("approved");
});

rejectProposal.addEventListener("click", async () => {
  await recordApprovalDecision("rejected");
});

function setDetailsFromUiState(uiState) {
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
  detailVisibleText.textContent = JSON.stringify(text);
  detailVisibleTextBoxes.textContent = formatTextBoxes(textBoxes);
  detailVisibleElements.textContent = formatVisibleElements(elements);
  detailError.textContent = "none";
}

function formatTextBoxes(textBoxes) {
  if (!textBoxes.length) {
    return "0 boxes";
  }

  const preview = textBoxes.slice(0, 3).map((box) => {
    const bbox = box.bbox ?? {};
    const confidence = Number.isFinite(box.confidence) ? box.confidence.toFixed(2) : "unknown";
    return `${box.text ?? ""} @ ${bbox.x ?? "?"},${bbox.y ?? "?"} ${bbox.width ?? "?"}x${
      bbox.height ?? "?"
    } (${confidence})`;
  });

  return `${textBoxes.length} box(es): ${preview.join("; ")}`;
}

function formatVisibleElements(elements) {
  if (!elements.length) {
    return "0 elements";
  }

  const preview = elements.slice(0, 3).map((element) => {
    const bbox = element.bbox ?? {};
    const confidence = Number.isFinite(element.confidence) ? element.confidence.toFixed(2) : "unknown";
    return `${element.type ?? "unknown"}:${element.label ?? ""} @ ${bbox.x ?? "?"},${
      bbox.y ?? "?"
    } ${bbox.width ?? "?"}x${bbox.height ?? "?"} (${confidence})`;
  });

  return `${elements.length} element(s): ${preview.join("; ")}`;
}

function setDetailsFromProposal(proposal) {
  const action = proposal.action ?? {};
  const dryRunAction = buildDryRunAction(action);

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

  if (!dryRunAction) {
    dryRunStatus.textContent = "No dry-run preview yet.";
    dryRunDetails.hidden = true;
    dryRunTargetLabel.textContent = "none";
    dryRunBbox.textContent = "none";
    dryRunCenter.textContent = "none";
    dryRunExecuted.textContent = "false";
    return;
  }

  dryRunStatus.textContent = "Would target this area. No action executed.";
  dryRunDetails.hidden = false;
  dryRunTargetLabel.textContent = dryRunAction.target_label || dryRunAction.target_element_id || "unknown";
  dryRunBbox.textContent = formatTargetBbox(dryRunAction.bbox);
  dryRunCenter.textContent = `${dryRunAction.center.x},${dryRunAction.center.y}`;
  dryRunExecuted.textContent = String(dryRunAction.executed);
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
  renderDryRunAction();
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
    setDetailsFromSafetyDecision(payload.safety_decision ?? {});
    currentProposal = payload.proposal ?? null;
    currentSafetyDecision = payload.safety_decision ?? null;
    currentTask = task;
    statusText.textContent = "waiting for you";
    detailsPanel.open = true;
  } catch (error) {
    statusText.textContent = "planning failed";
    setDetailsError(error);
  } finally {
    primaryAction.disabled = false;
    taskInput.disabled = false;
  }
});
