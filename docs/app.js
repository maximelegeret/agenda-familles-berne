// Agenda Familles Berne : affichage de docs/events.json.
// - En haut : la prochaine activité en grand (« Bientôt »), puis les suivantes en petites cartes.
// - Ensuite : les offres régulières (repliables), puis la liste par jour.
// - En bas : la barre de période (aujourd'hui / week-end / 14 jours) et la feuille des filtres.
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

const FILTRES_DEFAUT = { periode: "14_jours", prix: "tous", types: [] };
let filtres = { ...FILTRES_DEFAUT };
let donnees = null;

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

// Filtres prix et type (sans la période)
function passePrixType(e) {
  if (filtres.prix === "gratuit" && e.prix !== "gratuit") return false;
  if (filtres.prix === "payant" && (e.prix === "gratuit" || !e.prix || e.prix === "inconnu")) return false;
  if (filtres.types.length && !filtres.types.includes(e.categorie)) return false;
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
  corps.append(ligneLieu(e), pastilles(e), lienSource(e));
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
  textes.append(el("strong", null, T.chaque_semaine), el("span", null, remplir(T.chaque_semaine_aide, { n: offres.length })));
  resume.append(pile, textes, icone("fleche"));
  bloc.append(resume);
  const liste = el("div", "groupe");
  offres.forEach((o) => liste.append(ligne(o, true)));
  bloc.append(liste);
  return bloc;
}

// Une ligne de la liste ; un toucher déplie le détail
function ligne(e, reguliere = false) {
  const item = el("article", "ligne");
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
  textes.append(haut, el("span", "ligne-titre", e.titre), el("span", "ligne-lieu", e.lieu_nom));
  bouton.append(vignette, textes, icone("fleche"));
  item.append(bouton);

  const detail = el("div", "ligne-detail");
  detail.hidden = true;
  if (e.description_courte) detail.append(el("p", "ligne-texte", e.description_courte));
  detail.append(lienSource(e));
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
// Barre du bas et feuille des filtres
// ---------------------------------------------------------------------------

function afficherBarre() {
  const barre = document.getElementById("barre");
  barre.replaceChildren();
  const segments = el("div", "segments");
  segments.setAttribute("role", "group");
  for (const [valeur, texte] of [["aujourd_hui", T.periode_aujourd_hui], ["weekend", T.periode_weekend], ["14_jours", T.periode_14_jours]]) {
    const b = el("button", "segment", texte);
    b.type = "button";
    b.setAttribute("aria-pressed", String(filtres.periode === valeur));
    b.addEventListener("click", () => { filtres.periode = valeur; sauverFiltres(); afficher(); window.scrollTo({ top: 0, behavior: "smooth" }); });
    segments.append(b);
  }
  const nbActifs = (filtres.prix !== "tous" ? 1 : 0) + filtres.types.length;
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
  effacer.addEventListener("click", () => { filtres.prix = "tous"; filtres.types = []; majFeuille(); });
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
  b.addEventListener("click", () => { filtres = { ...FILTRES_DEFAUT, types: [] }; sauverFiltres(); afficher(); });
  vide.append(b);
  return vide;
}

function afficher() {
  const contenu = document.getElementById("contenu");
  const evenements = evenementsFiltres();
  const offres = (donnees.offres_regulieres || []).filter(passePrixType);

  const n = evenements.length;
  const cleResume = { aujourd_hui: "resume_aujourd_hui", weekend: "resume_weekend", "14_jours": "resume_14_jours" }[filtres.periode];
  document.getElementById("resume").textContent = remplir(T[cleResume], { n });

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
  afficherBarre();
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
  const maj = lireDate(donnees.mis_a_jour).toLocaleString(LANGUE, { weekday: "long", day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" });
  document.getElementById("mise-a-jour").textContent = remplir(T.mis_a_jour, { date: maj });
  const noms = (donnees.sources || []).filter((s) => s.ok && s.nom !== "Ajouts manuels").map((s) => s.nom);
  document.getElementById("sources").textContent = noms.length ? remplir(T.sources_liste, { liste: noms.join(", ") }) : "";
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
    // "no-store" : toujours la dernière version, jamais une copie en cache
    donnees = await (await fetch("events.json", { cache: "no-store" })).json();
    afficher();
    afficherPied();
    setInterval(rafraichirQuand, 60000);
    // Fermer la feuille en touchant le fond assombri
    document.getElementById("feuille").addEventListener("click", (ev) => { if (ev.target.id === "feuille") ev.target.close(); });
  } catch (erreur) {
    console.error(erreur);
    const p = el("p", "avis");
    p.append(el("span", null, (T && T.erreur_chargement) || "Erreur de chargement."));
    document.getElementById("contenu").replaceChildren(p);
  }
}

demarrer();
