import { Shell } from "@/components/shell";
import { getLlm } from "@/lib/retell";
import { agent, business, branding, industryTemplate } from "@/lib/config";
import { SettingsForm } from "./settings-form";

export const dynamic = "force-dynamic";

export default async function ConfiguracionPage() {
  const llm = await getLlm();

  return (
    <Shell>
      <div className="mb-8">
        <h1 className="font-heading text-4xl font-bold italic tracking-tight">
          Configuracion
        </h1>
        <p className="mt-1 text-sm text-neutral-500">
          Personaliza el comportamiento de {agent.name}
        </p>
      </div>

      <SettingsForm
        agentName={agent.name}
        businessName={business.name}
        industryName={industryTemplate.displayName}
        language={agent.language}
        brandColor={branding.primaryColor}
        initialGreeting={llm?.begin_message ?? ""}
        initialPrompt={llm?.general_prompt ?? ""}
        initialTemperature={llm?.model_temperature ?? 0.4}
        model={llm?.model ?? ""}
      />
    </Shell>
  );
}
