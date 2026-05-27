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
const detailVisibleElements = document.querySelector("#detailVisibleElements");
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
  const elements = Array.isArray(uiState.visible_elements) ? uiState.visible_elements : [];

  detailUiStateId.textContent = uiState.ui_state_id ?? "unknown";
  detailObservationId.textContent = uiState.source_observation_id ?? "unknown";
  detailAppGuess.textContent = uiState.app_guess ?? "unknown";
  detailStateGuess.textContent = uiState.state_guess ?? "unknown";
  detailSummary.textContent = uiState.summary ?? "No summary available.";
  detailConfidence.textContent =
    Number.isFinite(uiState.confidence) ? uiState.confidence.toFixed(2) : "unknown";
  detailVisibleElements.textContent = JSON.stringify(elements);
  detailError.textContent = "none";
}

function setDetailsError(error) {
  detailError.textContent = error.message || String(error);
  detailsPanel.open = true;
}

primaryAction.addEventListener("click", async () => {
  statusText.textContent = "understanding...";
  primaryAction.disabled = true;

  try {
    const response = await fetch("/understanding");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Understanding failed with HTTP ${response.status}`);
    }

    setDetailsFromUiState(payload);
    statusText.textContent = "waiting for you";
  } catch (error) {
    statusText.textContent = "understanding failed";
    setDetailsError(error);
  } finally {
    primaryAction.disabled = false;
  }
});
