import { useRef, useState, useSyncExternalStore } from "react";

import type { ToolsCatalog } from "@/lib/tools-catalog-cache";

import type { AutomationFilter } from "@/components/settings/system/AutomationsSettings";
import {
  DEFAULT_CUSTOM_MCP_FORM,
  type CustomMcpForm,
} from "@/components/settings/system/AppsSettings";
import type {
  AutomationsPayload,
  McpOAuthFlowPayload,
  NujinAgentFeatureInfo,
  NujinAgentFeaturesPayload,
  SessionAutomationJob,
} from "@/lib/types";

export type NujinAgentFeatureInstallRequest = {
  feature: NujinAgentFeatureInfo;
  installOnly: boolean;
};

export function useSystemSettingsState(toolsCatalog: ToolsCatalog) {
  const { cliApps, mcpPresets, invalidation: toolsCatalogInvalidation } = useSyncExternalStore(toolsCatalog.subscribe, toolsCatalog.getSnapshot);
  const { setCliApps, setMcpPresets } = toolsCatalog;
  const [nujinagentFeatures, setNujinAgentFeatures] = useState<NujinAgentFeaturesPayload | null>(null);
  const [automations, setAutomations] = useState<AutomationsPayload | null>(null);
  const [cliAppsLoading, setCliAppsLoading] = useState(true);
  const [nujinagentFeaturesLoading, setNujinAgentFeaturesLoading] = useState(true);
  const [mcpPresetsLoading, setMcpPresetsLoading] = useState(true);
  const [automationsLoading, setAutomationsLoading] = useState(true);
  const [cliAppsAction, setCliAppsAction] = useState<string | null>(null);
  const [nujinagentFeatureAction, setNujinAgentFeatureAction] = useState<string | null>(null);
  const nujinagentFeatureActionRef = useRef<string | null>(null);
  const [nujinagentFeatureConfirm, setNujinAgentFeatureConfirm] =
    useState<NujinAgentFeatureInstallRequest | null>(null);
  const [mcpPresetAction, setMcpPresetAction] = useState<string | null>(null);
  const [mcpOAuthFlow, setMcpOAuthFlow] = useState<McpOAuthFlowPayload | null>(null);
  const mcpOAuthFlowRef = useRef<McpOAuthFlowPayload | null>(null);
  const mcpOAuthPopupRef = useRef<Window | null>(null);
  const mcpOAuthNavigatedUrlRef = useRef<string | null>(null);
  const [mcpOAuthPopupBlocked, setMcpOAuthPopupBlocked] = useState(false);
  const [mcpOAuthCallbackUrl, setMcpOAuthCallbackUrl] = useState("");
  const [mcpOAuthCompleting, setMcpOAuthCompleting] = useState(false);
  const [mcpOAuthCallbackError, setMcpOAuthCallbackError] = useState<string | null>(null);
  const [appsQuery, setAppsQuery] = useState("");
  const [automationsFilter, setAutomationsFilter] = useState<AutomationFilter>("all");
  const [cliAppsMessage, setCliAppsMessage] = useState<string | null>(null);
  const [cliAppsError, setCliAppsError] = useState<string | null>(null);
  const [nujinagentFeaturesError, setNujinAgentFeaturesError] = useState<string | null>(null);
  const [cliAppsFocusName, setCliAppsFocusName] = useState<string | null>(null);
  const [mcpMessage, setMcpMessage] = useState<string | null>(null);
  const [mcpError, setMcpError] = useState<string | null>(null);
  const [automationsError, setAutomationsError] = useState<string | null>(null);
  const [automationAction, setAutomationAction] = useState<string | null>(null);
  const [automationPendingDelete, setAutomationPendingDelete] =
    useState<SessionAutomationJob | null>(null);
  const [automationPendingEdit, setAutomationPendingEdit] =
    useState<SessionAutomationJob | null>(null);
  const [mcpFieldValues, setMcpFieldValues] = useState<Record<string, Record<string, string>>>({});
  const [customMcpForm, setCustomMcpForm] = useState<CustomMcpForm>(DEFAULT_CUSTOM_MCP_FORM);
  const [mcpConfigImport, setMcpConfigImport] = useState("");

  return {
    toolsCatalog,
    toolsCatalogInvalidation,
    appsQuery,
    automationAction,
    automationPendingDelete,
    automationPendingEdit,
    automations,
    automationsError,
    automationsFilter,
    automationsLoading,
    cliApps,
    cliAppsAction,
    cliAppsError,
    cliAppsFocusName,
    cliAppsLoading,
    cliAppsMessage,
    customMcpForm,
    mcpConfigImport,
    mcpError,
    mcpFieldValues,
    mcpMessage,
    mcpOAuthCallbackError,
    mcpOAuthCallbackUrl,
    mcpOAuthCompleting,
    mcpOAuthFlow,
    mcpOAuthFlowRef,
    mcpOAuthNavigatedUrlRef,
    mcpOAuthPopupBlocked,
    mcpOAuthPopupRef,
    mcpPresetAction,
    mcpPresets,
    mcpPresetsLoading,
    nujinagentFeatureAction,
    nujinagentFeatureActionRef,
    nujinagentFeatureConfirm,
    nujinagentFeatures,
    nujinagentFeaturesError,
    nujinagentFeaturesLoading,
    setAppsQuery,
    setAutomationAction,
    setAutomationPendingDelete,
    setAutomationPendingEdit,
    setAutomations,
    setAutomationsError,
    setAutomationsFilter,
    setAutomationsLoading,
    setCliApps,
    setCliAppsAction,
    setCliAppsError,
    setCliAppsFocusName,
    setCliAppsLoading,
    setCliAppsMessage,
    setCustomMcpForm,
    setMcpConfigImport,
    setMcpError,
    setMcpFieldValues,
    setMcpMessage,
    setMcpOAuthCallbackError,
    setMcpOAuthCallbackUrl,
    setMcpOAuthCompleting,
    setMcpOAuthFlow,
    setMcpOAuthPopupBlocked,
    setMcpPresetAction,
    setMcpPresets,
    setMcpPresetsLoading,
    setNujinAgentFeatureAction,
    setNujinAgentFeatureConfirm,
    setNujinAgentFeatures,
    setNujinAgentFeaturesError,
    setNujinAgentFeaturesLoading,
  };
}

export type SystemSettingsState = ReturnType<typeof useSystemSettingsState>;
