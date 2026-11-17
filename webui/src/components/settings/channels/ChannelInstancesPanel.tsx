import type { ReactNode } from "react";

import {
  configureChannel,
  disableNujinAgentFeature,
  enableNujinAgentFeature,
} from "@/lib/api";
import type { NujinAgentChannelInstanceInfo, NujinAgentFeatureInfo, NujinAgentFeaturesPayload } from "@/lib/types";
import { useClient } from "@/providers/ClientProvider";
import {
  ChannelInstancesPanelView,
  type ChannelInstancesPanelCustomization,
  type ChannelInstancesPanelViewProps,
} from "./ChannelInstancesPanelView";

export type { ChannelInstancesPanelCustomization } from "./ChannelInstancesPanelView";

export function ChannelInstancesPanel({
  feature,
  showBrandLogos,
  instances,
  onFeaturesUpdate,
  customization,
  renderView,
}: {
  feature: NujinAgentFeatureInfo;
  showBrandLogos: boolean;
  instances?: NujinAgentChannelInstanceInfo[];
  onFeaturesUpdate: (payload: NujinAgentFeaturesPayload) => void;
  customization?: ChannelInstancesPanelCustomization;
  renderView?: (props: ChannelInstancesPanelViewProps) => ReactNode;
}) {
  const { client } = useClient();
  const viewProps: ChannelInstancesPanelViewProps = {
    feature,
    showBrandLogos,
    instances,
    customization,
    onToggleInstance: async (instance, checked) => {
      const payload = checked
        ? await enableNujinAgentFeature(client, feature.name, { instanceId: instance.id })
        : await disableNujinAgentFeature(client, feature.name, { instanceId: instance.id });
      onFeaturesUpdate(payload);
    },
    onSaveInstance: async (instance, values) => {
      const payload = await configureChannel(client, feature.name, values, {
        enable: instance.enabled,
        instanceId: instance.id,
      });
      if (payload.nujinagent_features) onFeaturesUpdate(payload.nujinagent_features);
    },
  };
  return renderView ? renderView(viewProps) : <ChannelInstancesPanelView {...viewProps} />;
}
