const agentName = document.querySelector("#agentName");
const renameDialog = document.querySelector("#renameDialog");
const renameForm = document.querySelector("#renameForm");
const renameInput = document.querySelector("#renameInput");
const primaryAction = document.querySelector("#primaryAction");
const statusText = document.querySelector("#statusText");
const detailsPanel = document.querySelector(".details-panel");
const detailObservationId = document.querySelector("#detailObservationId");
const detailWindowTitle = document.querySelector("#detailWindowTitle");
const detailAppName = document.querySelector("#detailAppName");
const detailScreenSize = document.querySelector("#detailScreenSize");
const detailCursor = document.querySelector("#detailCursor");
const detailScreenshotPath = document.querySelector("#detailScreenshotPath");
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

function setDetailsFromObservation(observation) {
  const activeWindow = observation.active_window ?? {};
  const screen = observation.screen ?? {};
  const cursor = observation.cursor ?? {};

  detailObservationId.textContent = observation.observation_id ?? "unknown";
  detailWindowTitle.textContent = activeWindow.title ?? "unknown";
  detailAppName.textContent = activeWindow.app_name ?? "unknown";
  detailScreenSize.textContent =
    screen.width && screen.height ? `${screen.width} x ${screen.height}` : "unknown";
  detailCursor.textContent =
    Number.isFinite(cursor.x) && Number.isFinite(cursor.y) ? `${cursor.x}, ${cursor.y}` : "unknown";
  detailScreenshotPath.textContent = screen.screenshot_path ?? "not captured";
  detailError.textContent = "none";
}

function setDetailsError(error) {
  detailError.textContent = error.message || String(error);
  detailsPanel.open = true;
}

primaryAction.addEventListener("click", async () => {
  statusText.textContent = "observing...";
  primaryAction.disabled = true;

  try {
    const response = await fetch("/observation");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Observation failed with HTTP ${response.status}`);
    }

    setDetailsFromObservation(payload);
    statusText.textContent = "waiting for you";
  } catch (error) {
    statusText.textContent = "observation failed";
    setDetailsError(error);
  } finally {
    primaryAction.disabled = false;
  }
});
