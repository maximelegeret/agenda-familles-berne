// Onglet « Sortir » : où aller maintenant ?
// - En haut : la météo du jour à Berne (Open-Meteo, gratuit, sans clé ; on n'envoie que les
//   coordonnées du centre de Berne) et le choix Tous / Dedans / Dehors.
// - Puis : les lieux ouverts maintenant (couverts d'abord s'il pleut), les activités de l'agenda
//   qui commencent dans les 3 heures, et les lieux fermés avec leur prochaine ouverture.
// Les horaires des 14 prochains jours sont calculés chaque nuit par recuperer.py (docs/lieux.json).
// Utilise les outils de app.js : el, icone, remplir, T, filtres, ligne, convientAuxAges…

// Pour vérifier l'écran à une autre heure ou par un autre temps (sans effet en temps normal) :
//   …/?maintenant=2026-11-15T09:00&meteo=pluie#sortir     (meteo = pluie, neige ou beau)
const PARAMS_SORTIR = new URLSearchParams(location.search);
const maintenantSortir = () => (PARAMS_SORTIR.get("maintenant") ? new Date(PARAMS_SORTIR.get("maintenant")) : new Date());

const BERNE_METEO = "https://api.open-meteo.com/v1/forecast?latitude=46.948&longitude=7.447"
  + "&current=temperature_2m,precipitation,weather_code"
  + "&hourly=precipitation,precipitation_probability,weather_code&forecast_days=2&timezone=Europe%2FZurich";

let lieux = null;          // contenu de docs/lieux.json
let erreurLieux = false;
let meteo = null;          // { texte, icone, mauvais (pluie/neige), temperature } ou { indisponible: true }
let meteoLueA = 0;
let choixLieux = "tous";   // tous | dedans | dehors (gardé sur le téléphone)
try { choixLieux = localStorage.getItem("sortir-choix") || "tous"; } catch (_) { /* stockage indisponible */ }

// Types de lieux -> teinte et illustration (nature réutilise celle de l'agenda)
const cleLieu = (type) => (type === "nature" ? "nature" : type);

// ---------------------------------------------------------------------------
// Ouvert ou fermé ?
// ---------------------------------------------------------------------------

const hhmm = (d) => `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
const enMinutes = (t) => Number(t.slice(0, 2)) * 60 + Number(t.slice(3, 5));

// Statut d'un lieu à un instant donné :
// { ouvert, texte, ordre } — ordre sert au tri (0 = ouvert, 1 = ferme bientôt, 2 = fermé)
function statutLieu(lieu, m) {
  if (lieu.toujours_ouvert) return { ouvert: true, texte: T.acces_libre, ordre: 0 };
  const cle = formatJour(m);
  if (!lieu.ouverture || !(cle in lieu.ouverture)) return { ouvert: false, texte: T.horaires_a_verifier, ordre: 3 };
  const maintenant = enMinutes(hhmm(m));
  const plages = lieu.ouverture[cle].map((p) => p.split("-"));
  for (const [debut, fin] of plages) {
    if (enMinutes(debut) <= maintenant && maintenant < enMinutes(fin)) {
      const bientot = enMinutes(fin) - maintenant <= 60;
      return { ouvert: true, texte: remplir(bientot ? T.ferme_bientot : T.ouvert_jusqua, { heure: fin }), ordre: bientot ? 1 : 0 };
    }
  }
  const plusTard = plages.find(([debut]) => enMinutes(debut) > maintenant);
  if (plusTard) return { ouvert: false, texte: remplir(T.ouvre_a, { heure: plusTard[0] }), ordre: 2, attente: enMinutes(plusTard[0]) - maintenant };
  for (let n = 1; n <= 7; n++) {
    const jour = new Date(m); jour.setDate(m.getDate() + n);
    const prochaines = lieu.ouverture[formatJour(jour)];
    if (prochaines && prochaines.length) {
      const h = prochaines[0].split("-")[0];
      const texte = n === 1 ? remplir(T.ouvre_demain, { heure: h })
        : remplir(T.ouvre_jour, { jour: jour.toLocaleDateString(LANGUE, { weekday: "long" }), heure: h });
      return { ouvert: false, texte, ordre: 2, attente: n * 1440 + enMinutes(h) - maintenant };
    }
  }
  return { ouvert: false, texte: T.ferme_prochains_jours, ordre: 3 };
}

// Le lieu convient-il aux âges réglés dans les filtres de l'agenda ? (âge non précisé : oui)
function lieuConvientAuxAges(lieu) {
  if (!filtres.ages.length || lieu.age_min == null) return true;
  return filtres.ages.some((a) => a >= lieu.age_min);
}

function passeChoix(lieu) {
  if (choixLieux === "dedans") return lieu.dedans === true || lieu.dedans === "mixte";
  if (choixLieux === "dehors") return lieu.dedans === false || lieu.dedans === "mixte";
  return true;
}

// Plus le nombre est petit, plus le lieu monte : adapté à la météo, puis aux âges
function rangMeteo(lieu) {
  if (!meteo || meteo.indisponible) return 0;
  if (meteo.mauvais) return lieu.dedans === true ? 0 : lieu.dedans === "mixte" ? 1 : 2;
  return lieu.dedans === true ? 1 : 0;
}

// ---------------------------------------------------------------------------
// Météo du jour (Open-Meteo)
// ---------------------------------------------------------------------------

function descriptionCode(code) {
  if ([71, 73, 75, 77, 85, 86].includes(code)) return { texte: T.meteo_neige, icone: "neige", mauvais: true };
  if (code >= 51 && code <= 99) return { texte: null, icone: "pluie", mauvais: true }; // pluie, averses, orage
  if (code === 45 || code === 48) return { texte: T.meteo_brouillard, icone: "brouillard", mauvais: false };
  if (code === 3) return { texte: T.meteo_couvert, icone: "nuage", mauvais: false };
  if (code === 2) return { texte: T.meteo_eclaircies, icone: "eclaircie", mauvais: false };
  return { texte: T.meteo_soleil, icone: "soleil", mauvais: false };
}

// Heures de pluie : précipitations ≥ 0,2 mm ou probabilité ≥ 60 %
function pleutA(h, i) {
  return (h.precipitation[i] || 0) >= 0.2 || (h.precipitation_probability[i] || 0) >= 60;
}

function lireMeteo(d, m) {
  const h = d.hourly;
  const debut = h.time.findIndex((t) => t.slice(0, 13) === `${formatJour(m)}T${String(m.getHours()).padStart(2, "0")}`);
  const temperature = Math.round(d.current.temperature_2m);
  const actuel = descriptionCode(d.current.weather_code);
  if (debut < 0) return { ...actuel, texte: actuel.texte || T.meteo_couvert, temperature };
  const finJournee = h.time.findIndex((t) => t === `${formatJour(m)}T20:00`);
  const dernier = finJournee > debut ? finJournee : debut + 6;
  if (actuel.icone === "neige") return { ...actuel, temperature };
  if (d.current.precipitation > 0 || pleutA(h, debut)) {
    let i = debut + 1;
    while (i <= dernier && pleutA(h, i)) i++;
    const texte = i > dernier ? T.meteo_pluie_journee : remplir(T.meteo_pluie_jusqua, { heure: `${Number(h.time[i].slice(11, 13))} h` });
    return { texte, icone: "pluie", mauvais: true, temperature };
  }
  for (let i = debut + 1; i <= Math.min(debut + 3, h.time.length - 1); i++) {
    if (pleutA(h, i)) {
      return { texte: remplir(T.meteo_pluie_des, { heure: `${Number(h.time[i].slice(11, 13))} h` }), icone: "pluie", mauvais: true, temperature };
    }
  }
  return { ...actuel, texte: actuel.texte || T.meteo_couvert, mauvais: false, temperature };
}

async function chargerMeteo() {
  const simulee = PARAMS_SORTIR.get("meteo");
  if (simulee) {
    meteo = simulee === "beau" ? { texte: T.meteo_soleil, icone: "soleil", mauvais: false, temperature: 12 }
      : simulee === "neige" ? { texte: T.meteo_neige, icone: "neige", mauvais: true, temperature: -1 }
      : { texte: remplir(T.meteo_pluie_jusqua, { heure: "14 h" }), icone: "pluie", mauvais: true, temperature: 6 };
    return;
  }
  // Une lecture toutes les 30 minutes suffit
  if (meteo && Date.now() - meteoLueA < 30 * 60e3) return;
  try {
    const d = await (await fetch(BERNE_METEO, { cache: "no-store" })).json();
    meteo = lireMeteo(d, maintenantSortir());
    meteoLueA = Date.now();
  } catch (_) {
    meteo = { indisponible: true };
  }
}

function bandeMeteo() {
  const zone = el("div", "meteo");
  if (!meteo) {
    zone.append(icone("nuage"), el("span", "meteo-texte meteo-attente", T.meteo_chargement));
    return zone;
  }
  if (meteo.indisponible) {
    zone.append(icone("nuage"), el("span", "meteo-texte meteo-attente", T.meteo_indisponible));
    return zone;
  }
  if (meteo.mauvais) zone.classList.add("meteo-mauvais");
  const textes = el("span", "meteo-textes");
  const ligneHaut = el("span", "meteo-texte");
  ligneHaut.append(el("strong", null, meteo.texte), el("span", "meteo-temp", ` · ${meteo.temperature}°`));
  textes.append(ligneHaut, el("span", "meteo-conseil", meteo.mauvais ? T.meteo_conseil_dedans : T.meteo_conseil_dehors));
  zone.append(icone(meteo.icone), textes);
  return zone;
}

// ---------------------------------------------------------------------------
// Une ligne de lieu (même forme que les lignes de l'agenda)
// ---------------------------------------------------------------------------

function texteAujourdhui(lieu, m) {
  if (lieu.toujours_ouvert) return T.acces_libre;
  const plages = (lieu.ouverture || {})[formatJour(m)];
  if (!plages) return T.horaires_a_verifier;
  return plages.length ? remplir(T.aujourd_hui_horaires, { plages: plages.join(", ").replace(/-/g, "–") }) : T.aujourd_hui_ferme;
}

function equipements(lieu) {
  const liste = (lieu.equipements || []).filter((e) => ICONES[e]);
  if (!liste.length) return null;
  const zone = el("span", "equipements");
  for (const e of liste) {
    const i = icone(e);
    i.setAttribute("role", "img");
    i.setAttribute("aria-label", T.equipements[e]);
    i.title = T.equipements[e];
    zone.append(i);
  }
  return zone;
}

function pastillesLieu(lieu) {
  const zone = el("div", "pastilles");
  zone.append(el("span", "pastille", lieu.dedans === true ? T.dedans : lieu.dedans === false ? T.dehors : T.mixte));
  if (/^gratuit/i.test(lieu.prix)) zone.append(el("span", "pastille pastille-gratuit", T.gratuit));
  if (lieu.age_min) zone.append(el("span", "pastille", remplir(T.age_des, { age: duree(lieu.age_min) })));
  const eq = equipements(lieu);
  if (eq) zone.append(eq);
  return zone;
}

function ligneDeLieu(lieu, statut, m) {
  const item = el("article", statut.ouvert ? "ligne ligne-lieu-item" : "ligne ligne-lieu-item est-ferme");
  item.dataset.cat = cleLieu(lieu.type);
  const bouton = el("button", "ligne-bouton");
  bouton.type = "button";
  bouton.setAttribute("aria-expanded", "false");
  const vignette = el("span", "vignette");
  vignette.append(illustration(cleLieu(lieu.type)));
  const textes = el("span", "ligne-textes");
  const haut = el("span", "ligne-haut");
  haut.append(el("span", statut.ordre === 1 ? "heure statut statut-bientot" : "heure statut", statut.texte));
  haut.append(el("span", "type", T.types_lieux[lieu.type]));
  textes.append(haut, el("span", "ligne-titre", lieu.nom), el("span", "ligne-lieu", lieu.resume), pastillesLieu(lieu));
  bouton.append(vignette, textes, icone("fleche"));
  item.append(bouton);

  const detail = el("div", "ligne-detail");
  detail.hidden = true;
  detail.append(el("p", "ligne-texte ligne-horaires", texteAujourdhui(lieu, m)));
  detail.append(el("p", "ligne-texte", lieu.prix === "gratuit" ? T.gratuit : lieu.prix));
  if (lieu.remarque) {
    const avis = el("p", "remarque");
    avis.append(icone("alerte"), el("span", null, lieu.remarque));
    detail.append(avis);
  }
  const adresse = el("p", "lieu");
  adresse.append(icone("lieu"), el("span", null, lieu.adresse));
  detail.append(adresse);
  const a = el("a", "lien-source");
  a.href = lieu.url; a.target = "_blank"; a.rel = "noopener";
  a.append(el("span", null, T.site_officiel), icone("externe"));
  detail.append(a);
  const verifie = lireDate(lieu.verifie_le + "T12:00").toLocaleDateString(LANGUE, { day: "numeric", month: "long", year: "numeric" });
  detail.append(el("p", "verifie", remplir(T.verifie_le, { date: verifie })));
  item.append(detail);

  bouton.addEventListener("click", () => {
    const ouvert = bouton.getAttribute("aria-expanded") === "true";
    bouton.setAttribute("aria-expanded", String(!ouvert));
    detail.hidden = ouvert;
  });
  return item;
}

// ---------------------------------------------------------------------------
// L'écran
// ---------------------------------------------------------------------------

function afficherBandeauSortir() {
  const bandeau = document.getElementById("bandeau");
  bandeau.setAttribute("role", "region");
  bandeau.setAttribute("aria-label", T.lieux_dedans + " / " + T.lieux_dehors);
  bandeau.replaceChildren();
  const segments = el("div", "segments segments-plein");
  segments.setAttribute("role", "group");
  for (const [valeur, texte] of [["tous", T.lieux_tous], ["dedans", T.lieux_dedans], ["dehors", T.lieux_dehors]]) {
    const b = el("button", "segment", texte);
    b.type = "button";
    b.setAttribute("aria-pressed", String(choixLieux === valeur));
    b.addEventListener("click", () => {
      choixLieux = valeur;
      try { localStorage.setItem("sortir-choix", valeur); } catch (_) { /* idem */ }
      afficherSortir();
    });
    segments.append(b);
  }
  bandeau.append(segments);
}

// Activités de l'agenda en cours ou qui commencent dans les 3 prochaines heures
function activitesBientot(m) {
  if (!donnees || !donnees.evenements) return [];
  return donnees.evenements.filter((e) => {
    const debut = lireDate(e.debut);
    const fin = e.fin ? lireDate(e.fin) : new Date(debut.getTime() + 2 * 3600e3);
    return fin > m && debut - m <= 3 * 3600e3 && convientAuxAges(e);
  }).sort((a, b) => a.debut.localeCompare(b.debut));
}

function afficherSortir() {
  const contenu = document.getElementById("contenu");
  document.getElementById("titre-page").textContent = T.titre_sortir;
  afficherBandeauSortir();
  piedSortir();
  if (erreurLieux) {
    const p = el("p", "avis");
    p.append(icone("alerte"), el("span", null, T.erreur_lieux));
    contenu.replaceChildren(p);
    return;
  }
  if (!lieux) {
    document.getElementById("resume").textContent = T.chargement_lieux;
    contenu.replaceChildren();
    chargerLieux();
    return;
  }

  const m = maintenantSortir();
  const choisis = lieux.lieux.filter(passeChoix).map((l) => ({ lieu: l, statut: statutLieu(l, m) }));
  // La météo d'abord (un musée qui ferme dans une heure reste devant un parc sous la pluie)
  const parRang = (a, b) => (rangMeteo(a.lieu) - rangMeteo(b.lieu))
    || (a.statut.ordre - b.statut.ordre)
    || (lieuConvientAuxAges(b.lieu) - lieuConvientAuxAges(a.lieu))
    || a.lieu.nom.localeCompare(b.lieu.nom, LANGUE);
  const ouverts = choisis.filter((x) => x.statut.ouvert).sort(parRang);
  const fermes = choisis.filter((x) => !x.statut.ouvert)
    .sort((a, b) => (a.statut.attente ?? 1e9) - (b.statut.attente ?? 1e9) || parRang(a, b));

  // En-tête : combien de lieux ouverts, et pour quels âges
  const n = ouverts.length;
  let resume = n === 0 ? T.resume_sortir_aucun : n === 1 ? T.resume_sortir_un : remplir(T.resume_sortir, { n });
  if (filtres.ages.length) {
    const ages = filtres.ages.map((a) => (a === 0 ? T.moins_un_an : String(a))).join(", ").replace(/, ([^,]*)$/, " et $1");
    resume += ` · ${remplir(T.pour_ages, { ages: remplir(T.ans, { n: ages }) })}`;
  }
  document.getElementById("resume").textContent = resume;

  contenu.replaceChildren(bandeMeteo());

  contenu.append(el("h2", "section-titre", T.ouvert_maintenant));
  if (ouverts.length) {
    const groupe = el("div", "groupe");
    ouverts.forEach((x) => groupe.append(ligneDeLieu(x.lieu, x.statut, m)));
    contenu.append(groupe);
  } else {
    const vide = el("div", "vide vide-compact");
    vide.append(el("p", "vide-titre", T.rien_d_ouvert), el("p", "vide-aide", T.rien_d_ouvert_aide));
    contenu.append(vide);
  }

  const bientot = activitesBientot(m);
  if (bientot.length) {
    contenu.append(el("h2", "section-titre", T.commence_bientot));
    const groupe = el("div", "groupe");
    bientot.slice(0, 5).forEach((e) => groupe.append(ligne(e)));
    contenu.append(groupe);
  }

  if (fermes.length) {
    contenu.append(el("h2", "section-titre", T.ferme_pour_l_instant));
    const groupe = el("div", "groupe");
    fermes.forEach((x) => groupe.append(ligneDeLieu(x.lieu, x.statut, m)));
    contenu.append(groupe);
  }

  // La météo arrive après coup : on redessine une fois reçue
  if (!meteo || (!meteo.indisponible && Date.now() - meteoLueA > 30 * 60e3 && !PARAMS_SORTIR.get("meteo"))) {
    chargerMeteo().then(() => { if (onglet === "sortir") afficherSortir(); });
  }
}

function piedSortir() {
  const p = document.getElementById("pied-sortir");
  p.hidden = false;
  p.textContent = `${T.pied_sortir} ${T.credit_meteo}`;
  if (lieux) {
    const maj = lireDate(lieux.mis_a_jour).toLocaleString(LANGUE, { weekday: "long", day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" });
    document.getElementById("mise-a-jour").textContent = remplir(T.mis_a_jour, { date: maj });
  }
}

async function chargerLieux() {
  if (chargerLieux.enCours) return;
  chargerLieux.enCours = true;
  try {
    lieux = await (await fetch("lieux.json", { cache: "no-store" })).json();
  } catch (erreur) {
    console.error(erreur);
    erreurLieux = true;
  }
  chargerLieux.enCours = false;
  if (onglet === "sortir") afficherSortir();
}
