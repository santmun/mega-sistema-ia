"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

export function SettingsForm({
  agentName,
  businessName,
  industryName,
  language,
  brandColor,
  initialGreeting,
  initialPrompt,
  initialTemperature,
  model,
}: {
  agentName: string;
  businessName: string;
  industryName: string;
  language: string;
  brandColor: string;
  initialGreeting: string;
  initialPrompt: string;
  initialTemperature: number;
  model: string;
}) {
  const [greeting, setGreeting] = useState(initialGreeting);
  const [prompt, setPrompt] = useState(initialPrompt);
  const [temperature, setTemperature] = useState(initialTemperature);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [outboundStatus, setOutboundStatus] = useState<string | null>(null);
  const [triggeringOutbound, setTriggeringOutbound] = useState(false);

  async function handleSave() {
    setSaving(true);
    setSaved(false);
    try {
      const res = await fetch("/api/settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          beginMessage: greeting,
          generalPrompt: prompt,
          modelTemperature: temperature,
        }),
      });
      if (res.ok) setSaved(true);
    } finally {
      setSaving(false);
    }
  }

  async function handleTriggerOutbound() {
    setTriggeringOutbound(true);
    setOutboundStatus(null);
    try {
      const res = await fetch("/api/trigger-outbound", { method: "POST" });
      const data = await res.json();
      setOutboundStatus(
        `${data.calls_made ?? 0} llamadas realizadas de ${data.leads_found ?? 0} leads pendientes`
      );
    } catch {
      setOutboundStatus("Error al disparar el worker");
    } finally {
      setTriggeringOutbound(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Agent Info */}
      <Card className="border-white/[0.06] bg-white/[0.02]">
        <CardHeader>
          <CardTitle className="font-heading text-lg italic">
            Informacion del Agente
          </CardTitle>
        </CardHeader>
        <CardContent className="flex items-center gap-6">
          <div
            className="flex h-16 w-16 items-center justify-center rounded-2xl text-2xl font-bold text-black"
            style={{ background: `linear-gradient(135deg, ${brandColor}, ${brandColor}dd)` }}
          >
            {agentName.charAt(0)}
          </div>
          <div>
            <p className="font-heading text-xl font-semibold italic">
              {agentName}
            </p>
            <p className="text-sm text-neutral-400">
              Asistente virtual — {businessName}
            </p>
            <div className="flex gap-2 mt-2">
              <Badge
                variant="outline"
                className="border-emerald-500/30 text-emerald-400 text-[10px]"
              >
                Activa
              </Badge>
              {model && (
                <Badge
                  variant="outline"
                  className="border-neutral-600 text-neutral-400 text-[10px]"
                >
                  {model}
                </Badge>
              )}
              <Badge
                variant="outline"
                className="border-neutral-600 text-neutral-400 text-[10px]"
              >
                {language}
              </Badge>
              <Badge
                variant="outline"
                className="border-neutral-600 text-neutral-400 text-[10px]"
              >
                {industryName}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Greeting */}
      <Card className="border-white/[0.06] bg-white/[0.02]">
        <CardHeader>
          <CardTitle className="font-heading text-lg italic">
            Saludo Inicial
          </CardTitle>
          <p className="text-xs text-neutral-500">
            Lo primero que dice {agentName} al contestar una llamada
          </p>
        </CardHeader>
        <CardContent>
          <Textarea
            value={greeting}
            onChange={(e) => setGreeting(e.target.value)}
            rows={3}
            className="bg-white/[0.04] border-white/[0.08] text-sm resize-none"
          />
        </CardContent>
      </Card>

      {/* Prompt */}
      <Card className="border-white/[0.06] bg-white/[0.02]">
        <CardHeader>
          <CardTitle className="font-heading text-lg italic">
            Personalidad y Comportamiento
          </CardTitle>
          <p className="text-xs text-neutral-500">
            Las instrucciones que definen como se comporta {agentName} durante
            las llamadas
          </p>
        </CardHeader>
        <CardContent>
          <Textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={16}
            className="bg-white/[0.04] border-white/[0.08] text-sm font-mono resize-none leading-relaxed"
          />
        </CardContent>
      </Card>

      {/* Temperature */}
      <Card className="border-white/[0.06] bg-white/[0.02]">
        <CardHeader>
          <CardTitle className="font-heading text-lg italic">
            Creatividad
          </CardTitle>
          <p className="text-xs text-neutral-500">
            Que tan creativa es {agentName} en sus respuestas (0 = muy precisa,
            1 = muy creativa)
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="flex-1"
              style={{ accentColor: brandColor }}
            />
            <span
              className="text-lg font-heading font-bold italic w-10 text-right"
              style={{ color: brandColor }}
            >
              {temperature}
            </span>
          </div>
          <div className="flex justify-between text-[10px] text-neutral-600 mt-1 px-1">
            <span>Precisa</span>
            <span>Creativa</span>
          </div>
        </CardContent>
      </Card>

      {/* Save */}
      <div className="flex items-center gap-4">
        <Button
          onClick={handleSave}
          disabled={saving}
          className="bg-white text-black hover:bg-neutral-200 font-medium px-8"
        >
          {saving ? "Guardando..." : "Guardar Cambios"}
        </Button>
        {saved && (
          <span className="text-sm text-emerald-400">
            Cambios guardados correctamente
          </span>
        )}
      </div>

      <Separator className="bg-white/[0.06]" />

      {/* Outbound trigger */}
      <Card className="border-white/[0.06] bg-white/[0.02]">
        <CardHeader>
          <CardTitle className="font-heading text-lg italic">
            Llamadas Outbound
          </CardTitle>
          <p className="text-xs text-neutral-500">
            Dispara manualmente el worker que llama a los leads pendientes
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Button
              onClick={handleTriggerOutbound}
              disabled={triggeringOutbound}
              variant="outline"
              className="hover:bg-white/[0.05]"
              style={{
                borderColor: `${brandColor}4d`,
                color: brandColor,
              }}
            >
              {triggeringOutbound
                ? "Ejecutando..."
                : "Disparar Llamadas Outbound"}
            </Button>
            {outboundStatus && (
              <span className="text-sm text-neutral-400">
                {outboundStatus}
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
