import { Shell } from "@/components/shell";
import { getCalls } from "@/lib/notion";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

export const dynamic = "force-dynamic";

export default async function LlamadasPage() {
  const calls = await getCalls();

  return (
    <Shell>
      <div className="mb-8">
        <h1 className="font-heading text-4xl font-bold italic tracking-tight">
          Llamadas
        </h1>
        <p className="mt-1 text-sm text-neutral-500">
          {calls.length} llamadas registradas
        </p>
      </div>

      <div className="space-y-3">
        {calls.map((call: any) => (
          <Card key={call.id} className="border-white/[0.06] bg-white/[0.02]">
            <CardContent className="py-5">
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white/[0.06] text-base">
                  {call.tipo === "Inbound" ? "📥" : "📤"}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium">
                      {call.titulo || "Llamada"}
                    </span>
                    <Badge
                      variant="outline"
                      className={
                        call.tipo === "Inbound"
                          ? "border-emerald-500/30 text-emerald-400 text-[10px]"
                          : "border-blue-500/30 text-blue-400 text-[10px]"
                      }
                    >
                      {call.tipo}
                    </Badge>
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
                    {call.sentimiento && (
                      <span
                        className={`text-[10px] ${
                          call.sentimiento === "Positivo"
                            ? "text-emerald-400"
                            : call.sentimiento === "Negativo"
                              ? "text-red-400"
                              : "text-neutral-500"
                        }`}
                      >
                        {call.sentimiento}
                      </span>
                    )}
                  </div>
                  {call.resumen && (
                    <p className="text-sm text-neutral-400 leading-relaxed">
                      {call.resumen}
                    </p>
                  )}
                  <div className="flex items-center gap-4 mt-2 text-[11px] text-neutral-600">
                    {call.telefono && <span>Tel: {call.telefono}</span>}
                    {call.duracion > 0 && (
                      <span>
                        Duracion: {Math.floor(call.duracion / 60)}:
                        {String(call.duracion % 60).padStart(2, "0")}
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-xs text-neutral-500">
                    {call.fecha
                      ? new Date(call.fecha).toLocaleDateString("es-MX", {
                          day: "numeric",
                          month: "short",
                          year: "numeric",
                        })
                      : ""}
                  </p>
                  <p className="text-[10px] text-neutral-600 mt-0.5">
                    {call.fecha
                      ? new Date(call.fecha).toLocaleTimeString("es-MX", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : ""}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {calls.length === 0 && (
          <p className="text-sm text-neutral-600 py-12 text-center">
            No hay llamadas registradas aun.
          </p>
        )}
      </div>
    </Shell>
  );
}
