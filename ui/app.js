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
    return `${element.type ?? "unknown"}:${compactText(element.label ?? "", 48)} @ ${bbox.x ?? "?"},${
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

function renderClickReadiness(clickReadiness = null, actionContract = null) {
  clickReadinessReasons.replaceChildren();
  clickReadinessReasons.hidden = true;
  const isClickContract = actionContract?.type === "click";
  const status = clickReadiness?.status || "not_applicable";

  if (!isClickContract || status === "not_applicable") {
    clickReadinessPanel.dataset.state = "not_applicable";
    clickReadinessSummary.textContent = "Click readiness: not applicable";
    return;
  }

  clickReadinessPanel.dataset.state = status;
  clickReadinessSummary.textContent = `Click readiness: ${status}`;

  const reasons = Array.isArray(clickReadiness.reasons) ? clickReadiness.reasons : [];
  if (!reasons.length) {
    return;
  }

  clickReadinessReasons.hidden = false;
  for (const reason of reasons) {
    const item = document.createElement("li");
    item.textContent = reason;
    clickReadinessReasons.appendChild(item);
  }
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
    renderClickReadiness(payload.click_readiness ?? null, payload.action_contract ?? null);
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
