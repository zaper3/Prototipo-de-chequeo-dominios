import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type CSSProperties,
  type FormEvent,
  type ReactNode,
} from "react";
import {
  Activity,
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  Check,
  ChevronLeft,
  ChevronRight,
  CircleDot,
  Clock3,
  Database,
  ExternalLink,
  FileSearch,
  Fingerprint,
  Gauge,
  Globe2,
  History,
  KeyRound,
  Layers3,
  LoaderCircle,
  LockKeyhole,
  MailCheck,
  Network,
  Radar,
  RefreshCw,
  RotateCcw,
  ScanSearch,
  Search,
  Server,
  ShieldAlert,
  ShieldCheck,
  ShieldQuestion,
  TerminalSquare,
  Trash2,
  X,
} from "lucide-react";
import {
  createScan,
  deleteAllScans,
  deleteScan,
  getChanges,
  getScan,
  listScans,
} from "./api";
import type {
  Finding,
  RiskLevel,
  ScanChanges,
  ScanHistoryItem,
  ScanHistoryPage,
  ScanJob,
  ScanProfile,
  ScanReport,
} from "./types";

type Section = "overview" | "reputation" | "identity" | "dns" | "tls" | "web" | "subdomains" | "network" | "evidence";

const navigation: Array<{ id: Section; label: string; icon: typeof Activity }> = [
  { id: "overview", label: "Resumen", icon: Activity },
  { id: "reputation", label: "Reputación", icon: ShieldQuestion },
  { id: "identity", label: "Identidad", icon: Fingerprint },
  { id: "dns", label: "DNS y correo", icon: MailCheck },
  { id: "tls", label: "TLS/SSL", icon: LockKeyhole },
  { id: "web", label: "Seguridad web", icon: TerminalSquare },
  { id: "subdomains", label: "Subdominios", icon: Network },
  { id: "network", label: "Red y puertos", icon: Server },
  { id: "evidence", label: "Evidencias", icon: FileSearch },
];

const profiles: Array<{ id: ScanProfile; name: string; time: string; description: string }> = [
  { id: "quick", name: "Rápido", time: "~15 s", description: "Identidad, DNS, TLS, HTTP y reputación." },
  { id: "standard", name: "Estándar", time: "~1–2 min", description: "Añade correo, subdominios y puertos frecuentes." },
  { id: "deep", name: "Profundo", time: "varios min", description: "TCP completo, banners y comprobaciones ampliadas." },
];

const riskLabels: Record<RiskLevel, string> = {
  low: "Riesgo bajo",
  moderate: "Riesgo moderado",
  high: "Riesgo alto",
  critical: "Riesgo crítico",
  unknown: "Datos insuficientes",
};

const profileLabels: Record<ScanProfile, string> = { quick: "Rápido", standard: "Estándar", deep: "Profundo" };

function targetPreview(value: string): string | null {
  const clean = value.trim();
  if (!clean) return null;
  try {
    if (clean.includes("://")) return new URL(clean).hostname || null;
  } catch {
    return null;
  }
  return /^[\p{L}0-9.-]+$/u.test(clean) ? clean.replace(/\.$/, "").toLowerCase() : null;
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (Array.isArray(value)) return value.map(formatValue).join(", ");
  if (typeof value === "object") return JSON.stringify(value);
  if (typeof value === "boolean") return value ? "Sí" : "No";
  return String(value);
}

function severityLabel(severity: Finding["severity"]): string {
  return { critical: "Crítica", high: "Alta", medium: "Media", low: "Baja", info: "Info" }[severity];
}

function Panel({ title, kicker, icon, children, className = "" }: { title: string; kicker?: string; icon?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={`panel ${className}`}>
      <header className="panel-header">
        <div className="panel-icon">{icon}</div>
        <div><span className="kicker">{kicker}</span><h2>{title}</h2></div>
      </header>
      {children}
    </section>
  );
}

function DataRows({ data }: { data: Record<string, unknown> }) {
  const entries = Object.entries(data).filter(([, value]) => value !== null && value !== "" && (!Array.isArray(value) || value.length));
  if (!entries.length) return <Empty label="No hay datos disponibles para esta consulta." />;
  return <div className="data-rows">{entries.map(([key, value]) => <div className="data-row" key={key}><span>{key.replaceAll("_", " ")}</span><strong>{formatValue(value)}</strong></div>)}</div>;
}

function Empty({ label }: { label: string }) {
  return <div className="empty"><CircleDot size={17} /><span>{label}</span></div>;
}

function RiskBadge({ risk }: { risk: RiskLevel | null }) {
  return <span className={`risk-badge ${risk ?? "unknown"}`}>{risk ? riskLabels[risk] : "Pendiente"}</span>;
}

function ComparisonCard({ changes }: { changes: ScanChanges | null }) {
  if (!changes?.previous_scan_id) return null;
  const delta = changes.score_delta ?? 0;
  return (
    <div className="comparison-card">
      <div>{delta >= 0 ? <ArrowUp size={17} /> : <ArrowDown size={17} />}<span>Variación frente al análisis anterior</span><strong>{delta > 0 ? "+" : ""}{delta} puntos</strong></div>
      <small>{changes.added_findings.length} hallazgos nuevos · {changes.resolved_findings.length} resueltos · {changes.added_ports.length} puertos nuevos</small>
    </div>
  );
}

function Overview({ report, changes }: { report: ScanReport; changes: ScanChanges | null }) {
  return (
    <div className="overview-grid">
      <Panel title="Riesgo observado" kicker="Evaluación v2" icon={<ShieldCheck size={20} />} className="score-panel">
        <div className="score-content risk-summary">
          <div className="score-ring" style={{ "--score": `${report.score * 3.6}deg` } as CSSProperties}><div><strong>{report.score}</strong><span>/100</span></div></div>
          <div className="score-copy">
            <RiskBadge risk={report.risk_level} />
            <h3>{riskLabels[report.risk_level]}</h3>
            <p>{report.summary}</p>
            <div className="confidence-row"><span>Confianza <strong>{report.confidence}</strong></span><span>Cobertura <strong>{report.coverage_percent}%</strong></span><span>Perfil <strong>{profileLabels[report.profile]}</strong></span></div>
          </div>
        </div>
        <ComparisonCard changes={changes} />
      </Panel>
      <Panel title="Puntuación por categoría" kicker={`Reglas ${report.ruleset_version}`} icon={<Gauge size={20} />}>
        <div className="category-scores">{Object.entries(report.category_scores).map(([name, item]) => <div className={!item.available ? "unavailable" : ""} key={name}><span>{name.replaceAll("_", " ")}</span><div><i style={{ width: `${item.available ? item.score : 0}%` }} /></div><strong>{item.available ? item.score : "N/D"}</strong></div>)}</div>
      </Panel>
      <Panel title="Superficie observada" kicker="Inventario" icon={<Radar size={20} />}>
        <div className="metrics-grid"><div><span>IPs públicas</span><strong>{report.ip_addresses.length}</strong></div><div><span>Subdominios</span><strong>{report.subdomains.length}</strong></div><div><span>Puertos abiertos</span><strong>{report.ports.length}</strong></div><div><span>Hallazgos</span><strong>{report.findings.length}</strong></div></div>
      </Panel>
      <Panel title="Acciones prioritarias" kicker="Siguientes pasos" icon={<ChevronRight size={20} />} className="actions-panel">
        {report.top_actions.length ? <ol>{report.top_actions.map((action) => <li key={action}>{action}</li>)}</ol> : <Empty label="No se generaron acciones prioritarias; el resultado no garantiza ausencia de riesgos." />}
      </Panel>
      <Panel title="Riesgos y recomendaciones" kicker="Evidencias priorizadas" icon={<ShieldAlert size={20} />} className="findings-panel">
        {report.findings.length ? <div className="findings">{report.findings.map((finding) => <article className="finding" key={finding.id}><span className={`severity ${finding.severity}`}>{severityLabel(finding.severity)}</span><div><div className="finding-meta"><span>{finding.category.replaceAll("_", " ")}</span><span>{finding.source}</span><span>-{finding.score_impact}</span></div><h3>{finding.title}</h3><p>{finding.detail}</p><small><ChevronRight size={14} />{finding.recommendation}</small></div></article>)}</div> : <div className="positive"><ShieldCheck /><div><strong>No se detectaron riesgos en las reglas ejecutadas</strong><p>Esto no sustituye una auditoría de seguridad completa.</p></div></div>}
      </Panel>
    </div>
  );
}

function Results({ report, section, changes }: { report: ScanReport; section: Section; changes: ScanChanges | null }) {
  if (section === "overview") return <Overview report={report} changes={changes} />;
  if (section === "reputation") return <Panel title="Inteligencia de reputación" kicker="Proveedores opcionales" icon={<ShieldQuestion size={20} />}><DataRows data={report.reputation} /></Panel>;
  if (section === "identity") return <div className="split-grid"><Panel title="Identidad del dominio" kicker="Antigüedad y registro" icon={<Fingerprint size={20} />}><DataRows data={report.domain_identity} /></Panel><Panel title="WHOIS" kicker="Datos de registro" icon={<FileSearch size={20} />}><DataRows data={report.whois} /></Panel></div>;
  if (section === "dns") return <div className="split-grid"><Panel title="Registros DNS" kicker={`${Object.values(report.dns).flat().length} respuestas`} icon={<Database size={20} />}><div className="record-groups">{Object.entries(report.dns).map(([type, values]) => <div className="record-group" key={type}><span className="record-type">{type}</span><div>{values.length ? values.map((value) => <code key={value}>{value}</code>) : <em>Sin registros</em>}</div></div>)}</div></Panel><Panel title="Seguridad del correo" kicker="SPF, DMARC y transporte" icon={<MailCheck size={20} />}><DataRows data={report.email_security} /></Panel></div>;
  if (section === "tls") return <Panel title="Certificado y protocolos TLS" kicker={report.ssl.valid ? "Certificado validado" : "Validación no disponible"} icon={<LockKeyhole size={20} />}><DataRows data={report.ssl} /></Panel>;
  if (section === "web") return <div className="split-grid"><Panel title="Cabeceras HTTP" kicker={report.http.status_code ? `Respuesta ${report.http.status_code}` : "Sin respuesta"} icon={<TerminalSquare size={20} />}><DataRows data={report.http.headers ?? {}} /></Panel><Panel title="Controles web" kicker="Cookies, CORS y contenido" icon={<ShieldCheck size={20} />}><DataRows data={report.web_security} /><div className="header-checks">{Object.entries(report.http.security_headers ?? {}).map(([name, state]) => <div key={name} className={state.present ? "present" : "missing"}>{state.present ? <Check size={17} /> : <AlertTriangle size={17} />}<span>{name}</span><strong>{state.present ? "Presente" : "Ausente"}</strong></div>)}</div></Panel></div>;
  if (section === "subdomains") return <Panel title="Subdominios encontrados" kicker={`${report.subdomains.length} activos o históricos`} icon={<Network size={20} />}>{report.subdomains.length ? <div className="domain-list">{report.subdomains.map((item) => <div className={item.potential_dangling ? "dangling" : ""} key={item.name}><Globe2 size={16} /><strong>{item.name}</strong><span>{item.sources.join(" + ")}{item.potential_dangling ? " · CNAME potencialmente colgante" : ""}</span></div>)}</div> : <Empty label="No se encontraron subdominios en las fuentes consultadas." />}</Panel>;
  if (section === "network") return <div className="split-grid"><Panel title="Direcciones IP" kicker="Resolución pública" icon={<Globe2 size={20} />}><div className="ip-list">{report.ip_addresses.map((ip) => <code key={ip}>{ip}</code>)}</div></Panel><Panel title="Puertos TCP abiertos" kicker={`${report.ports.length} encontrados en la IP principal`} icon={<Server size={20} />}>{report.ports.length ? <div className="ports-grid">{report.ports.map((port) => <div className={port.risk ? "risky" : ""} key={port.port}><strong>{port.port}</strong><span>{port.service}</span><small>{port.banner || port.protocol.toUpperCase()}</small></div>)}</div> : <Empty label="No se detectaron puertos abiertos o el perfil no los comprobó." />}</Panel></div>;
  return <Panel title="Evidencias y cobertura" kicker="Trazabilidad" icon={<Layers3 size={20} />}><div className="coverage-block"><div><span>Completados</span>{report.coverage.completed_modules.map((item) => <code key={item}>{item}</code>)}</div><div><span>No disponibles</span>{report.coverage.missing_modules.length ? report.coverage.missing_modules.map((item) => <code key={item}>{item}</code>) : <strong>Todos los módulos respondieron</strong>}</div></div>{Object.keys(report.errors).length ? <DataRows data={report.errors} /> : null}</Panel>;
}

function HistoryPanel({ page, loading, query, setQuery, risk, setRisk, profile, setProfile, dateFrom, setDateFrom, dateTo, setDateTo, onPrevious, onNext, onOpen, onRepeat, onDelete, onDeleteAll, onClose }: { page: ScanHistoryPage | null; loading: boolean; query: string; setQuery: (value: string) => void; risk: RiskLevel | ""; setRisk: (value: RiskLevel | "") => void; profile: ScanProfile | ""; setProfile: (value: ScanProfile | "") => void; dateFrom: string; setDateFrom: (value: string) => void; dateTo: string; setDateTo: (value: string) => void; onPrevious: () => void; onNext: () => void; onOpen: (item: ScanHistoryItem) => void; onRepeat: (item: ScanHistoryItem) => void; onDelete: (item: ScanHistoryItem) => void; onDeleteAll: () => void; onClose: () => void }) {
  const currentPage = page ? Math.floor(page.offset / page.limit) + 1 : 1;
  const totalPages = page ? Math.max(1, Math.ceil(page.total / page.limit)) : 1;
  return <section className="history-panel"><header><div><span className="kicker">REGISTRO LOCAL</span><h2>Historial de análisis</h2><p>Los informes se conservan durante 90 días en este equipo.</p></div><button className="icon-button" onClick={onClose} aria-label="Cerrar historial"><X size={19} /></button></header><div className="history-filters"><label><Search size={15} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar dominio" /></label><select aria-label="Filtrar por riesgo" value={risk} onChange={(event) => setRisk(event.target.value as RiskLevel | "")}><option value="">Todos los riesgos</option>{Object.entries(riskLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select><select aria-label="Filtrar por perfil" value={profile} onChange={(event) => setProfile(event.target.value as ScanProfile | "")}><option value="">Todos los perfiles</option>{profiles.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select><input aria-label="Fecha desde" type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} /><input aria-label="Fecha hasta" type="date" value={dateTo} min={dateFrom || undefined} onChange={(event) => setDateTo(event.target.value)} /><button className="danger-ghost" onClick={onDeleteAll} disabled={!page?.total}><Trash2 size={14} /> Vaciar</button></div>{loading ? <div className="history-loading"><LoaderCircle className="spin" /> Cargando historial…</div> : page?.items.length ? <><div className="history-list">{page.items.map((item) => <article key={item.id}><button className="history-main" onClick={() => onOpen(item)}><div><strong>{item.domain}</strong><span>{new Date(item.created_at).toLocaleString("es-ES")}</span></div><RiskBadge risk={item.risk_level} /><div className="history-score"><strong>{item.score ?? "—"}</strong><span>{profileLabels[item.profile]}</span></div></button><div className="history-actions"><button onClick={() => onRepeat(item)} title="Repetir"><RotateCcw size={15} /></button><button onClick={() => onDelete(item)} title="Eliminar"><Trash2 size={15} /></button></div></article>)}</div><div className="history-pagination"><span>{page.total} informes · página {currentPage} de {totalPages}</span><div><button onClick={onPrevious} disabled={page.offset === 0} aria-label="Página anterior"><ChevronLeft size={15} /></button><button onClick={onNext} disabled={page.offset + page.limit >= page.total} aria-label="Página siguiente"><ChevronRight size={15} /></button></div></div></> : <Empty label="Todavía no hay análisis que coincidan con los filtros." />}</section>;
}

export default function App() {
  const [target, setTarget] = useState("");
  const [profile, setProfile] = useState<ScanProfile>("standard");
  const [authorized, setAuthorized] = useState(false);
  const [deepAuthorized, setDeepAuthorized] = useState(false);
  const [job, setJob] = useState<ScanJob | null>(null);
  const [changes, setChanges] = useState<ScanChanges | null>(null);
  const [error, setError] = useState("");
  const [section, setSection] = useState<Section>("overview");
  const [showHistory, setShowHistory] = useState(false);
  const [historyPage, setHistoryPage] = useState<ScanHistoryPage | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyQuery, setHistoryQuery] = useState("");
  const [historyRisk, setHistoryRisk] = useState<RiskLevel | "">("");
  const [historyProfile, setHistoryProfile] = useState<ScanProfile | "">("");
  const [historyDateFrom, setHistoryDateFrom] = useState("");
  const [historyDateTo, setHistoryDateTo] = useState("");
  const [historyOffset, setHistoryOffset] = useState(0);
  const busy = job?.status === "queued" || job?.status === "running";
  const preview = useMemo(() => targetPreview(target), [target]);
  const canSubmit = Boolean(target.trim() && authorized && !busy && (profile !== "deep" || deepAuthorized));

  const refreshHistory = useCallback(async () => {
    setHistoryLoading(true);
    try { setHistoryPage(await listScans({ query: historyQuery, riskLevel: historyRisk, profile: historyProfile, dateFrom: historyDateFrom, dateTo: historyDateTo, limit: 10, offset: historyOffset })); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "No se pudo cargar el historial."); }
    finally { setHistoryLoading(false); }
  }, [historyDateFrom, historyDateTo, historyOffset, historyProfile, historyQuery, historyRisk]);

  useEffect(() => { setHistoryOffset(0); }, [historyQuery, historyRisk, historyProfile, historyDateFrom, historyDateTo]);

  useEffect(() => { void refreshHistory(); }, [refreshHistory]);

  useEffect(() => {
    if (!job || !busy) return;
    const timer = window.setTimeout(async () => {
      try {
        const updated = await getScan(job.id);
        setJob(updated);
        if (updated.status === "failed") setError(updated.error ?? "El análisis no pudo completarse.");
        if (updated.status === "completed") {
          setChanges(await getChanges(updated.id));
          await refreshHistory();
        }
      } catch (caught) { setError(caught instanceof Error ? caught.message : "No se pudo consultar el progreso."); }
    }, 900);
    return () => window.clearTimeout(timer);
  }, [job, busy, refreshHistory]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;
    setError(""); setSection("overview"); setChanges(null); setShowHistory(false);
    try { setJob(await createScan(target, profile)); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "No se pudo iniciar el análisis."); }
  }

  async function openHistory(item: ScanHistoryItem) {
    try { const stored = await getScan(item.id); setJob(stored); setChanges(await getChanges(item.id)); setSection("overview"); setShowHistory(false); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "No se pudo abrir el informe."); }
  }

  function repeatHistory(item: ScanHistoryItem) {
    setTarget(item.input_target); setProfile(item.profile); setAuthorized(false); setDeepAuthorized(false); setJob(null); setShowHistory(false); window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function removeHistory(item: ScanHistoryItem) {
    if (!window.confirm(`¿Eliminar el análisis de ${item.domain}?`)) return;
    await deleteScan(item.id); if (job?.id === item.id) setJob(null); await refreshHistory();
  }

  async function removeAllHistory() {
    if (!window.confirm("¿Eliminar todo el historial local? Esta acción no se puede deshacer.")) return;
    await deleteAllScans(); setJob(null); await refreshHistory();
  }

  function reset() { setJob(null); setChanges(null); setTarget(""); setAuthorized(false); setDeepAuthorized(false); setSection("overview"); }

  return <div className="app-shell">
    <header className="topbar"><a className="brand" href="#top" aria-label="Inicio"><span><ScanSearch size={23} /></span><div><strong>DOMAIN<span>CHECK</span></strong><small>OSINT CONSOLE</small></div></a><div className="topbar-actions"><button onClick={() => setShowHistory((value) => !value)}><History size={16} /><span>Historial</span><strong>{historyPage?.total ?? 0}</strong></button><div className="topbar-status"><i /><span>Motor local</span><strong>v0.2.0-alpha.1</strong></div></div></header>
    <main id="top">
      <section className="hero"><div className="eyebrow"><Radar size={15} /> Inteligencia de superficie digital</div><h1>Evalúa la exposición de<br /><span>cualquier dominio público.</span></h1><p>Señales técnicas, reputación, cobertura y evolución histórica explicadas con un lenguaje orientado al riesgo.</p><form className="scan-form" onSubmit={submit}><div className="domain-field"><Globe2 size={21} /><input aria-label="Dominio o URL" value={target} onChange={(event) => setTarget(event.target.value)} placeholder="ejemplo.com o https://ejemplo.com/ruta" disabled={busy} autoComplete="off" spellCheck="false" /><button disabled={!canSubmit}>{busy ? <LoaderCircle className="spin" size={19} /> : <ScanSearch size={19} />}{busy ? "Analizando" : "Analizar"}</button></div>{target.includes("://") && preview && <div className="normalization-hint"><Check size={15} /><span>Se analizará el dominio <strong>{preview}</strong>; la ruta no forma parte del análisis.</span></div>}<div className="profile-selector">{profiles.map((item) => <button type="button" aria-label={`${item.name} ${item.time}`} className={profile === item.id ? "selected" : ""} key={item.id} onClick={() => { setProfile(item.id); if (item.id !== "deep") setDeepAuthorized(false); }} disabled={busy}><span>{item.name}<small>{item.time}</small></span><p>{item.description}</p></button>)}</div><div className="scan-options"><label><input type="checkbox" checked={authorized} onChange={(event) => setAuthorized(event.target.checked)} disabled={busy} /><span className="fake-check"><Check size={13} /></span><span>Confirmo que tengo autorización para analizar este objetivo</span></label>{profile === "deep" && <label className="deep-consent"><input type="checkbox" checked={deepAuthorized} onChange={(event) => setDeepAuthorized(event.target.checked)} disabled={busy} /><span className="fake-check"><Check size={13} /></span><span>Autorizo el escaneo TCP completo y comprobaciones profundas</span></label>}</div></form></section>
      {showHistory && <HistoryPanel page={historyPage} loading={historyLoading} query={historyQuery} setQuery={setHistoryQuery} risk={historyRisk} setRisk={setHistoryRisk} profile={historyProfile} setProfile={setHistoryProfile} dateFrom={historyDateFrom} setDateFrom={setHistoryDateFrom} dateTo={historyDateTo} setDateTo={setHistoryDateTo} onPrevious={() => setHistoryOffset((value) => Math.max(0, value - 10))} onNext={() => setHistoryOffset((value) => value + 10)} onOpen={openHistory} onRepeat={repeatHistory} onDelete={removeHistory} onDeleteAll={removeAllHistory} onClose={() => setShowHistory(false)} />}
      {error && <div className="error-banner"><ShieldAlert size={20} /><div><strong>No se pudo completar la solicitud</strong><span>{error}</span></div><button onClick={() => setError("")} aria-label="Cerrar">×</button></div>}
      {busy && job && <section className="progress-card"><div className="radar-loader"><Radar /><i /><i /><i /></div><div className="progress-copy"><span>ANÁLISIS {profileLabels[job.profile].toUpperCase()} EN CURSO</span><h2>{job.domain}</h2><p>{job.stage}</p><div className="progress-track"><i style={{ width: `${job.progress}%` }} /></div><small><Clock3 size={14} /> Los resultados se guardarán en el historial local.<strong>{job.progress}%</strong></small></div></section>}
      {job?.status === "completed" && job.report && <section className="dashboard"><div className="result-heading"><div><span className="kicker">INFORME OSINT PERSISTENTE</span><h2>{job.report.domain}</h2><p><Clock3 size={14} /> {new Date(job.report.generated_at).toLocaleString("es-ES")} · {job.report.duration_seconds}s · {profileLabels[job.report.profile]}</p></div><button onClick={reset}><RefreshCw size={16} /> Nuevo análisis</button></div><div className="dashboard-layout"><aside>{navigation.map(({ id, label, icon: Icon }) => <button key={id} className={section === id ? "active" : ""} onClick={() => setSection(id)}><Icon size={17} /><span>{label}</span><ChevronRight size={14} /></button>)}<div className="aside-note"><KeyRound size={18} /><strong>Riesgo observado</strong><p>La categoría no certifica que un dominio sea seguro.</p></div></aside><div className="result-content"><Results report={job.report} section={section} changes={changes} />{Object.keys(job.report.errors).length > 0 && <div className="partial-warning"><AlertTriangle size={17} /><span>Informe parcial: {Object.keys(job.report.errors).join(", ")} no devolvió datos.</span></div>}</div></div></section>}
      {!job && !showHistory && <section className="workflow"><div><span>01</span><h3>Dominio o URL</h3><p>Extraemos el hostname y bloqueamos destinos privados.</p></div><ChevronRight /><div><span>02</span><h3>Perfil proporcional</h3><p>Elige tiempo y profundidad según el objetivo.</p></div><ChevronRight /><div><span>03</span><h3>Riesgo y evolución</h3><p>Compara hallazgos con consultas anteriores.</p></div></section>}
    </main>
    <footer><div><ShieldCheck size={17} /><span>Análisis defensivo, autorizado y local</span></div><a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">API OpenAPI <ExternalLink size={13} /></a></footer>
  </div>;
}
