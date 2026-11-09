// Illustrations dessinées pour l'agenda (SVG, aucune image externe).
// Chaque type d'activité a sa petite scène. Les couleurs viennent du CSS :
//   .i-ink  = couleur foncée du type   .i-soft = teinte claire du type
//   .i-hi   = blanc de la carte        .i-acc  = couleur d'accent chaude
// La couleur du type est réglée par l'attribut data-cat sur l'élément parent.

const ILLUSTRATIONS = {
  // Conte : un livre ouvert, une lune et deux étoiles qui s'en échappent
  conte: `
    <path class="i-hi i-trait" d="M10 42c7-3.5 14-3.5 22 1V21c-8-4.5-15-4.5-22-1z"/>
    <path class="i-hi i-trait" d="M54 42c-7-3.5-14-3.5-22 1V21c8-4.5 15-4.5 22-1z"/>
    <path class="i-ligne" d="M15 27c4-1.4 8-1.2 12 .6M15 32c4-1.4 8-1.2 12 .6M37 27.6c4-1.8 8-2 12-.6M37 32.6c4-1.8 8-2 12-.6"/>
    <path class="i-ink" d="M44 6.5a6.5 6.5 0 1 0 6.8 9.2A5.2 5.2 0 0 1 44 6.5z"/>
    <path class="i-acc" d="M30 9l1.2 2.6 2.8.4-2 2 .5 2.8-2.5-1.3-2.5 1.3.5-2.8-2-2 2.8-.4z"/>
    <circle class="i-acc" cx="20" cy="14" r="1.6"/>
    <path class="i-soft" d="M8 46c8 4 40 4 48 0v4c-8 4-40 4-48 0z"/>`,

  // Atelier : une palette de peintre et un pinceau
  atelier: `
    <path class="i-hi i-trait" d="M32 12c-12 0-22 8.5-22 19 0 6.5 5 9.5 9.5 8.4 3.6-.9 3.4 4.2 7.6 5.4C40 48 54 40 54 29.5 54 19.6 44 12 32 12z"/>
    <circle class="i-ink" cx="22" cy="27" r="3.4"/>
    <circle class="i-acc" cx="31" cy="21" r="3.4"/>
    <circle class="i-soft i-trait-fin" cx="41" cy="23" r="3.4"/>
    <circle class="i-ink" cx="44" cy="33" r="3"/>
    <path class="i-ink" d="M35 51.5l13.5-17 3.4 2.6-12.6 17.6c-1.4 2-4.6 2.4-5.6.8-.6-1-.2-2.6 1.3-4z"/>
    <path class="i-acc" d="M48.5 34.5l4-5.2c.9-1.2 2.6-1.3 3.5-.3.8.9.7 2.3-.2 3.3l-3.9 4.8z"/>`,

  // Spectacle : une scène avec ses rideaux et un projecteur
  spectacle: `
    <rect class="i-soft" x="8" y="12" width="48" height="38" rx="4"/>
    <path class="i-hi" d="M18 20h28v24H18z"/>
    <path class="i-ink" d="M8 12h14c-1 9-.6 22 2 34H8zM56 12H42c1 9 .6 22-2 34h16z"/>
    <path class="i-ink" d="M8 10h48v6c-6 2-12 2-16 0-4 2-12 2-16 0-4 2-10 2-16 0z"/>
    <path class="i-acc" d="M32 22l-6 18h12z" opacity=".55"/>
    <circle class="i-acc" cx="32" cy="21" r="2.4"/>
    <path class="i-ink" d="M6 50h52v4H6z"/>`,

  // Musique : deux croches et une petite vague sonore
  musique: `
    <path class="i-ink" d="M25 16l24-6v28.5a6 4.6 0 1 1-3-4V19.6l-18 4.5v19a6 4.6 0 1 1-3-4z"/>
    <path class="i-acc" d="M28 18.4l18-4.5v4.2l-18 4.5z"/>
    <path class="i-ligne" d="M10 30c3-3 3-7 0-10M15 33c5-5 5-13 0-18"/>
    <circle class="i-soft i-trait-fin" cx="52" cy="50" r="4"/>`,

  // Visite : la façade d'un musée à colonnes
  visite: `
    <path class="i-ink" d="M32 8l24 12H8z"/>
    <circle class="i-acc" cx="32" cy="15" r="2.2"/>
    <path class="i-hi i-trait" d="M10 22h44v4H10z"/>
    <path class="i-soft i-trait" d="M14 27h6v19h-6zM24 27h6v19h-6zM34 27h6v19h-6zM44 27h6v19h-6z"/>
    <path class="i-ink" d="M8 46h48v4H8zM5 51h54v4H5z"/>`,

  // Nature : un arbre rond et une petite fleur
  nature: `
    <circle class="i-soft i-trait" cx="30" cy="24" r="15"/>
    <circle class="i-ink" cx="24" cy="21" r="2"/><circle class="i-ink" cx="35" cy="28" r="2"/><circle class="i-ink" cx="33" cy="17" r="1.6"/>
    <path class="i-ink" d="M28 36h4v16h-4z"/>
    <path class="i-ligne" d="M30 44l-6-5M30 41l5-4"/>
    <path class="i-ink" d="M8 52h48v3H8z"/>
    <path class="i-ligne" d="M48 51v-8"/>
    <circle class="i-acc" cx="48" cy="40" r="3.6"/>
    <circle class="i-hi" cx="48" cy="40" r="1.4"/>`,

  // Sport : un ballon qui rebondit
  sport: `
    <circle class="i-hi i-trait" cx="32" cy="28" r="15"/>
    <path class="i-ink" d="M32 21l6.6 4.8-2.5 7.8h-8.2l-2.5-7.8z"/>
    <path class="i-ligne" d="M32 13v8M38.6 25.8l8-2.6M36.1 33.6l5 6.6M27.9 33.6l-5 6.6M25.4 25.8l-8-2.6"/>
    <ellipse class="i-soft" cx="32" cy="52" rx="13" ry="3"/>
    <path class="i-acc" d="M10 18h6M8 26h5M50 18h6M51 26h5" stroke-width="2.6" stroke-linecap="round" fill="none" style="stroke:var(--i-acc)"/>`,

  // Fête : une guirlande de fanions et des confettis
  fete: `
    <path class="i-ligne" d="M6 14c16 10 36 10 52 0"/>
    <path class="i-ink" d="M10 16.6l9 4.4-2 11z"/>
    <path class="i-acc" d="M22 21.4l9 2-4.4 10.4z"/>
    <path class="i-soft i-trait-fin" d="M34 23.4l9-1.4-2.6 11z"/>
    <path class="i-ink" d="M46 20.6l8.4-4-.4 11.2z"/>
    <circle class="i-acc" cx="16" cy="44" r="2.2"/><circle class="i-ink" cx="30" cy="50" r="1.8"/>
    <path class="i-ink" d="M40 40l3 1-1 3-3-1z"/><circle class="i-acc" cx="50" cy="48" r="2"/>
    <path class="i-soft" d="M22 40l2.4 1.6-1.6 2.4-2.4-1.6z"/>`,

  // --- Types de lieux (onglet « Sortir ») ---

  // Animaux : une tête d'ours (Berne oblige) et une petite feuille
  animaux: `
    <circle class="i-ink" cx="17" cy="19" r="7"/><circle class="i-ink" cx="47" cy="19" r="7"/>
    <circle class="i-soft" cx="17" cy="19" r="3.2"/><circle class="i-soft" cx="47" cy="19" r="3.2"/>
    <circle class="i-soft i-trait" cx="32" cy="33" r="18"/>
    <ellipse class="i-hi i-trait-fin" cx="32" cy="40" rx="8.5" ry="6.5"/>
    <path class="i-ink" d="M28.6 37.2h6.8l-3.4 3.6z"/>
    <path class="i-ligne" d="M32 41v2.2M28.5 44c2 1.6 5 1.6 7 0"/>
    <circle class="i-ink" cx="25" cy="29" r="2"/><circle class="i-ink" cx="39" cy="29" r="2"/>
    <path class="i-acc" d="M52 46c4-4 8-3 9-1-2 4-6 5-9 1z"/>`,

  // Musée : un tableau encadré avec une montagne et un soleil
  musee: `
    <rect class="i-ink" x="8" y="10" width="48" height="40" rx="4"/>
    <rect class="i-hi" x="13" y="15" width="38" height="30" rx="2"/>
    <path class="i-soft" d="M13 45l12-16 8 10 6-6 12 12z"/>
    <path class="i-ink" d="M25 29l3.4 4.4-3.4-1.6-3 2.2z" opacity=".5"/>
    <circle class="i-acc" cx="42" cy="23" r="4"/>
    <path class="i-ink" d="M22 54h20v3H22z"/>`,

  // Piscine : un canard qui flotte sur les vagues, une échelle
  piscine: `
    <path class="i-ligne" d="M12 10v28M22 10v28M12 17h10M12 25h10M12 33h10"/>
    <path class="i-acc" d="M34 30c0-4 3-7 7-7s7 3 7 7c3 0 7 1 7 5 0 5-6 8-14 8s-13-3-13-8c0-3 3-5 6-5z"/>
    <path class="i-ink" d="M47 27.6l5-1.2-1.2 3z"/>
    <circle class="i-ink" cx="43" cy="27" r="1.4"/>
    <path class="i-soft" d="M6 44c5-3 9-3 13 0s9 3 13 0 9-3 13 0 9 3 13 0v12H6z"/>
    <path class="i-ligne" d="M8 50c4-2 7-2 11 0M30 52c4-2 7-2 11 0"/>`,

  // Jeux : un toboggan, son échelle et une balle
  jeux: `
    <path class="i-ligne" d="M16 52V18M26 52V18M16 26h10M16 34h10M16 42h10"/>
    <path class="i-ink" d="M13 16h16v5H13z"/>
    <path class="i-soft i-trait" d="M27 18c10 0 12 8 16 18s8 12 15 12v6c-10 0-15-3-19-13S33 24 27 24z"/>
    <circle class="i-acc" cx="49" cy="20" r="5.5"/>
    <path class="i-ink" d="M6 52h52v3H6z"/>`,

  // Livres et jeux : une pile de livres avec un marque-page et un dé
  bibliotheque: `
    <rect class="i-ink" x="10" y="42" width="38" height="9" rx="2"/>
    <rect class="i-soft i-trait" x="14" y="31" width="34" height="9" rx="2"/>
    <rect class="i-hi i-trait" x="12" y="20" width="32" height="9" rx="2"/>
    <path class="i-acc" d="M36 20h5v14l-2.5-2-2.5 2z"/>
    <rect class="i-hi i-trait" x="44" y="10" width="12" height="12" rx="3" transform="rotate(12 50 16)"/>
    <circle class="i-ink" cx="48" cy="14" r="1.3"/><circle class="i-ink" cx="52" cy="18.6" r="1.3"/>`,

  // Lieu de rencontre : une maison avec un cœur
  rencontre: `
    <path class="i-soft i-trait" d="M12 30l20-16 20 16v22H12z"/>
    <path class="i-ink" d="M7 31L32 11l25 20-3 3.4L32 17 10 34.4z"/>
    <path class="i-hi i-trait" d="M26 52V40a6 6 0 0 1 12 0v12z"/>
    <path class="i-acc" d="M32 33.5c-3.6-2.6-6-4.4-6-7a3.2 3.2 0 0 1 6-1.6 3.2 3.2 0 0 1 6 1.6c0 2.6-2.4 4.4-6 7z"/>
    <path class="i-ink" d="M6 52h52v3H6z"/>`,

  // Autre : un soleil souriant, pour les activités sans type
  autre: `
    <circle class="i-acc" cx="32" cy="32" r="12"/>
    <path class="i-ligne" d="M32 10v6M32 48v6M10 32h6M48 32h6M16.4 16.4l4.2 4.2M43.4 43.4l4.2 4.2M16.4 47.6l4.2-4.2M43.4 20.6l4.2-4.2"/>
    <path class="i-ink" d="M27 35c2.8 3 7.2 3 10 0" fill="none" stroke-width="2.4" stroke-linecap="round" style="stroke:var(--i-ink)"/>
    <circle class="i-ink" cx="28" cy="29.5" r="1.6"/><circle class="i-ink" cx="36" cy="29.5" r="1.6"/>`,
};

// La catégorie « fête » s'écrit avec un accent dans les données
function cleIllustration(categorie) {
  if (categorie === "fête") return "fete";
  return ILLUSTRATIONS[categorie] ? categorie : "autre";
}

// Renvoie un élément <svg> prêt à insérer (illustration décorative, cachée aux lecteurs d'écran)
function illustration(categorie) {
  const conteneur = document.createElement("span");
  conteneur.className = "illu";
  conteneur.dataset.cat = cleIllustration(categorie);
  conteneur.innerHTML = `<svg viewBox="0 0 64 64" aria-hidden="true" focusable="false">${ILLUSTRATIONS[cleIllustration(categorie)]}</svg>`;
  return conteneur;
}

// Scène bernoise de l'en-tête : collines, Münster, Zytglogge, arcades et l'Aar
const SCENE_BERNE = `
<svg class="scene" viewBox="0 0 400 150" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">
  <circle class="s-soleil" cx="318" cy="44" r="22"/>
  <path class="s-colline-loin" d="M0 98c50-26 96-30 150-14s96 6 140-12 84-14 110 0v78H0z"/>
  <path class="s-colline" d="M0 112c40-14 84-16 128-6s92 8 140-4 92-10 132 2v46H0z"/>
  <!-- Münster : flèche fine -->
  <path class="s-pierre-fonce" d="M92 64l5-30 5 30v42H92z"/>
  <path class="s-pierre-fonce" d="M86 76h22v30H86z"/>
  <path class="s-toit" d="M97 18l2.6 18h-5.2z"/>
  <!-- Zytglogge : tour et horloge -->
  <path class="s-pierre" d="M196 60h30v52h-30z"/>
  <path class="s-toit" d="M192 62l19-26 19 26z"/>
  <path class="s-toit" d="M209 30h4v8h-4z"/>
  <circle class="s-horloge" cx="211" cy="76" r="8.5"/>
  <path class="s-aiguille" d="M211 70v6.5l4.5 3"/>
  <path class="s-fenetre" d="M205 92h12v20h-12z"/>
  <!-- Arcades de la vieille ville -->
  <path class="s-pierre" d="M120 96h76v24h-76zM226 96h96v24h-96z"/>
  <path class="s-toit" d="M118 90l10-12h58l10 12zM224 90l12-14h74l12 14z"/>
  <path class="s-arcade" d="M126 120v-10a6 6 0 0 1 12 0v10zM144 120v-10a6 6 0 0 1 12 0v10zM162 120v-10a6 6 0 0 1 12 0v10zM180 120v-10a6 6 0 0 1 12 0v10zM232 120v-10a6 6 0 0 1 12 0v10zM250 120v-10a6 6 0 0 1 12 0v10zM268 120v-10a6 6 0 0 1 12 0v10zM286 120v-10a6 6 0 0 1 12 0v10zM304 120v-10a6 6 0 0 1 12 0v10z"/>
  <path class="s-geranium" d="M128 98h8v3h-8zM164 98h8v3h-8zM252 98h8v3h-8zM288 98h8v3h-8z"/>
  <!-- L'Aar -->
  <path class="s-aar" d="M0 124c40 6 80 6 120 0s80-6 120 0 80 6 120 0 30-4 40-2v30H0z"/>
  <path class="s-vague" d="M30 134c10 2 20 2 30 0M150 138c12 2 24 2 36 0M270 133c10 2 20 2 30 0"/>
</svg>`;
