import { Shell } from "@/components/shell";
import { getLeads, getLeadExtra } from "@/lib/notion";
import { industryTemplate } from "@/lib/config";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export const dynamic = "force-dynamic";

const tempColors: Record<string, string> = {
  Hot: "bg-red-500/20 text-red-400 border-red-500/30",
  Warm: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  Cold: "bg-blue-500/20 text-blue-400 border-blue-500/30",
};

const statusColors: Record<string, string> = {
  "Pendiente de llamar": "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  "En proceso": "bg-blue-500/20 text-blue-400 border-blue-500/30",
  "Cita agendada": "bg-purple-500/20 text-purple-400 border-purple-500/30",
  "No contesta": "bg-orange-500/20 text-orange-400 border-orange-500/30",
  "Cerrado ganado": "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  "Cerrado perdido": "bg-red-500/20 text-red-400 border-red-500/30",
};

export default async function LeadsPage() {
  const leads = await getLeads();
  const extraFields = industryTemplate.leadExtraFields;

  return (
    <Shell>
      <div className="mb-8">
        <h1 className="font-heading text-4xl font-bold italic tracking-tight">
          Leads
        </h1>
        <p className="mt-1 text-sm text-neutral-500">
          {leads.length} prospectos en el CRM
        </p>
      </div>

      <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-white/[0.06] hover:bg-transparent">
              <TableHead className="text-neutral-500">Nombre</TableHead>
              <TableHead className="text-neutral-500">Telefono</TableHead>
              <TableHead className="text-neutral-500">Estatus</TableHead>
              <TableHead className="text-neutral-500">Temp.</TableHead>
              {/* Dynamic columns from industry template */}
              {extraFields.slice(0, 3).map((field: any) => (
                <TableHead key={field.name} className="text-neutral-500">
                  {field.name}
                </TableHead>
              ))}
              <TableHead className="text-neutral-500">Intentos</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {leads.map((lead: any) => (
              <TableRow
                key={lead.id}
                className="border-white/[0.06] hover:bg-white/[0.03]"
              >
                <TableCell className="font-medium">{lead.nombre}</TableCell>
                <TableCell className="text-sm text-neutral-400 font-mono">
                  {lead.telefono}
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    className={`text-[10px] ${statusColors[lead.estatus] || ""}`}
                  >
                    {lead.estatus}
                  </Badge>
                </TableCell>
                <TableCell>
                  {lead.temperatura && (
                    <Badge
                      variant="outline"
                      className={`text-[10px] ${tempColors[lead.temperatura] || ""}`}
                    >
                      {lead.temperatura}
                    </Badge>
                  )}
                </TableCell>
                {/* Dynamic columns */}
                {extraFields.slice(0, 3).map((field: any) => {
                  const value = getLeadExtra(lead._raw, field.name, field.type);
                  const display = Array.isArray(value)
                    ? value.join(", ")
                    : value?.toLocaleString?.("es-MX") ?? String(value ?? "—");
                  return (
                    <TableCell key={field.name} className="text-sm text-neutral-400">
                      {display || "—"}
                    </TableCell>
                  );
                })}
                <TableCell className="text-sm text-neutral-500 text-center">
                  {lead.intentos}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Shell>
  );
}
