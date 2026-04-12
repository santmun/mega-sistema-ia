import { Shell } from "@/components/shell";
import { getStats, getCalls } from "@/lib/notion";
import { branding, industryTemplate } from "@/lib/config";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const [stats, calls] = await Promise.all([getStats(), getCalls()]);
  const recentCalls = calls.slice(0, 8);
  const color = branding.primaryColor;

  return (
    <Shell>
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-heading text-4xl font-bold italic tracking-tight">
          {branding.dashboardTitle}
        </h1>
        <p className="mt-1 text-sm text-neutral-500">
          Resumen de actividad de tu agente de voz
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <KpiCard label="Total Leads" value={stats.totalLeads} />
        <KpiCard label="Llamadas" value={stats.totalCalls} />
        <KpiCard
          label={industryTemplate.actionLabel + "s"}
          value={stats.citasAgendadas}
          accentColor={color}
        />
        <KpiCard label="Tasa de Exito" value={`${stats.tasaExito}%`} />
      </div>

      {/* Second row */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <KpiCard
          label="Duracion Promedio"
          value={formatDuration(stats.avgDuration)}
          sub="minutos"
        />
        <KpiCard label="Contestadas" value={stats.contestadas} />
        <Card className="border-white/[0.06] bg-white/[0.02]">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-normal uppercase tracking-widest text-neutral-500">
              Temperatura de Leads
            </CardTitle>
          </CardHeader>
          <CardContent className="flex items-end gap-4">
            <TempBadge label="Hot" count={stats.temperatura.hot} color="bg-red-500/20 text-red-400 border-red-500/30" />
            <TempBadge label="Warm" count={stats.temperatura.warm} color="bg-orange-500/20 text-orange-400 border-orange-500/30" />
            <TempBadge label="Cold" count={stats.temperatura.cold} color="bg-blue-500/20 text-blue-400 border-blue-500/30" />
          </CardContent>
        </Card>
      </div>

      {/* Lead Funnel */}
      <div className="mb-8">
        <h2 className="font-heading text-xl font-semibold italic mb-4">
          Funnel de Leads
        </h2>
        <div className="flex gap-2 flex-wrap">
          {Object.entries(stats.statusCounts).map(([status, count]) => (
            <div
              key={status}
              className="flex items-center gap-2 rounded-lg border border-white/[0.06] bg-white/[0.02] px-4 py-2.5"
            >
              <StatusDot status={status} />
              <span className="text-sm text-neutral-400">{status}</span>
              <span className="text-sm font-semibold text-white">
                {count as number}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Calls */}
      <div>
        <h2 className="font-heading text-xl font-semibold italic mb-4">
          Llamadas Recientes
        </h2>
        <div className="space-y-2">
          {recentCalls.map((call: any) => (
            <Card
              key={call.id}
              className="border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04] transition-colors"
            >
              <CardContent className="flex items-center gap-4 py-4">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/[0.06] text-sm">
                  {call.tipo === "Inbound" ? "📥" : "📤"}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">
                      {call.titulo || "Llamada"}
                    </span>
                    <Badge
                      variant="outline"
                      className={
                        call.resultado === "Contestada"
                          ? "border-emerald-500/30 text-emerald-400 text-[10px]"
                          : "border-neutral-600 text-neutral-500 text-[10px]"
                      }
                    >
                      {call.resultado}
                    </Badge>
                    {call.citaAgendada && (
                      <Badge
                        className="text-[10px]"
                        style={{
                          backgroundColor: `${color}33`,
                          color: color,
                          borderColor: `${color}4d`,
                        }}
                      >
                        {industryTemplate.actionLabel}
                      </Badge>
                    )}
                    <SentimentBadge sentiment={call.sentimiento} />
                  </div>
                  {call.resumen && (
                    <p className="mt-1 text-xs text-neutral-500 truncate max-w-2xl">
                      {call.resumen}
                    </p>
                  )}
                </div>
                <div className="text-right shrink-0">
                  <p className="text-xs text-neutral-500">
                    {call.duracion ? formatDuration(call.duracion) : "--:--"}
                  </p>
                  <p className="text-[10px] text-neutral-600 mt-0.5">
                    {call.fecha
                      ? new Date(call.fecha).toLocaleDateString("es-MX", {
                          day: "numeric",
                          month: "short",
                        })
                      : ""}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
          {recentCalls.length === 0 && (
            <p className="text-sm text-neutral-600 py-8 text-center">
              No hay llamadas registradas aun.
            </p>
          )}
        </div>
      </div>
    </Shell>
  );
}

// ── Components ──

function KpiCard({
  label,
  value,
  sub,
  accentColor,
}: {
  label: string;
  value: string | number;
  sub?: string;
  accentColor?: string;
}) {
  return (
    <Card className="border-white/[0.06] bg-white/[0.02]">
      <CardHeader className="pb-1">
        <CardTitle className="text-xs font-normal uppercase tracking-widest text-neutral-500">
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p
          className="text-3xl font-heading font-bold italic tracking-tight"
          style={accentColor ? { color: accentColor } : undefined}
        >
          {value}
        </p>
        {sub && <p className="text-[10px] text-neutral-600 mt-0.5">{sub}</p>}
      </CardContent>
    </Card>
  );
}

function TempBadge({ label, count, color }: { label: string; count: number; color: string }) {
  return (
    <div className={`flex items-center gap-2 rounded-md border px-3 py-1.5 ${color}`}>
      <span className="text-xs font-medium">{label}</span>
      <span className="text-lg font-bold font-heading italic">{count}</span>
    </div>
  );
}

function SentimentBadge({ sentiment }: { sentiment: string }) {
  if (!sentiment) return null;
  const cls: Record<string, string> = {
    Positivo: "text-emerald-500",
    Neutral: "text-neutral-500",
    Negativo: "text-red-500",
  };
  const icon: Record<string, string> = { Positivo: "↑", Neutral: "→", Negativo: "↓" };
  return (
    <span className={`text-[10px] ${cls[sentiment] || "text-neutral-600"}`}>
      {icon[sentiment]} {sentiment}
    </span>
  );
}

function StatusDot({ status }: { status: string }) {
  const colors: Record<string, string> = {
    "Pendiente de llamar": "bg-yellow-400",
    "En proceso": "bg-blue-400",
    "Cita agendada": "bg-purple-400",
    "No contestado": "bg-orange-400",
    "Sin interes": "bg-red-400",
    "Cerrado ganado": "bg-emerald-400",
    "Cerrado perdido": "bg-red-400",
  };
  return <div className={`h-2 w-2 rounded-full ${colors[status] || "bg-neutral-500"}`} />;
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}
