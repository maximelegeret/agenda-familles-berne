// Affiche les événements de events.json, regroupés par jour.
// Tous les textes de l'interface viennent de textes_fr.json (traduction allemande prévue plus tard).

const LANGUE = "fr";
let T = {}; // les textes de l'interface

// Remplace {min}, {max}… dans un texte
function remplir(texte, valeurs) {
  return texte.replace(/\{(\w+)\}/g, (_, cle) => valeurs[cle]);
}

// Crée un élément HTML avec une classe et un texte (le texte n'est jamais interprété comme du HTML)
function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

// "2026-11-08T16:00" -> objet Date (heure locale du navigateur = heure de Berne pour nous)
function lireDate(iso) {
  return new Date(iso);
}

// Clé du jour, ex. "2026-11-08", pour regrouper
function cleJour(iso) {
  return iso.slice(0, 10);
}

// Titre d'un jour : "Aujourd'hui", "Demain" ou "samedi 14 novembre"
function titreJour(cle) {
  const aujourdHui = new Date();
  const demain = new Date();
  demain.setDate(aujourdHui.getDate() + 1);
  const format = (d) => d.toLocaleDateString("sv-SE"); // donne AAAA-MM-JJ
  const date = lireDate(cle + "T12:00").toLocaleDateString(LANGUE, {
    weekday: "long", day: "numeric", month: "long",
  });
  if (cle === format(aujourdHui)) return `${T.aujourd_hui} · ${date}`;
  if (cle === format(demain)) return `${T.demain} · ${date}`;
  return date;
}

function heure(iso) {
  return lireDate(iso).toLocaleTimeString(LANGUE, { hour: "2-digit", minute: "2-digit" });
}

// 0.5 -> "6 mois" ; 4 -> "4 ans"
function duree(age) {
  if (age < 1) return remplir(T.mois, { n: Math.round(age * 12) });
  return remplir(age === 1 ? T.an : T.ans, { n: String(age).replace(".", ",") });
}

// Texte de l'âge selon ce que la source indique
function texteAge(e) {
  let texte;
  const min = e.age_min, max = e.age_max;
  if (min != null && max != null) {
    // "6–10 ans", ou "6 mois – 4 ans" quand les unités diffèrent
    texte = min >= 1 ? `${min}–${duree(max)}` : `${duree(min)} – ${duree(max)}`;
  }
  else if (min != null) texte = remplir(T.age_des, { age: duree(min) });
  else if (max != null) texte = remplir(T.age_jusqu_a, { age: duree(max) });
  else if (e.age_texte) return e.age_texte; // âge pas compris : on montre le texte de la source
  else return null;
  if (e.age_source === "déduit") texte += " " + T.age_deduit;
  return texte;
}

function textePrix(prix) {
  if (prix === "gratuit") return T.gratuit;
  if (!prix || prix === "inconnu") return T.prix_inconnu;
  return prix;
}

// Fabrique la fiche d'un événement
function fiche(e) {
  const carte = el("article", "fiche");

  const haut = el("div", "fiche-haut");
  let horaire = heure(e.debut);
  if (e.fin) horaire += " – " + heure(e.fin);
  // Offre régulière : on montre les horaires habituels à la place d'une heure précise
  if (e.type === "offre régulière") horaire = e.repetition;
  haut.append(el("span", "fiche-heure", horaire));
  if (e.categorie) haut.append(el("span", "etiquette", T.categories[e.categorie] || e.categorie));
  carte.append(haut);

  carte.append(el("h3", "fiche-titre", e.titre));
  if (e.description_courte) carte.append(el("p", "fiche-description", e.description_courte));

  carte.append(el("p", "fiche-lieu", e.adresse ? `${e.lieu_nom} · ${e.adresse}` : e.lieu_nom));

  // Pastilles : âge, prix, inscription
  const infos = el("div", "fiche-infos");
  const age = texteAge(e);
  infos.append(el("span", age ? "pastille" : "pastille pastille-vide", age || T.age_inconnu));
  if (/begleitung/i.test(e.age_texte || "")) infos.append(el("span", "pastille", T.accompagne));
  infos.append(el("span", e.prix === "gratuit" ? "pastille pastille-gratuit" : "pastille", textePrix(e.prix)));
  if (e.inscription_requise) infos.append(el("span", "pastille pastille-alerte", T.inscription_requise));
  carte.append(infos);

  // Lien vers la source (toujours affiché), puis les autres sources éventuelles
  const lien = el("a", "fiche-lien", `${T.voir_source} ${e.source} →`);
  lien.href = e.url_source;
  lien.target = "_blank";
  lien.rel = "noopener";
  carte.append(lien);
  if (e.autres_sources && e.autres_sources.length) {
    const autres = el("p", "fiche-autres", T.aussi_sur + " ");
    e.autres_sources.forEach((s, i) => {
      const a = el("a", null, s.source);
      a.href = s.url_source;
      a.target = "_blank";
      a.rel = "noopener";
      if (i > 0) autres.append(", ");
      autres.append(a);
    });
    carte.append(autres);
  }
  return carte;
}

// ---------------------------------------------------------------------------
// Filtres : période, prix, type d'activité
// ---------------------------------------------------------------------------

// Choix par défaut ; mémorisés dans le navigateur pour la prochaine visite
const FILTRES_DEFAUT = { periode: "14_jours", prix: "tous", types: [] };
let filtres = { ...FILTRES_DEFAUT };
let donneesChargees = null;

function chargerFiltres() {
  try {
    const memo = JSON.parse(localStorage.getItem("agenda-filtres"));
    if (memo) filtres = { ...FILTRES_DEFAUT, ...memo };
  } catch (_) { /* navigation privée ou stockage bloqué : on garde les choix par défaut */ }
}

function sauverFiltres() {
  try { localStorage.setItem("agenda-filtres", JSON.stringify(filtres)); } catch (_) { /* idem */ }
}

// Jours (AAAA-MM-JJ) couverts par une période
function joursDeLaPeriode(periode) {
  const format = (d) => d.toLocaleDateString("sv-SE");
  const aujourdHui = new Date();
  if (periode === "aujourd_hui") return [format(aujourdHui)];
  if (periode === "weekend") {
    // Le samedi et le dimanche qui viennent (ou aujourd'hui si on y est déjà)
    const jour = aujourdHui.getDay(); // 0 = dimanche, 6 = samedi
    if (jour === 0) return [format(aujourdHui)];
    const samedi = new Date(aujourdHui);
    samedi.setDate(aujourdHui.getDate() + (6 - jour));
    const dimanche = new Date(samedi);
    dimanche.setDate(samedi.getDate() + 1);
    return [format(samedi), format(dimanche)];
  }
  return null; // 14 jours : pas de restriction
}

function passeLesFiltres(e, jours) {
  if (jours && !jours.includes(cleJour(e.debut))) return false;
  if (filtres.prix === "gratuit" && e.prix !== "gratuit") return false;
  // « Payant » : un prix connu et non gratuit (les prix inconnus n'apparaissent qu'avec « Tous »)
  if (filtres.prix === "payant" && (e.prix === "gratuit" || !e.prix || e.prix === "inconnu")) return false;
  if (filtres.types.length && !filtres.types.includes(e.categorie)) return false;
  return true;
}

// Un groupe de boutons (une ligne de filtres)
function groupeDeBoutons(libelle, options, estActif, auClic) {
  const groupe = el("div", "filtre-groupe");
  groupe.append(el("span", "filtre-libelle", libelle));
  const boutons = el("div", "filtre-boutons");
  for (const [valeur, texte] of options) {
    const b = el("button", "puce", texte);
    b.type = "button";
    b.setAttribute("aria-pressed", estActif(valeur) ? "true" : "false");
    b.addEventListener("click", () => { auClic(valeur); sauverFiltres(); afficher(donneesChargees); });
    boutons.append(b);
  }
  groupe.append(boutons);
  return groupe;
}

function afficherFiltres(donnees) {
  const zone = document.getElementById("filtres");
  zone.replaceChildren();

  zone.append(groupeDeBoutons(T.filtre_periode, [
    ["aujourd_hui", T.periode_aujourd_hui], ["weekend", T.periode_weekend], ["14_jours", T.periode_14_jours],
  ], (v) => filtres.periode === v, (v) => { filtres.periode = v; }));

  zone.append(groupeDeBoutons(T.filtre_prix, [
    ["tous", T.prix_tous], ["gratuit", T.prix_gratuit], ["payant", T.prix_payant],
  ], (v) => filtres.prix === v, (v) => { filtres.prix = v; }));

  // Types : seulement ceux présents dans les données, dans l'ordre de la liste des catégories
  const presents = new Set([...donnees.evenements, ...(donnees.offres_regulieres || [])].map((e) => e.categorie));
  const types = Object.keys(T.categories).filter((c) => presents.has(c));
  // On oublie un type mémorisé qui n'existe plus dans les données
  filtres.types = filtres.types.filter((t) => types.includes(t));
  zone.append(groupeDeBoutons(T.filtre_type, [["tous", T.types_tous], ...types.map((c) => [c, T.categories[c]])],
    (v) => (v === "tous" ? filtres.types.length === 0 : filtres.types.includes(v)),
    (v) => {
      if (v === "tous") filtres.types = [];
      else if (filtres.types.includes(v)) filtres.types = filtres.types.filter((t) => t !== v);
      else filtres.types = [...filtres.types, v];
    }));
}

// ---------------------------------------------------------------------------
// Affichage de la liste
// ---------------------------------------------------------------------------

function afficher(donnees) {
  donneesChargees = donnees;
  afficherFiltres(donnees);
  const liste = document.getElementById("liste");
  liste.replaceChildren();

  // Avertissement si une source n'a pas pu être lue
  for (const s of donnees.sources || []) {
    if (!s.ok) liste.append(el("p", "message message-erreur", remplir(T.source_en_echec, { nom: s.nom })));
  }

  const jours = joursDeLaPeriode(filtres.periode);
  const evenements = donnees.evenements.filter((e) => passeLesFiltres(e, jours));
  // Offres régulières : filtrées par prix et type (elles ont lieu toutes les semaines)
  const offres = (donnees.offres_regulieres || []).filter((o) => passeLesFiltres(o, null));

  const n = evenements.length;
  // En français, 0 et 1 s'accordent au singulier
  liste.append(el("p", "compteur", n <= 1 ? remplir(T.resultat, { n }) : remplir(T.resultats, { n })));

  // Section « Chaque semaine » : les offres régulières, repliée par défaut
  // (<details> se déplie d'un toucher, sans JavaScript supplémentaire)
  if (offres.length) {
    const section = el("details", "jour jour-regulier");
    const titre = el("summary", "jour-titre");
    titre.append(el("span", null, `${T.chaque_semaine} (${offres.length})`));
    titre.append(el("span", "jour-aide", T.chaque_semaine_aide));
    section.append(titre);
    offres.forEach((o) => section.append(fiche(o)));
    liste.append(section);
  }

  if (!donnees.evenements.length) {
    liste.append(el("p", "message", T.aucun_evenement));
  } else if (!n) {
    // Rien ne correspond : on propose de tout réafficher
    const vide = el("div", "message");
    vide.append(el("p", null, T.aucun_resultat));
    const bouton = el("button", "puce", T.reinitialiser);
    bouton.type = "button";
    bouton.addEventListener("click", () => {
      filtres = { ...FILTRES_DEFAUT, types: [] };
      sauverFiltres();
      afficher(donneesChargees);
    });
    vide.append(bouton);
    liste.append(vide);
  }

  // Regroupe par jour (les événements arrivent déjà triés par date)
  let jourCourant = null;
  let section = null;
  for (const e of evenements) {
    const cle = cleJour(e.debut);
    if (cle !== jourCourant) {
      jourCourant = cle;
      section = el("section", "jour");
      section.append(el("h2", "jour-titre", titreJour(cle)));
      liste.append(section);
    }
    section.append(fiche(e));
  }

  const maj = lireDate(donnees.mis_a_jour).toLocaleString(LANGUE, {
    day: "numeric", month: "long", hour: "2-digit", minute: "2-digit",
  });
  document.getElementById("mise-a-jour").textContent = `${T.mis_a_jour} ${maj}`;
}

async function demarrer() {
  try {
    T = await (await fetch(`textes_${LANGUE}.json`)).json();
    document.title = T.titre_page;
    document.getElementById("titre-page").textContent = T.titre_page;
    document.getElementById("sous-titre").textContent = T.sous_titre;
    document.getElementById("liste").replaceChildren(el("p", "message", T.chargement));
    chargerFiltres();

    // "no-store" : toujours la dernière version, jamais une copie en cache
    const donnees = await (await fetch("events.json", { cache: "no-store" })).json();
    afficher(donnees);
  } catch (erreur) {
    console.error(erreur);
    const message = (T && T.erreur_chargement) || "Erreur de chargement.";
    document.getElementById("liste").replaceChildren(el("p", "message message-erreur", message));
  }
}

demarrer();
