#!/usr/bin/env python3
# Report settimanale fatturato - Clinica Veterinaria Tergeste
# Uso: python3 report.py data.json out.html
import json, sys, datetime as dt
D = json.load(open(sys.argv[1], encoding="utf-8")); OUT = sys.argv[2]
BLU = "#517DBC"
# Benchmark dai bilanci (ricavi da prestazioni, conto 70.09) -> media settimanale = ricavi/giorni*7
BIL = [("2023", 1083590.95, 365), ("2024", 972988.11, 366), ("2025", 1046051.96, 365), ("Q1 2026 (provv.)", 289008.04, 90)]
MAT = {"2023": 17.7, "2024": 17.9, "2025": 16.6, "Q1 2026 (provv.)": 16.5}  # materiale medico % ricavi
W25 = 1046051.96 / 365 * 7
BREAKEVEN = W25 * 0.875  # stima: margine di sicurezza ~12,5% (analisi bilanci 2025)
TARGET = 289008.04 / 90 * 7  # ritmo Q1 2026

def eur(x): return ("-" if round(x) < 0 else "") + "€ " + f"{abs(x):,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
def pct(x):
    x = round(x, 1) + 0.0
    return ("+" if x > 0 else "") + f"{x:.1f}".replace(".", ",") + "%"
def dlt(a, b): return (a - b) / b * 100 if b else 0.0
def col(x): return "#1e8e3e" if x >= 0 else "#c5221f"

days = sorted(D["days"], key=lambda r: r["d"])
weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
cur, prev = weeks[-1], weeks[-2]
tc, tp = sum(r["r"] for r in cur), sum(r["r"] for r in prev)
nc, npv = sum(r["n"] for r in cur), sum(r["n"] for r in prev)
wk_tot = [sum(r["r"] for r in w) for w in weeks]
_s = sorted(wk_tot); avg4 = (_s[len(_s)//2] + _s[(len(_s)-1)//2]) / 2  # mediana: robusta a picchi
tkc, tkp = (tc / nc if nc else 0), (tp / npv if npv else 0)
pcc, pcp = D["pc_cur"], D["pc_prev"]
names = sorted(set(pcc) | set(pcp), key=lambda k: (-pcc.get(k, [0, 0])[0], -pcp.get(k, [0, 0])[0], k))
rank = [k for k in names if pcc.get(k, [0])[0] > 0]
best = rank[0] if rank else "-"
best_real = next((k for k in rank if k.upper() not in ("GENERICO", "NON ASSEGNATO")), best)
gen_share = pcc.get("GENERICO", [0])[0] / tc * 100 if tc else 0
drug_share = (pcc.get("FARMACI", [0])[0] + pcc.get("PARAFARMACI", [0])[0]) / tc * 100 if tc else 0
GG = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
if tc >= TARGET: stato, sc = "OTTIMO - sopra il ritmo del Q1 2026", "#1e8e3e"
elif tc >= W25: stato, sc = "BENE - sopra la media settimanale 2025", "#1e8e3e"
elif tc >= BREAKEVEN: stato, sc = "ATTENZIONE - sotto la media 2025 ma sopra il pareggio stimato", "#e37400"
else: stato, sc = "CRITICO - sotto il punto di pareggio stimato", "#c5221f"

S = []
S.append(f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Report fatturato {D['week_start']}</title><style>
body{{font-family:Calibri,Arial,Helvetica,sans-serif;color:#2B2B2B;background:#fff;margin:0;padding:16px}}
.w{{max-width:900px;margin:auto}}h1{{color:{BLU};margin:0;font-size:24px}}h2{{color:{BLU};border-bottom:2px solid {BLU};padding-bottom:4px;margin-top:28px;font-size:18px}}
.sub{{color:#666;font-size:14px}}.k{{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}}
.t{{flex:1 1 150px;border:1px solid {BLU};border-radius:8px;padding:10px}}.t b{{display:block;font-size:22px}}.t span{{font-size:12px;color:#666}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th{{background:{BLU};color:#fff;padding:6px;text-align:left}}td{{padding:5px 6px}}
tr:nth-child(even) td{{background:#F2F4F8}}.r{{text-align:right}}.bar{{background:{BLU};height:10px;border-radius:3px}}
.box{{background:#F2F4F8;border-left:4px solid {BLU};padding:10px 14px;margin:10px 0}}.st{{color:#fff;padding:10px 14px;border-radius:8px;font-weight:bold}}
li{{margin-bottom:6px}}.f{{margin-top:30px;border-top:1px solid {BLU};padding-top:8px;font-size:11px;color:#777}}
</style></head><body><div class="w">
<h1>Clinica Veterinaria Tergeste — Report settimanale fatturato</h1>
<div class="sub">Settimana {D['week_start']} → {D['week_end']} · generato il {dt.date.today().isoformat()} · fonte: gestionale Snoots (imponibile, IVA esclusa)</div>
<div class="st" style="background:{sc};margin-top:14px">Stato settimana: {stato}</div>
<div class="k">
<div class="t"><span>Fatturato settimana</span><b>{eur(tc)}</b><span style="color:{col(tc-tp)}">{pct(dlt(tc,tp))} vs sett. prec. ({eur(tp)})</span></div>
<div class="t"><span>Mediana ultime 4 settimane</span><b>{eur(avg4)}</b><span style="color:{col(tc-avg4)}">{pct(dlt(tc,avg4))} questa settimana</span></div>
<div class="t"><span>Documenti emessi</span><b>{nc:.0f}</b><span>{npv:.0f} sett. prec. ({pct(dlt(nc,npv))})</span></div>
<div class="t"><span>Scontrino medio</span><b>{eur(tkc)}</b><span style="color:{col(tkc-tkp)}">{pct(dlt(tkc,tkp))} vs {eur(tkp)}</span></div>
<div class="t"><span>Centro di ricavo migliore</span><b style="font-size:18px">{best_real}</b><span>{eur(pcc.get(best_real,[0])[0])}</span></div>
</div>""")

# Giornaliero
mx = max([r["r"] for r in cur + prev] + [1])
S.append("<h2>1. Andamento giornaliero</h2><table><tr><th>Giorno</th><th class=r>Questa sett.</th><th class=r>Sett. prec.</th><th class=r>Δ</th><th style='width:35%'></th></tr>")
for i, (a, b) in enumerate(zip(cur, prev)):
    S.append(f"<tr><td>{GG[i]} {a['d'][8:]}/{a['d'][5:7]}</td><td class=r>{eur(a['r'])}</td><td class=r>{eur(b['r'])}</td><td class=r style='color:{col(a['r']-b['r'])}'>{pct(dlt(a['r'],b['r']))}</td><td><div class=bar style='width:{a['r']/mx*100:.0f}%'></div></td></tr>")
S.append("</table>")

# Centri di ricavo
S.append(f"<h2>2. Centri di ricavo — classifica per fatturato</h2><div class=box>Il centro con il fatturato più alto è <b>{best}</b>" + (f"; escludendo le voci non classificate, il migliore è <b>{best_real}</b>." if best != best_real else ".") + "</div>")
S.append("<table><tr><th>#</th><th>Centro</th><th class=r>Fatturato</th><th class=r>% tot.</th><th class=r>Sett. prec.</th><th class=r>Δ €</th><th class=r>Δ %</th><th style='width:20%'></th></tr>")
m2 = max([pcc.get(k, [0])[0] for k in names] + [1])
for i, k in enumerate(names, 1):
    a = pcc.get(k, [0, 0])[0]; b = pcp.get(k, [0, 0])[0]
    dp = pct(dlt(a, b)) if b else ("nuovo" if a else "-")
    S.append(f"<tr><td>{i}</td><td>{k}</td><td class=r>{eur(a)}</td><td class=r>{pct(a/tc*100 if tc else 0).lstrip('+')}</td><td class=r>{eur(b)}</td><td class=r style='color:{col(a-b)}'>{'+' if a-b>0 else ''}{eur(a-b)}</td><td class=r style='color:{col(a-b)}'>{dp}</td><td><div class=bar style='width:{a/m2*100:.0f}%'></div></td></tr>")
S.append("</table>")
up = sorted(names, key=lambda k: -(pcc.get(k, [0])[0] - pcp.get(k, [0])[0]))
S.append(f"<p>Crescita maggiore: <b>{up[0]}</b> ({'+' if pcc.get(up[0],[0])[0]-pcp.get(up[0],[0])[0]>0 else ''}{eur(pcc.get(up[0],[0])[0]-pcp.get(up[0],[0])[0])}). Calo maggiore: <b>{up[-1]}</b> ({eur(pcc.get(up[-1],[0])[0]-pcp.get(up[-1],[0])[0])}).</p>")

# Bilanci
S.append("<h2>3. Confronto con i bilanci</h2><table><tr><th>Periodo</th><th class=r>Ricavi</th><th class=r>Media settimanale</th><th class=r>Questa sett. vs media</th><th class=r>Materiale medico % ricavi</th></tr>")
for lab, rv, g in BIL:
    w = rv / g * 7
    S.append(f"<tr><td>{lab}</td><td class=r>{eur(rv)}</td><td class=r>{eur(w)}</td><td class=r style='color:{col(tc-w)}'>{pct(dlt(tc,w))}</td><td class=r>{str(MAT[lab]).replace('.',',')}%</td></tr>")
S.append(f"""</table><div class=box>Punto di pareggio settimanale stimato: <b>{eur(BREAKEVEN)}</b> (media 2025 meno il margine di sicurezza ~12,5%).
Ritmo del Q1 2026: <b>{eur(TARGET)}</b>/settimana. Questa settimana: <b>{eur(tc)}</b> → margine sul pareggio {pct(dlt(tc,BREAKEVEN))}.<br>
Ricordiamo dai bilanci: EBITDA ~9,5–10% nel 2024–2025 (benchmark settore 12–22%), utile netto ~2,5–2,8% (obiettivo 8–15%), materiale medico costantemente sopra la soglia del 16%.</div>""")

# Va bene / migliorare
good, bad = [], []
(good if tc >= tp else bad).append(f"Fatturato {pct(dlt(tc,tp))} rispetto alla settimana precedente.")
(good if tc >= W25 else bad).append(f"Rispetto alla media settimanale 2025 ({eur(W25)}): {pct(dlt(tc,W25))}.")
(good if tkc >= tkp else bad).append(f"Scontrino medio {eur(tkc)} ({pct(dlt(tkc,tkp))}).")
if gen_share > 15: bad.append(f"Il {gen_share:.0f}% del fatturato è nel centro GENERICO: prestazioni non classificate, l'analisi per reparto è meno precisa.")
else: good.append(f"Solo il {gen_share:.0f}% del fatturato è non classificato (GENERICO).")
if drug_share: (bad if drug_share < 16 else good).append(f"Farmaci + parafarmaci = {drug_share:.1f}% del fatturato".replace(".", ",") + ": il costo del materiale medico storico è il 16–18% dei ricavi. Verificare ricarichi e consumi interni non addebitati.")
we = cur[5]["r"] + cur[6]["r"]
bad.append(f"Weekend: {eur(we)} ({we/tc*100 if tc else 0:.0f}% della settimana) — verificare la copertura costi dei turni h24.") if tc and we / tc < 0.12 else good.append(f"Weekend: {eur(we)} ({we/tc*100:.0f}% della settimana).")
S.append("<h2>4. Cosa va bene e cosa migliorare</h2><table><tr><th style='width:50%'>✅ Va bene</th><th>⚠️ Da migliorare</th></tr><tr><td valign=top><ul>" + "".join(f"<li>{x}</li>" for x in good) + "</ul></td><td valign=top><ul>" + "".join(f"<li>{x}</li>" for x in bad) + "</ul></td></tr></table>")
S.append("<h2>5. Idee e punti di miglioramento</h2><ol>" + "".join(f"<li>{x}</li>" for x in D.get("ideas", [])) + "</ol>")
S.append("""<div class=f>Note: dati Snoots = imponibile netto IVA, sede principale (Trieste; include Muggia se fatturata sullo stesso gestionale). I bilanci riportano i ricavi contabili: il confronto è indicativo. Q1 2026 è provvisorio. I centri di ricavo su Snoots sono attivi da settembre 2026.<br>
Clinica Veterinaria Tergeste — Trieste · Muggia — clinicaveterinariatergeste@gmail.com — P.IVA 00995740321</div></div></body></html>""")
# File solo ASCII: ogni carattere speciale (€, à, è, —, →, Δ, ✅...) diventa un'entità HTML (&#8364; ...),
# così si vede correttamente con qualsiasi programma e non può trasformarsi in "?".
import re; open(OUT, "w", encoding="ascii", errors="xmlcharrefreplace").write(re.sub(r"\n\s*", "\n", "\n".join(S)))
print(json.dumps({"tot": round(tc, 2), "prev": round(tp, 2), "delta_pct": round(dlt(tc, tp), 1), "avg4": round(avg4, 2), "docs": nc, "ticket": round(tkc, 2), "ticket_prev": round(tkp, 2),
                  "stato": stato, "best": best, "best_real": best_real, "generico_pct": round(gen_share, 1), "farmaci_pct": round(drug_share, 1),
                  "ranking": [(k, round(pcc.get(k, [0])[0]), round(pcp.get(k, [0])[0])) for k in names], "good": good, "bad": bad}, ensure_ascii=False))
