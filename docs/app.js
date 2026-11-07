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

// Texte de l'âge selon ce que la source indique
function texteAge(e) {
  let texte;
  if (e.age_min != null && e.age_max != null) texte = remplir(T.age_entre, { min: e.age_min, max: e.age_max });
  else if (e.age_min != null) texte = remplir(T.age_des, { min: e.age_min });
  else if (e.age_max != null) texte = remplir(T.age_jusqu_a, { max: e.age_max });
  else if (e.age_texte) return e.age_texte; // âge pas encore compris : on montre le texte de la source
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

function afficher(donnees) {
  const liste = document.getElementById("liste");
  liste.replaceChildren();

  // Avertissement si une source n'a pas pu être lue
  for (const s of donnees.sources || []) {
    if (!s.ok) liste.append(el("p", "message message-erreur", remplir(T.source_en_echec, { nom: s.nom })));
  }

  if (!donnees.evenements.length) {
    liste.append(el("p", "message", T.aucun_evenement));
  }

  // Regroupe par jour (les événements arrivent déjà triés par date)
  let jourCourant = null;
  let section = null;
  for (const e of donnees.evenements) {
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
