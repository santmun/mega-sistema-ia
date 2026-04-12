/**
 * Server-side config loader.
 * Reads sofia.config.yaml and the industry template at build/request time.
 */

import fs from "fs";
import path from "path";
import yaml from "js-yaml";

const PROJECT_ROOT = path.resolve(process.cwd(), "..");

function loadYaml(filePath: string): Record<string, any> {
  try {
    const content = fs.readFileSync(filePath, "utf-8");
    return (yaml.load(content) as Record<string, any>) ?? {};
  } catch {
    return {};
  }
}

const config = loadYaml(path.join(PROJECT_ROOT, "sofia.config.yaml"));

const industry = config.business?.industry ?? "";
const template = industry
  ? loadYaml(path.join(PROJECT_ROOT, `prompts/${industry}.yaml`))
  : {};

// --- Exports ---

export const business = {
  name: config.business?.name ?? "",
  industry,
  timezone: config.business?.timezone ?? "America/Mexico_City",
  phone: config.business?.phone ?? "",
  address: config.business?.address ?? "",
  hours: config.business?.hours ?? "",
  website: config.business?.website ?? "",
};

export const agent = {
  name: config.agent?.name ?? "Sofia",
  language: config.agent?.language ?? "es-MX",
  personality: config.agent?.personality ?? "",
};

export const branding = {
  primaryColor: config.branding?.primary_color ?? "#06b6d4",
  logoText: config.branding?.logo_text ?? business.name?.split(" ")[0] ?? "AI",
  dashboardTitle: config.branding?.dashboard_title ?? "Panel de Control",
};

export const industryTemplate = {
  displayName: template.display_name ?? industry,
  productLabel: template.product_label ?? "Productos",
  actionLabel: template.action_label ?? "Agendar",
  leadExtraFields: template.crm_fields?.lead_extra_fields ?? [],
};

/** Get the first letter for the logo icon */
export function logoInitial(): string {
  return agent.name.charAt(0).toUpperCase();
}
