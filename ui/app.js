const agentName = document.querySelector("#agentName");
const renameDialog = document.querySelector("#renameDialog");
const renameForm = document.querySelector("#renameForm");
const renameInput = document.querySelector("#renameInput");
const primaryAction = document.querySelector("#primaryAction");
const statusText = document.querySelector("#statusText");
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
const detailActionParameters = document.querySelector("#detailActionParameters");
const detailActionReason = document.querySelector("#detailActionReason");
const detailActionRisk = document.querySelector("#detailActionRisk");
const detailRequiresApproval = document.querySelector("#detailRequiresApproval");
const detailError = document.querySelector("#detailError");

const savedName = window.localStorage.getItem("agent.displayName");

if (savedName) {
  agentName.textContent = savedName;
  document.title = savedName;
}

function setAgentName(name) {
  const trimmed = name.trim();

  if (!trimmed) {
    return;
  }

  agentName.textContent = trimmed;
  document.title = trimmed;
  window.localStorage.setItem("agent.displayName", trimmed);
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

  detailProposalId.textContent = proposal.proposal_id ?? "unknown";
  detailActionType.textContent = action.type ?? "unknown";
  detailActionTarget.textContent = action.target ?? "unknown";
  detailActionParameters.textContent = JSON.stringify(action.parameters ?? {});
  detailActionReason.textContent = action.reason ?? "No proposal reason.";
  detailActionRisk.textContent = action.risk ?? "unknown";
  detailRequiresApproval.textContent =
    typeof action.requires_approval === "boolean" ? String(action.requires_approval) : "unknown";
}

function setDetailsError(error) {
  detailError.textContent = error.message || String(error);
  detailsPanel.open = true;
}

primaryAction.addEventListener("click", async () => {
  statusText.textContent = "planning...";
  primaryAction.disabled = true;

  try {
    const response = await fetch("/proposal");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Proposal failed with HTTP ${response.status}`);
    }

    setDetailsFromUiState(payload.ui_state ?? {});
    setDetailsFromProposal(payload.proposal ?? {});
    statusText.textContent = "waiting for you";
  } catch (error) {
    statusText.textContent = "planning failed";
    setDetailsError(error);
  } finally {
    primaryAction.disabled = false;
  }
});
