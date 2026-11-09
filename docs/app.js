// Agenda Familles Berne : affichage de docs/events.json (onglet « Agenda »).
// - En haut : le bandeau de période (aujourd'hui / week-end / 14 jours) et le bouton des filtres.
// - Puis la prochaine activité en grand (« Bientôt »), les suivantes en petites cartes,
//   les offres régulières (repliables) et la liste par jour.
// - En bas : les onglets Agenda / Sortir. L'onglet « Sortir » (lieux ouverts) est dans sortir.js.
// Tous les textes viennent de textes_fr.json (traduction allemande prévue plus tard).

const LANGUE = "fr";
let T = {}; // textes de l'interface

// ---------------------------------------------------------------------------
// Petits outils
// ---------------------------------------------------------------------------

// Remplace {n}, {age}… dans un texte
function remplir(texte, valeurs = {}) {
  return texte.replace(/\{(\w+)\}/g, (_, cle) => valeurs[cle]);
}

// En français, 0 et 1 s'accordent au singulier : « 1 activité régulière »
function accorder(texte, n) {
  return n <= 1 ? texte.replace(/activités/g, "activité").replace(/régulières/g, "régulière") : texte;
}

// Crée un élément avec une classe et un texte (jamais interprété comme du HTML)
function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined && texte !== null) e.textContent = texte;
  return e;
}

// Petites icônes d'interface, dessinées au même trait
const ICONES = {
  lieu: '<path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0C18.5 15.4 12 21 12 21z"/><circle cx="12" cy="10" r="2.3"/>',
  filtres: '<path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2.2"/><circle cx="10" cy="17" r="2.2"/>',
  fleche: '<path d="M9 6l6 6-6 6"/>',
  externe: '<path d="M14 5h5v5M19 5l-8 8M18 14v4a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h4"/>',
  fermer: '<path d="M6 6l12 12M18 6L6 18"/>',
  alerte: '<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17v.5"/>',
  etoile: '<path d="M12 3.6l2.6 5.3 5.8.8-4.2 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z"/>',
  agenda: '<rect x="4" y="5" width="16" height="15" rx="2.5"/><path d="M4 10h16M9 3v4M15 3v4M12 13v4M10 15h4"/>',
  partager: '<path d="M12 4v11M8 8l4-4 4 4"/><path d="M6 12v6a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-6"/>',
  // Onglet « Sortir » : une boussole
  sortir: '<circle cx="12" cy="12" r="8.5"/><path d="M15.2 8.8l-2 4.4-4.4 2 2-4.4z"/>',
  // Météo
  soleil: '<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"/>',
  nuage: '<path d="M7.5 18h9.5a4 4 0 0 0 .4-8A5.5 5.5 0 0 0 6.9 11.2 3.4 3.4 0 0 0 7.5 18z"/>',
  eclaircie: '<path d="M9 4.5v1.3M4.2 9H5.5M5.6 5.6l.9.9M12.4 5.6l-.9.9"/><path d="M6.6 10.6A3 3 0 0 1 11.7 8"/><path d="M9.5 19h8a3.5 3.5 0 0 0 .3-7 4.8 4.8 0 0 0-9.1 1.1 3 3 0 0 0 .8 5.9z"/>',
  pluie: '<path d="M7.5 15h9.5a4 4 0 0 0 .4-8A5.5 5.5 0 0 0 6.9 8.2 3.4 3.4 0 0 0 7.5 15z"/><path d="M8.5 18l-1 2.5M12.5 18l-1 2.5M16.5 18l-1 2.5"/>',
  neige: '<path d="M7.5 14h9.5a4 4 0 0 0 .4-8A5.5 5.5 0 0 0 6.9 7.2 3.4 3.4 0 0 0 7.5 14z"/><path d="M8 18.5h.01M12 20h.01M16 18.5h.01M10 21.5h.01M14 21.5h.01" stroke-width="2.6"/>',
  brouillard: '<path d="M4 9h16M6 13h12M4 17h16"/>',
  // Équipements des lieux
  cafe: '<path d="M5 9h11v5a5 5 0 0 1-5 5h-1a5 5 0 0 1-5-5z"/><path d="M16 10.5h1.5a2.5 2.5 0 0 1 0 5H16M8.5 3.5c-.8 1 .8 2 0 3M12 3.5c-.8 1 .8 2 0 3"/>',
  langer: '<rect x="3" y="13" width="18" height="5" rx="2.5"/><circle cx="7.5" cy="9.5" r="2.3"/><path d="M11 11h7.5"/>',
  poussette: '<path d="M4 5h2.2l2.4 9h9.2l2-6.5H7.4"/><circle cx="9.5" cy="18.5" r="1.6"/><circle cx="16.5" cy="18.5" r="1.6"/>',
  wc: '<path d="M5 4h14M7 4v6h10V4M8 10v3a4 4 0 0 0 8 0v-3M10 17l-1 3h6l-1-3"/>',
  jeux: '<path d="M5 20V6M10 20V6M5 10h5M5 15h5M4 6h7"/><path d="M10 7c4 0 5 4 6.5 8S19 19 21 19"/>',
};
function icone(nom) {
  const s = el("span", "icone");
  s.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">${ICONES[nom]}</svg>`;
  return s;
}

// Dates : "2026-11-08T16:00" est déjà à l'heure de Berne
const lireDate = (iso) => new Date(iso);
const cleJour = (iso) => iso.slice(0, 10);
const formatJour = (d) => d.toLocaleDateString("sv-SE"); // AAAA-MM-JJ
const heure = (iso) => lireDate(iso).toLocaleTimeString(LANGUE, { hour: "2-digit", minute: "2-digit" });

function titreJour(cle) {
  const auj = new Date();
  const dem = new Date(); dem.setDate(auj.getDate() + 1);
  const date = lireDate(cle + "T12:00").toLocaleDateString(LANGUE, { weekday: "long", day: "numeric", month: "long" });
  if (cle === formatJour(auj)) return { principal: T.aujourd_hui, secondaire: date };
  if (cle === formatJour(dem)) return { principal: T.demain, secondaire: date };
  return { principal: date, secondaire: "" };
}

// « Dans 40 min », « En cours », « Demain 10:15 », « mer. 14:15 »
function quand(e, maintenant = new Date()) {
  const debut = lireDate(e.debut);
  const fin = e.fin ? lireDate(e.fin) : new Date(debut.getTime() + 2 * 3600e3);
  if (debut <= maintenant && maintenant < fin) return { texte: T.en_cours, proche: true };
  const minutes = Math.round((debut - maintenant) / 60000);
  const memeJour = formatJour(debut) === formatJour(maintenant);
  if (memeJour && minutes < 60) return { texte: remplir(T.dans_min, { n: Math.max(1, minutes) }), proche: true };
  if (memeJour) {
    const h = Math.floor(minutes / 60), m = minutes % 60;
    const texte = h < 3 && m >= 5 ? remplir(T.dans_h_min, { h, m: String(m).padStart(2, "0") }) : remplir(T.dans_h, { h });
    return { texte, proche: h < 3 };
  }
  const demain = new Date(maintenant); demain.setDate(maintenant.getDate() + 1);
  if (formatJour(debut) === formatJour(demain)) return { texte: remplir(T.demain_a, { heure: heure(e.debut) }), proche: false };
  const jour = debut.toLocaleDateString(LANGUE, { weekday: "short" });
  return { texte: remplir(T.jour_a, { jour, heure: heure(e.debut) }), proche: false };
}

// 0.5 -> "6 mois" ; 4 -> "4 ans"
function duree(age) {
  if (age < 1) return remplir(T.mois, { n: Math.round(age * 12) });
  return remplir(age === 1 ? T.an : T.ans, { n: String(age).replace(".", ",") });
}

function texteAge(e) {
  // « dès 0 an » ne dit rien : un âge minimum de 0 compte comme « pas de minimum »
  const min = e.age_min ? e.age_min : null, max = e.age_max;
  let texte;
  if (min != null && max != null) texte = min >= 1 ? `${min}–${duree(max)}` : `${duree(min)} – ${duree(max)}`;
  else if (min != null) texte = remplir(T.age_des, { age: duree(min) });
  else if (max != null) texte = remplir(T.age_jusqu_a, { age: duree(max) });
  else return e.age_texte || null; // âge pas compris : le texte de la source
  if (e.age_source === "déduit") texte += " " + T.age_deduit;
  return texte;
}

function textePrix(prix) {
  if (prix === "gratuit") return T.gratuit;
  if (!prix || prix === "inconnu") return null;
  return prix;
}

// ---------------------------------------------------------------------------
// Filtres (mémorisés dans le navigateur)
// ---------------------------------------------------------------------------

// Onglet affiché : "agenda" ou "sortir" (gardé dans l'adresse : …/#sortir)
let onglet = location.hash === "#sortir" ? "sortir" : "agenda";

// ages : âges des enfants (ex. [2, 5]) ; moments : matin / apres_midi / soir ; favoris : seulement les favoris
const FILTRES_DEFAUT = { periode: "14_jours", prix: "tous", types: [], ages: [], moments: [], favoris: false };
let filtres = { ...FILTRES_DEFAUT };
let donnees = null;

// Favoris : identifiants des activités marquées d'une étoile, gardés sur ce téléphone
let favoris = new Set();
function chargerFavoris() {
  try { favoris = new Set(JSON.parse(localStorage.getItem("agenda-favoris")) || []); } catch (_) { favoris = new Set(); }
}
function basculerFavori(id) {
  if (favoris.has(id)) favoris.delete(id); else favoris.add(id);
  try { localStorage.setItem("agenda-favoris", JSON.stringify([...favoris])); } catch (_) { /* stockage indisponible */ }
  return favoris.has(id);
}

// Moment de la journée d'une séance
function momentDe(e) {
  const h = lireDate(e.debut).getHours();
  return h < 12 ? "matin" : h < 17 ? "apres_midi" : "soir";
}

// Vrai si l'activité convient à au moins un des âges choisis (âge inconnu : on garde)
function convientAuxAges(e) {
  if (!filtres.ages.length) return true;
  if (e.age_min == null && e.age_max == null) return true;
  return filtres.ages.some((a) => (e.age_min == null || a >= e.age_min) && (e.age_max == null || a <= e.age_max));
}

function chargerFiltres() {
  try {
    const memo = JSON.parse(localStorage.getItem("agenda-filtres"));
    if (memo) filtres = { ...FILTRES_DEFAUT, ...memo };
  } catch (_) { /* stockage indisponible : choix par défaut */ }
}
function sauverFiltres() {
  try { localStorage.setItem("agenda-filtres", JSON.stringify(filtres)); } catch (_) { /* idem */ }
}

function joursDeLaPeriode(periode) {
  const auj = new Date();
  if (periode === "aujourd_hui") return [formatJour(auj)];
  if (periode === "weekend") {
    const j = auj.getDay(); // 0 = dimanche, 6 = samedi
    if (j === 0) return [formatJour(auj)];
    const sam = new Date(auj); sam.setDate(auj.getDate() + (6 - j));
    const dim = new Date(sam); dim.setDate(sam.getDate() + 1);
    return [formatJour(sam), formatJour(dim)];
  }
  return null;
}

// Filtres de la feuille (prix, type, âges, favoris), sans la période.
// Le moment de la journée ne s'applique qu'aux séances datées (pas aux offres régulières).
function passePrixType(e, avecMoment = true) {
  if (filtres.prix === "gratuit" && e.prix !== "gratuit") return false;
  if (filtres.prix === "payant" && (e.prix === "gratuit" || !e.prix || e.prix === "inconnu")) return false;
  if (filtres.types.length && !filtres.types.includes(e.categorie)) return false;
  if (!convientAuxAges(e)) return false;
  if (filtres.favoris && !favoris.has(e.id)) return false;
  if (avecMoment && filtres.moments.length && !filtres.moments.includes(momentDe(e))) return false;
  return true;
}

function evenementsFiltres() {
  const jours = joursDeLaPeriode(filtres.periode);
  const maintenant = new Date();
  return donnees.evenements.filter((e) => {
    const fin = e.fin ? lireDate(e.fin) : new Date(lireDate(e.debut).getTime() + 2 * 3600e3);
    if (fin < maintenant) return false; // déjà fini depuis la dernière mise à jour
    if (jours && !jours.includes(cleJour(e.debut))) return false;
    return passePrixType(e);
  })
    // Toujours dans l'ordre chronologique, même si le fichier ne l'était pas
    .sort((a, b) => a.debut.localeCompare(b.debut));
}

// Regroupe les séances d'une même activité (même titre, même source), dans l'ordre de la première.
// Pas par lien : certains sites (Schlachthaus) donnent un lien différent à chaque séance.
function regrouperSeances(evenements) {
  const groupes = new Map();
  for (const e of evenements) {
    const cle = `${e.titre}|${e.source}`;
    if (!groupes.has(cle)) groupes.set(cle, []);
    groupes.get(cle).push(e);
  }
  return [...groupes.values()];
}

// « mer. 11 · 15:00 »
function dateCourte(e) {
  const d = lireDate(e.debut);
  return `${d.toLocaleDateString(LANGUE, { weekday: "short", day: "numeric" })} · ${heure(e.debut)}`;
}

// Ligne « Autres dates : mer. 11 · 15:00, sam. 14 · 15:00 +3 » (null s'il n'y en a pas)
function autresDates(seances, maximum, avecTitre) {
  const reste = seances.slice(1);
  if (!reste.length) return null;
  const p = el("p", "autres-dates");
  if (avecTitre) p.append(el("strong", null, `${T.autres_dates} : `));
  p.append(reste.slice(0, maximum).map(dateCourte).join(", "));
  if (reste.length > maximum) p.append(" ", el("span", "plus-n", remplir(T.plus_n, { n: reste.length - maximum })));
  return p;
}

// ---------------------------------------------------------------------------
// Morceaux de fiche
// ---------------------------------------------------------------------------

function pastilles(e) {
  const zone = el("div", "pastilles");
  const age = texteAge(e);
  zone.append(el("span", age ? "pastille" : "pastille pastille-vide", age || T.age_inconnu));
  if (/begleitung/i.test(e.age_texte || "")) zone.append(el("span", "pastille", T.accompagne));
  const prix = textePrix(e.prix);
  zone.append(el("span", e.prix === "gratuit" ? "pastille pastille-gratuit" : prix ? "pastille" : "pastille pastille-vide", prix || T.prix_inconnu));
  if (e.inscription_requise) zone.append(el("span", "pastille pastille-tampon", T.inscription_requise));
  return zone;
}

function ligneLieu(e) {
  const p = el("p", "lieu");
  p.append(icone("lieu"), el("span", null, e.lieu_nom));
  return p;
}

function lienSource(e) {
  if (!e.url_source) return el("p", "source-texte", e.source);
  const a = el("a", "lien-source");
  a.href = e.url_source; a.target = "_blank"; a.rel = "noopener";
  a.append(el("span", null, remplir(T.voir_source, { source: e.source })), icone("externe"));
  return a;
}

function autresSources(e) {
  if (!e.autres_sources || !e.autres_sources.length) return null;
  const p = el("p", "autres-sources", T.aussi_sur + " ");
  e.autres_sources.forEach((s, i) => {
    const a = el("a", null, s.source);
    a.href = s.url_source; a.target = "_blank"; a.rel = "noopener";
    if (i) p.append(", ");
    p.append(a);
  });
  return p;
}

// ---------------------------------------------------------------------------
// Actions d'une fiche : favori, agenda, partage
// ---------------------------------------------------------------------------

// Fuseau de Berne décrit dans le fichier, pour que les agendas placent l'heure juste
const VTIMEZONE_ZURICH = [
  "BEGIN:VTIMEZONE", "TZID:Europe/Zurich",
  "BEGIN:DAYLIGHT", "TZOFFSETFROM:+0100", "TZOFFSETTO:+0200", "TZNAME:CEST",
  "DTSTART:19700329T020000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU", "END:DAYLIGHT",
  "BEGIN:STANDARD", "TZOFFSETFROM:+0200", "TZOFFSETTO:+0100", "TZNAME:CET",
  "DTSTART:19701025T030000", "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU", "END:STANDARD",
  "END:VTIMEZONE",
];

// "2026-11-11T15:00" -> "20261111T150000" (heure de Berne)
const dateIcs = (iso) => iso.replace(/[-:]/g, "").slice(0, 13) + "00";

// Fin d'une séance : l'heure de fin, sinon une heure après le début
function finOuUneHeure(e) {
  if (e.fin) return e.fin;
  const d = lireDate(e.debut); d.setHours(d.getHours() + 1);
  return `${formatJour(d)}T${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function texteIcs(t) {
  return (t || "").replace(/\\/g, "\\\\").replace(/\n/g, "\\n").replace(/[,;]/g, (c) => "\\" + c);
}

function fichierIcs(e) {
  const lignes = [
    "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Agenda Familles Berne//FR", "CALSCALE:GREGORIAN",
    ...VTIMEZONE_ZURICH,
    "BEGIN:VEVENT",
    `UID:${e.id}@agenda-familles-berne`,
    `DTSTAMP:${new Date().toISOString().replace(/[-:]/g, "").slice(0, 15)}Z`,
    `DTSTART;TZID=Europe/Zurich:${dateIcs(e.debut)}`,
    `DTEND;TZID=Europe/Zurich:${dateIcs(finOuUneHeure(e))}`,
    `SUMMARY:${texteIcs(e.titre)}`,
    `LOCATION:${texteIcs([e.lieu_nom, e.adresse].filter(Boolean).join(", "))}`,
    `DESCRIPTION:${texteIcs([e.description_courte, e.url_source].filter(Boolean).join("\n"))}`,
    e.url_source ? `URL:${e.url_source}` : null,
    "END:VEVENT", "END:VCALENDAR",
  ].filter(Boolean);
  return lignes.join("\r\n");
}

function telechargerIcs(e) {
  const blob = new Blob([fichierIcs(e)], { type: "text/calendar;charset=utf-8" });
  const a = el("a");
  a.href = URL.createObjectURL(blob);
  a.download = `${e.titre.replace(/[^\p{L}\p{N}]+/gu, "-").slice(0, 40)}.ics`;
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}

function lienGoogleAgenda(e) {
  const p = new URLSearchParams({
    action: "TEMPLATE", text: e.titre, ctz: "Europe/Zurich",
    dates: `${dateIcs(e.debut)}/${dateIcs(finOuUneHeure(e))}`,
    location: [e.lieu_nom, e.adresse].filter(Boolean).join(", "),
    details: [e.description_courte, e.url_source].filter(Boolean).join("\n\n"),
  });
  return `https://calendar.google.com/calendar/render?${p}`;
}

// Petit message temporaire en bas de l'écran (« Lien copié »…)
function message(texte) {
  document.querySelector(".toast")?.remove();
  const t = el("div", "toast", texte);
  t.setAttribute("role", "status");
  document.body.append(t);
  setTimeout(() => t.remove(), 2600);
}

async function partager(e) {
  const quandTexte = e.type === "offre régulière" ? e.repetition : dateCourte(e);
  const texte = `${e.titre} — ${quandTexte}, ${e.lieu_nom}`;
  if (navigator.share) {
    try { await navigator.share({ title: e.titre, text: texte, url: e.url_source || location.href }); } catch (_) { /* annulé */ }
    return;
  }
  try { await navigator.clipboard.writeText(`${texte}\n${e.url_source || location.href}`); message(T.lien_copie); }
  catch (_) { message(T.partage_impossible); }
}

function boutonAction(nomIcone, texte, auClic) {
  const b = el("button", "action");
  b.type = "button";
  b.append(icone(nomIcone), el("span", null, texte));
  b.addEventListener("click", (ev) => { ev.stopPropagation(); auClic(b); });
  return b;
}

function actions(e) {
  const zone = el("div", "actions");
  const fav = boutonAction("etoile", favoris.has(e.id) ? T.favori_oui : T.favori, (b) => {
    const actif = basculerFavori(e.id);
    b.setAttribute("aria-pressed", String(actif));
    b.querySelector("span:last-child").textContent = actif ? T.favori_oui : T.favori;
    document.querySelectorAll(`[data-id="${CSS.escape(e.id)}"]`).forEach((x) => x.classList.toggle("est-favori", actif));
    message(actif ? T.favori_ajoute : T.favori_retire);
  });
  fav.classList.add("action-favori");
  fav.setAttribute("aria-pressed", String(favoris.has(e.id)));
  zone.append(fav);
  if (e.type !== "offre régulière") {
    zone.append(boutonAction("agenda", T.agenda, () => telechargerIcs(e)));
    const g = el("a", "action-lien", T.google_agenda);
    g.href = lienGoogleAgenda(e); g.target = "_blank"; g.rel = "noopener";
    zone.append(g);
  }
  zone.append(boutonAction("partager", T.partager, () => partager(e)));
  return zone;
}

// ---------------------------------------------------------------------------
// « Bientôt » : la prochaine activité en grand + les suivantes
// ---------------------------------------------------------------------------

// Grande carte : la prochaine séance d'une activité, et ses autres dates
function carteVedette(seances) {
  const e = seances[0];
  const carte = el("article", "vedette");
  carte.dataset.cat = cleIllustration(e.categorie);
  const visuel = el("div", "vedette-visuel");
  visuel.append(illustration(e.categorie));
  const q = quand(e);
  const badge = el("span", q.proche ? "quand quand-proche" : "quand", q.texte);
  badge.dataset.debut = e.debut; badge.dataset.fin = e.fin || "";
  visuel.append(badge);
  carte.append(visuel);

  const corps = el("div", "vedette-corps");
  const haut = el("p", "vedette-haut");
  haut.append(el("span", "heure", e.fin ? `${heure(e.debut)} – ${heure(e.fin)}` : heure(e.debut)));
  if (e.categorie) haut.append(el("span", "type", T.categories[e.categorie]));
  corps.append(haut, el("h2", "vedette-titre", e.titre));
  if (e.description_courte) corps.append(el("p", "vedette-texte", e.description_courte));
  const dates = autresDates(seances, 4, true);
  if (dates) corps.append(dates);
  corps.append(ligneLieu(e), pastilles(e), lienSource(e), actions(e));
  const autres = autresSources(e);
  if (autres) corps.append(autres);
  carte.append(corps);
  return carte;
}

// Petite carte : une par activité, avec la prochaine séance et quelques dates suivantes
function petiteCarte(seances) {
  const e = seances[0];
  const carte = el("a", "mini");
  carte.dataset.cat = cleIllustration(e.categorie);
  carte.href = `#${e.id}`;
  carte.addEventListener("click", (ev) => { ev.preventDefault(); ouvrirLigne(e.id); });
  const visuel = el("div", "mini-visuel");
  visuel.append(illustration(e.categorie));
  carte.append(visuel);
  const q = quand(e);
  const badge = el("span", q.proche ? "quand quand-proche" : "quand", q.texte);
  badge.dataset.debut = e.debut; badge.dataset.fin = e.fin || "";
  carte.append(badge, el("h3", "mini-titre", e.titre), el("p", "mini-lieu", e.lieu_nom));
  const dates = autresDates(seances, 3, false);
  if (dates) carte.append(dates);
  return carte;
}

function sectionBientot(evenements) {
  if (!evenements.length) return null;
  // Une seule carte par activité, même si elle a plusieurs séances (ex. un spectacle)
  const groupes = regrouperSeances(evenements);
  const section = el("section", "bientot");
  const premier = groupes[0][0];
  const aujourdhui = cleJour(premier.debut) === formatJour(new Date());
  section.append(el("h2", "section-titre", aujourdhui ? T.bientot : T.prochaine));
  section.append(carteVedette(groupes[0]));
  const suivants = groupes.slice(1, 6);
  if (suivants.length) {
    const rang = el("div", "rangee");
    rang.setAttribute("role", "list");
    suivants.forEach((g) => { const c = petiteCarte(g); c.setAttribute("role", "listitem"); rang.append(c); });
    section.append(rang);
  }
  return section;
}

// ---------------------------------------------------------------------------
// Offres régulières et liste par jour
// ---------------------------------------------------------------------------

function sectionReguliere(offres) {
  if (!offres.length) return null;
  const bloc = el("details", "reguliers");
  const resume = el("summary", "reguliers-resume");
  const pile = el("span", "pile");
  // Une illustration par type différent (pas trois fois la même)
  [...new Set(offres.map((o) => cleIllustration(o.categorie)))].slice(0, 3)
    .forEach((c) => pile.append(illustration(c === "fete" ? "fête" : c)));
  const textes = el("span", "reguliers-textes");
  textes.append(el("strong", null, T.chaque_semaine), el("span", null, accorder(remplir(T.chaque_semaine_aide, { n: offres.length }), offres.length)));
  resume.append(pile, textes, icone("fleche"));
  bloc.append(resume);
  const liste = el("div", "groupe");
  offres.forEach((o) => liste.append(ligne(o, true)));
  bloc.append(liste);
  return bloc;
}

// Une ligne de la liste ; un toucher déplie le détail
function ligne(e, reguliere = false) {
  const item = el("article", favoris.has(e.id) ? "ligne est-favori" : "ligne");
  item.dataset.id = e.id;  // permet de mettre à jour l'étoile partout quand on change un favori
  item.id = e.id;
  item.dataset.cat = cleIllustration(e.categorie);
  const bouton = el("button", "ligne-bouton");
  bouton.type = "button";
  bouton.setAttribute("aria-expanded", "false");
  const vignette = el("span", "vignette");
  vignette.append(illustration(e.categorie));
  const textes = el("span", "ligne-textes");
  const haut = el("span", "ligne-haut");
  haut.append(el("span", "heure", reguliere ? e.repetition : (e.fin ? `${heure(e.debut)} – ${heure(e.fin)}` : heure(e.debut))));
  if (e.categorie) haut.append(el("span", "type", T.categories[e.categorie]));
  const titre = el("span", "ligne-titre");
  // Petite étoile devant le titre, visible seulement si l'activité est en favori (géré par CSS)
  const marque = icone("etoile");
  marque.classList.add("marque-favori");
  titre.append(marque, el("span", null, e.titre));
  textes.append(haut, titre, el("span", "ligne-lieu", e.lieu_nom));
  bouton.append(vignette, textes, icone("fleche"));
  item.append(bouton);

  const detail = el("div", "ligne-detail");
  detail.hidden = true;
  if (e.description_courte) detail.append(el("p", "ligne-texte", e.description_courte));
  detail.append(lienSource(e), actions(e));
  const autres = autresSources(e);
  if (autres) detail.append(autres);
  item.append(detail);

  bouton.addEventListener("click", () => {
    const ouvert = bouton.getAttribute("aria-expanded") === "true";
    bouton.setAttribute("aria-expanded", String(!ouvert));
    detail.hidden = ouvert;
  });
  // Les pastilles principales restent visibles même replié
  textes.append(pastilles(e));
  return item;
}

function ouvrirLigne(id) {
  const item = document.getElementById(id);
  if (!item) return;
  const bouton = item.querySelector(".ligne-bouton");
  if (bouton.getAttribute("aria-expanded") === "false") bouton.click();
  item.scrollIntoView({ behavior: "smooth", block: "center" });
  item.classList.remove("eclaire"); void item.offsetWidth; item.classList.add("eclaire");
}

function sectionsParJour(evenements) {
  const frag = document.createDocumentFragment();
  let jourCourant = null, groupe = null;
  for (const e of evenements) {
    const cle = cleJour(e.debut);
    if (cle !== jourCourant) {
      jourCourant = cle;
      const section = el("section", "jour");
      const t = titreJour(cle);
      const h = el("h2", "jour-titre");
      h.append(el("span", null, t.principal));
      if (t.secondaire) h.append(el("span", "jour-date", t.secondaire));
      groupe = el("div", "groupe");
      section.append(h, groupe);
      frag.append(section);
    }
    groupe.append(ligne(e));
  }
  return frag;
}

// ---------------------------------------------------------------------------
// Onglets (barre du bas), bandeau de période et feuille des filtres
// ---------------------------------------------------------------------------

function afficherOnglets() {
  const barre = document.getElementById("barre");
  barre.setAttribute("aria-label", T.onglets);
  barre.replaceChildren();
  for (const [valeur, texte, nomIcone] of [["agenda", T.onglet_agenda, "agenda"], ["sortir", T.onglet_sortir, "sortir"]]) {
    const b = el("button", "onglet");
    b.type = "button";
    if (onglet === valeur) b.setAttribute("aria-current", "page");
    b.append(icone(nomIcone), el("span", null, texte));
    b.addEventListener("click", () => changerOnglet(valeur));
    barre.append(b);
  }
}

function changerOnglet(valeur) {
  if (valeur === onglet) { window.scrollTo({ top: 0, behavior: "smooth" }); return; }
  onglet = valeur;
  history.replaceState(null, "", valeur === "sortir" ? "#sortir" : location.pathname + location.search);
  window.scrollTo({ top: 0 });
  afficher();
}

// Bandeau de l'Agenda : période + bouton des filtres (reste en haut en défilant)
function afficherBandeau() {
  const barre = document.getElementById("bandeau");
  barre.setAttribute("role", "region");
  barre.setAttribute("aria-label", T.periode_et_filtres);
  barre.replaceChildren();
  const segments = el("div", "segments segments-plein");
  segments.setAttribute("role", "group");
  for (const [valeur, texte] of [["aujourd_hui", T.periode_aujourd_hui], ["weekend", T.periode_weekend], ["14_jours", T.periode_14_jours]]) {
    const b = el("button", "segment", texte);
    b.type = "button";
    b.setAttribute("aria-pressed", String(filtres.periode === valeur));
    b.addEventListener("click", () => { filtres.periode = valeur; sauverFiltres(); afficher(); window.scrollTo({ top: 0, behavior: "smooth" }); });
    segments.append(b);
  }
  const nbActifs = (filtres.prix !== "tous" ? 1 : 0) + filtres.types.length + filtres.moments.length
    + (filtres.ages.length ? 1 : 0) + (filtres.favoris ? 1 : 0);
  const bf = el("button", nbActifs ? "bouton-filtres actif" : "bouton-filtres");
  bf.type = "button";
  bf.setAttribute("aria-label", nbActifs ? `${T.filtres} (${nbActifs})` : T.filtres);
  bf.append(icone("filtres"));
  if (nbActifs) bf.append(el("span", "compte", String(nbActifs)));
  bf.addEventListener("click", ouvrirFeuille);
  barre.append(segments, bf);
}

function ouvrirFeuille() {
  const feuille = document.getElementById("feuille");
  remplirFeuille();
  feuille.showModal();
}

function remplirFeuille() {
  const feuille = document.getElementById("feuille");
  feuille.replaceChildren();
  const entete = el("div", "feuille-entete");
  entete.append(el("h2", null, T.filtres_titre));
  entete.querySelector("h2").id = "feuille-titre";
  const fermer = el("button", "bouton-icone");
  fermer.type = "button"; fermer.setAttribute("aria-label", T.fermer);
  fermer.append(icone("fermer"));
  fermer.addEventListener("click", () => feuille.close());
  entete.append(fermer);
  feuille.append(el("div", "poignee"), entete);

  // Seulement mes favoris
  const favori = el("button", "interrupteur");
  favori.type = "button";
  favori.setAttribute("role", "switch");
  favori.setAttribute("aria-checked", String(filtres.favoris));
  favori.append(icone("etoile"), el("span", null, remplir(T.seulement_favoris, { n: favoris.size })), el("span", "interrupteur-curseur"));
  favori.addEventListener("click", () => { filtres.favoris = !filtres.favoris; majFeuille(); });
  feuille.append(favori);

  // Âges de mes enfants (souvenir gardé sur le téléphone)
  feuille.append(el("h3", "feuille-sous-titre", T.filtre_ages));
  const ages = el("div", "puces-ages");
  for (let a = 0; a <= 10; a++) {
    const b = el("button", "puce-age", a === 0 ? T.moins_un_an : String(a));
    b.type = "button";
    b.setAttribute("aria-pressed", String(filtres.ages.includes(a)));
    b.setAttribute("aria-label", a === 0 ? T.moins_un_an : remplir(a === 1 ? T.an : T.ans, { n: a }));
    b.addEventListener("click", () => {
      filtres.ages = filtres.ages.includes(a) ? filtres.ages.filter((x) => x !== a) : [...filtres.ages, a].sort((x, y) => x - y);
      majFeuille();
    });
    ages.append(b);
  }
  feuille.append(ages, el("p", "aide", T.filtre_ages_aide));

  // Moment de la journée
  feuille.append(el("h3", "feuille-sous-titre", T.filtre_moment));
  const moments = el("div", "segments segments-plein");
  for (const [v, t] of [["matin", T.moment_matin], ["apres_midi", T.moment_apres_midi], ["soir", T.moment_soir]]) {
    const b = el("button", "segment", t);
    b.type = "button"; b.setAttribute("aria-pressed", String(filtres.moments.includes(v)));
    b.addEventListener("click", () => {
      filtres.moments = filtres.moments.includes(v) ? filtres.moments.filter((x) => x !== v) : [...filtres.moments, v];
      majFeuille();
    });
    moments.append(b);
  }
  feuille.append(moments);

  // Prix
  feuille.append(el("h3", "feuille-sous-titre", T.filtre_prix));
  const prix = el("div", "segments segments-plein");
  for (const [v, t] of [["tous", T.prix_tous], ["gratuit", T.prix_gratuit], ["payant", T.prix_payant]]) {
    const b = el("button", "segment", t);
    b.type = "button"; b.setAttribute("aria-pressed", String(filtres.prix === v));
    b.addEventListener("click", () => { filtres.prix = v; majFeuille(); });
    prix.append(b);
  }
  feuille.append(prix);
  if (filtres.prix === "payant") feuille.append(el("p", "aide", T.prix_payant_aide));

  // Types présents dans les données
  feuille.append(el("h3", "feuille-sous-titre", T.filtre_type));
  const presents = new Set([...donnees.evenements, ...(donnees.offres_regulieres || [])].map((e) => e.categorie));
  const types = Object.keys(T.categories).filter((c) => presents.has(c));
  filtres.types = filtres.types.filter((t) => types.includes(t));
  const grille = el("div", "types");
  for (const c of types) {
    const b = el("button", "type-choix");
    b.type = "button"; b.dataset.cat = cleIllustration(c);
    b.setAttribute("aria-pressed", String(filtres.types.includes(c)));
    b.append(illustration(c), el("span", null, T.categories[c]));
    b.addEventListener("click", () => {
      filtres.types = filtres.types.includes(c) ? filtres.types.filter((t) => t !== c) : [...filtres.types, c];
      majFeuille();
    });
    grille.append(b);
  }
  feuille.append(grille);

  // Pied : effacer + voir les résultats
  const pied = el("div", "feuille-pied");
  const effacer = el("button", "bouton-texte", T.effacer);
  effacer.type = "button";
  // Les âges des enfants sont un réglage durable : « Effacer » ne les retire pas
  effacer.addEventListener("click", () => {
    filtres.prix = "tous"; filtres.types = []; filtres.moments = []; filtres.favoris = false; majFeuille();
  });
  const n = evenementsFiltres().length;
  const voir = el("button", "bouton-action", n === 0 ? T.voir_aucun : n === 1 ? T.voir_resultat : remplir(T.voir_resultats, { n }));
  voir.type = "button";
  voir.addEventListener("click", () => feuille.close());
  pied.append(effacer, voir);
  feuille.append(pied);
}

// Après un choix dans la feuille : on enregistre, on met la page à jour derrière
function majFeuille() {
  sauverFiltres();
  remplirFeuille();
  afficher();
}

// ---------------------------------------------------------------------------
// Affichage général
// ---------------------------------------------------------------------------

function avertissements() {
  const frag = document.createDocumentFragment();
  for (const s of donnees.sources || []) {
    if (s.ok) continue;
    const texte = s.nom === "Ajouts manuels" ? T.ajouts_en_erreur : remplir(T.source_en_echec, { nom: s.nom });
    const p = el("p", "avis");
    p.append(icone("alerte"), el("span", null, texte));
    frag.append(p);
  }
  return frag;
}

function etatVide() {
  const vide = el("div", "vide");
  vide.append(illustration("autre"), el("p", "vide-titre", T.aucun_resultat), el("p", "vide-aide", T.aucun_resultat_aide));
  const b = el("button", "bouton-action", T.reinitialiser);
  b.type = "button";
  // « Tout afficher » garde les âges des enfants (réglage durable) et retire le reste
  b.addEventListener("click", () => {
    filtres = { ...FILTRES_DEFAUT, types: [], moments: [], ages: filtres.ages }; sauverFiltres(); afficher();
  });
  vide.append(b);
  return vide;
}

// Affiche l'onglet courant : en-tête, bandeau, contenu, pied de page et onglets
function afficher() {
  document.body.dataset.onglet = onglet;
  afficherOnglets();
  document.getElementById("abonnement").hidden = onglet !== "agenda";
  document.getElementById("sources").hidden = onglet !== "agenda";
  if (onglet === "sortir") { afficherSortir(); return; }  // dans sortir.js
  document.getElementById("titre-page").textContent = T.titre;
  afficherAgenda();
}

function afficherAgenda() {
  const contenu = document.getElementById("contenu");
  const evenements = evenementsFiltres();
  const offres = (donnees.offres_regulieres || []).filter((o) => passePrixType(o, false));

  const n = evenements.length;
  const cleResume = { aujourd_hui: "resume_aujourd_hui", weekend: "resume_weekend", "14_jours": "resume_14_jours" }[filtres.periode];
  document.getElementById("resume").textContent = accorder(remplir(T[cleResume], { n }), n);

  contenu.replaceChildren(avertissements());
  if (!donnees.evenements.length) {
    contenu.append(el("p", "vide-titre", T.aucun_evenement));
  } else if (!n) {
    contenu.append(etatVide());
  } else {
    contenu.append(sectionBientot(evenements));
  }
  const reg = sectionReguliere(offres);
  if (reg) contenu.append(reg);
  if (n) {
    const titre = el("h2", "section-titre section-titre-liste", T.ensuite);
    contenu.append(titre, sectionsParJour(evenements));
  }
  afficherBandeau();
  if (donnees.mis_a_jour) afficherPied();
}

// Les « Dans 40 min » se mettent à jour chaque minute, sans tout redessiner
function rafraichirQuand() {
  document.querySelectorAll(".quand[data-debut]").forEach((b) => {
    const q = quand({ debut: b.dataset.debut, fin: b.dataset.fin || null });
    b.textContent = q.texte;
    b.classList.toggle("quand-proche", q.proche);
  });
}

function afficherPied() {
  document.getElementById("pied-sortir").hidden = true;
  const maj = lireDate(donnees.mis_a_jour).toLocaleString(LANGUE, { weekday: "long", day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" });
  document.getElementById("mise-a-jour").textContent = remplir(T.mis_a_jour, { date: maj });
  const noms = (donnees.sources || []).filter((s) => s.ok && s.nom !== "Ajouts manuels").map((s) => s.nom);
  document.getElementById("sources").textContent = noms.length ? remplir(T.sources_liste, { liste: noms.join(", ") }) : "";
  // Abonnement au flux d'agenda (webcal:// ouvre directement l'agenda du téléphone)
  const flux = new URL("agenda.ics", location.href);
  const abo = el("a", "lien-abonnement");
  abo.href = flux.href.replace(/^https?:/, "webcal:");
  abo.append(icone("agenda"), el("span", null, T.abonnement));
  const aide = el("p", "aide", remplir(T.abonnement_aide, { url: flux.href }));
  document.getElementById("abonnement").replaceChildren(abo, aide);
}

async function demarrer() {
  try {
    T = await (await fetch(`textes_${LANGUE}.json`)).json();
    document.title = T.titre_page;
    document.getElementById("scene").innerHTML = SCENE_BERNE;
    document.getElementById("marque").textContent = T.marque;
    document.getElementById("titre-page").textContent = T.titre;
    document.getElementById("resume").textContent = T.chargement;
    chargerFiltres();
    chargerFavoris();
    // "no-store" : toujours la dernière version, jamais une copie en cache
    donnees = await (await fetch("events.json", { cache: "no-store" })).json();
    afficher();
    setInterval(rafraichirQuand, 60000);
    // Fermer la feuille en touchant le fond assombri
    document.getElementById("feuille").addEventListener("click", (ev) => { if (ev.target.id === "feuille") ev.target.close(); });
    // Bouton « retour » du téléphone entre #sortir et l'agenda
    window.addEventListener("hashchange", () => { onglet = location.hash === "#sortir" ? "sortir" : "agenda"; afficher(); });
  } catch (erreur) {
    console.error(erreur);
    const p = el("p", "avis");
    p.append(el("span", null, (T && T.erreur_chargement) || "Erreur de chargement."));
    document.getElementById("contenu").replaceChildren(p);
  }
}

// On attend que tous les scripts (dont sortir.js) soient chargés avant de démarrer
document.addEventListener("DOMContentLoaded", demarrer);
