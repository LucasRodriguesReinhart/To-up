/* =====================================================================
   AMS — arte vetorial dos equipamentos (placeholders estilizados)
   Estilo: cartoon com contorno escuro, fills chapados e highlight
   superior-esquerdo. Cada item tem silhueta e paleta próprias.
   No Roblox cada um vira um ImageLabel (render/ícone do item).
   ===================================================================== */
(function(){
  const O = '#121a25';                       // cor do contorno
  const st = `stroke="${O}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"`;
  const thin = `stroke="${O}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"`;
  const hl = (d, o = .55, w = 3.5) => `<path d="${d}" fill="none" stroke="rgba(255,255,255,${o})" stroke-width="${w}" stroke-linecap="round"/>`;
  const wrap = inner => `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">${inner}</svg>`;

  /* ---------- MOCHILAS ------------------------------------------------ */
  function bag({ body, shade, flap, strap, pocket, emblem = '', extra = '' }){
    return `
      <rect x="20" y="40" width="11" height="54" rx="5.5" fill="${strap}" ${st}/>
      <rect x="89" y="40" width="11" height="54" rx="5.5" fill="${strap}" ${st}/>
      <rect x="28" y="30" width="64" height="80" rx="18" fill="${body}"/>
      <path d="M28 70 H92 V92 A18 18 0 0 1 74 110 H46 A18 18 0 0 1 28 92 Z" fill="${shade}"/>
      <rect x="28" y="30" width="64" height="80" rx="18" fill="none" ${st}/>
      <rect x="42" y="78" width="36" height="22" rx="8" fill="${pocket}" ${st}/>
      <path d="M46 14 Q60 2 74 14" fill="none" ${st}/>
      <path d="M36 20 H84 A12 12 0 0 1 96 32 V46 H24 V32 A12 12 0 0 1 36 20 Z" fill="${flap}" ${st}/>
      ${hl('M31 30 Q33 25 39 24 H52')}
      ${emblem}${extra}`;
  }

  const emblemLeaf = (c = '#ffb13b') => `
    <path d="M52 56 c-2 -10 8 -16 16 -11 c6 4 5 13 -2 14 c-5 1 -8 -3 -6 -7" fill="none" stroke="${c}" stroke-width="4" stroke-linecap="round"/>
    <path d="M66 59 l8 6" stroke="${c}" stroke-width="4" stroke-linecap="round"/>`;
  const emblemCloud = `
    <path d="M44 62 c-4 -6 2 -12 8 -9 c2 -7 12 -8 15 -1 c6 -4 13 2 10 8 c6 2 5 10 -2 10 c-2 6 -10 7 -13 2 c-5 5 -14 3 -14 -3 c-5 1 -8 -3 -4 -7z" fill="#d6303e" stroke="#fff" stroke-width="2.5" stroke-linejoin="round"/>`;
  const emblemCrescent = (c = '#c69bff') => `
    <path d="M66 50 a12 12 0 1 0 0 24 a9 9 0 1 1 0 -24z" fill="${c}" ${thin}/>`;
  const emblemHero = `
    <path d="M60 48 l12 6 v10 c0 7 -6 11 -12 13 c-6 -2 -12 -6 -12 -13 v-10z" fill="#ffd23f" ${thin}/>
    <path d="M62 52 l-6 11 h5 l-2 8 l7 -12 h-5z" fill="#e53935"/>`;

  const BAGS = {
    'pergaminho-ninja': wrap(`
      <ellipse cx="22" cy="60" rx="9" ry="19" fill="#c89a62" ${st}/>
      <ellipse cx="98" cy="60" rx="9" ry="19" fill="#c89a62" ${st}/>
      <rect x="22" y="41" width="76" height="38" fill="#f1dfb8"/>
      <path d="M22 60 h76 v19 h-76z" fill="#dcc394"/>
      <rect x="22" y="41" width="76" height="38" fill="none" ${st}/>
      <ellipse cx="98" cy="60" rx="9" ry="19" fill="#d9ad73" ${st}/>
      <ellipse cx="98" cy="60" rx="4" ry="10" fill="#8f6236" ${thin}/>
      <ellipse cx="22" cy="60" rx="9" ry="19" fill="#d9ad73" ${st}/>
      <ellipse cx="22" cy="60" rx="4" ry="10" fill="#8f6236" ${thin}/>
      <rect x="52" y="36" width="12" height="48" rx="4" fill="#d6303e" ${st}/>
      ${hl('M28 46 H48', .6)}
      <path d="M78 52 c-2 -8 7 -12 13 -8 c4 3 3 10 -2 11 c-4 1 -6 -2 -5 -5" fill="none" stroke="#5b3a1c" stroke-width="3" stroke-linecap="round"/>`),

    'mochila-akatsuki': wrap(bag({ body:'#2f2742', shade:'#1e1830', flap:'#3b3252', strap:'#211a30', pocket:'#3b3252', emblem: emblemCloud })),

    'casco-do-mestre-kame': wrap(`
      <rect x="18" y="36" width="12" height="52" rx="6" fill="#6b4a2a" ${st}/>
      <rect x="90" y="36" width="12" height="52" rx="6" fill="#6b4a2a" ${st}/>
      <path d="M18 76 A42 40 0 0 1 102 76 Z" fill="#7bb34a"/>
      <path d="M18 76 A42 40 0 0 1 102 76 L96 76 A36 34 0 0 0 24 76 Z" fill="#5c8f33"/>
      <path d="M18 76 A42 40 0 0 1 102 76 Z" fill="none" ${st}/>
      <path d="M48 48 l12 -6 12 6 v12 l-12 6 -12 -6z" fill="#9ed45f" ${thin}/>
      <path d="M26 66 l10 -6 12 6 v10 l-12 4 -10 -4z" fill="#8ec650" ${thin}/>
      <path d="M72 66 l12 -6 10 6 v10 l-10 4 -12 -4z" fill="#8ec650" ${thin}/>
      <rect x="14" y="74" width="92" height="18" rx="9" fill="#e9c68f" ${st}/>
      <rect x="22" y="92" width="76" height="12" rx="6" fill="#c8a06a" ${st}/>
      ${hl('M34 52 Q44 42 56 40', .5)}`),

    'capsula-hoi-poi': wrap(`
      <g transform="rotate(-32 60 60)">
        <rect x="24" y="40" width="72" height="40" rx="20" fill="#ff8a2b"/>
        <path d="M24 60 h72 v0 a20 20 0 0 1 -20 20 h-32 a20 20 0 0 1 -20 -20z" fill="#e0661a"/>
        <path d="M44 40 h32 a20 20 0 0 1 20 20 h-72 a20 20 0 0 1 20 -20z" fill="#f4f1ea"/>
        <rect x="24" y="40" width="72" height="40" rx="20" fill="none" ${st}/>
        <circle cx="60" cy="60" r="7" fill="#ffd23f" ${thin}/>
        <circle cx="60" cy="60" r="2.5" fill="#1a1a1a"/>
        <path d="M58 42 H80" stroke="#ffffffaa" stroke-width="3" stroke-linecap="round"/>
      </g>
      <path d="M30 92 Q44 104 60 100 Q76 96 90 104" fill="none" stroke="#ff8a2b" stroke-width="3.5" stroke-linecap="round" opacity=".7"/>`),

    'manto-das-sombras': wrap(`
      <path d="M60 8 C 44 8 36 22 36 38 C 24 48 18 72 16 108 H104 C 102 72 96 48 84 38 C 84 22 76 8 60 8 Z" fill="#3b2a66"/>
      <path d="M16 108 H104 C 103 86 100 72 94 60 C 80 76 40 76 26 60 C 20 72 17 86 16 108 Z" fill="#2b1d4f"/>
      <path d="M60 8 C 44 8 36 22 36 38 C 24 48 18 72 16 108 H104 C 102 72 96 48 84 38 C 84 22 76 8 60 8 Z" fill="none" ${st}/>
      <path d="M60 18 C 50 18 44 28 44 40 C 50 36 70 36 76 40 C 76 28 70 18 60 18 Z" fill="#120b24" ${thin}/>
      <path d="M42 46 C 36 56 32 70 30 92" fill="none" stroke="#9b6cff" stroke-width="3" stroke-linecap="round" opacity=".8"/>
      <path d="M78 46 C 84 56 88 70 90 92" fill="none" stroke="#9b6cff" stroke-width="3" stroke-linecap="round" opacity=".8"/>
      <g fill="#c69bff"><ellipse cx="53" cy="32" rx="3" ry="2"/><ellipse cx="67" cy="32" rx="3" ry="2"/></g>
      <circle cx="60" cy="48" r="5" fill="#c69bff" ${thin}/>
      <path d="M62 70 a10 10 0 1 0 0 20 a8 8 0 1 1 0 -20z" fill="#c69bff" ${thin}/>
      ${hl('M46 16 Q52 10 60 10', .35)}`),

    'bau-da-shadow-garden': wrap(`
      <rect x="18" y="52" width="84" height="48" rx="8" fill="#241a40"/>
      <path d="M18 76 H102 V92 A8 8 0 0 1 94 100 H26 A8 8 0 0 1 18 92 Z" fill="#170f2c"/>
      <rect x="18" y="52" width="84" height="48" rx="8" fill="none" ${st}/>
      <path d="M18 58 A42 24 0 0 1 102 58 V64 H18 Z" fill="#33255c" ${st}/>
      <rect x="34" y="40" width="10" height="60" fill="#8c5bff" ${thin}/>
      <rect x="76" y="40" width="10" height="60" fill="#8c5bff" ${thin}/>
      <rect x="51" y="58" width="18" height="18" rx="4" fill="#c69bff" ${thin}/>
      <circle cx="60" cy="66" r="3.5" fill="#120b24"/>
      <path d="M58 70 v5" stroke="#120b24" stroke-width="3" stroke-linecap="round"/>
      ${hl('M26 54 Q40 44 58 42', .3)}
      <path d="M22 108 Q40 100 60 106 Q80 112 98 104" fill="none" stroke="#9b6cff" stroke-width="3" stroke-linecap="round" opacity=".6"/>`),

    'caixa-nichirin': wrap(`
      <rect x="26" y="18" width="68" height="16" rx="5" fill="#c99a5b" ${st}/>
      <rect x="30" y="30" width="60" height="78" rx="6" fill="#b8824a"/>
      <path d="M30 70 H90 V102 A6 6 0 0 1 84 108 H36 A6 6 0 0 1 30 102 Z" fill="#8f5f33"/>
      <rect x="30" y="30" width="60" height="78" rx="6" fill="none" ${st}/>
      <path d="M40 34 V104 M60 34 V104 M80 34 V104" stroke="${O}" stroke-width="2" opacity=".5"/>
      <rect x="16" y="54" width="88" height="16" fill="#1a7a4a" ${st}/>
      <path d="M16 54 h11 v8 h-11z M38 54 h11 v8 h-11z M60 54 h11 v8 h-11z M82 54 h11 v8 h-11z M27 62 h11 v8 h-11z M49 62 h11 v8 h-11z M71 62 h11 v8 h-11z M93 62 h11 v8 h-11z" fill="#0f1a14"/>
      <rect x="52" y="82" width="16" height="12" rx="3" fill="#2a2a2a" ${thin}/>
      ${hl('M36 24 H60', .55)}`),

    'cesto-de-glicinias': wrap(`
      <path d="M38 14 Q60 -4 82 14" fill="none" ${st}/>
      <path d="M20 42 H100 L90 106 H30 Z" fill="#d1a265"/>
      <path d="M20 42 H100 L90 106 H30 Z" fill="none" ${st}/>
      <path d="M26 56 H96 M29 70 H93 M32 84 H90 M34 98 H88" stroke="${O}" stroke-width="2.5" opacity=".45"/>
      <path d="M44 42 L40 106 M60 42 L60 106 M76 42 L80 106" stroke="${O}" stroke-width="2.5" opacity=".3"/>
      <rect x="16" y="36" width="88" height="12" rx="6" fill="#e6bb7f" ${st}/>
      <g fill="#b48cff" stroke="${O}" stroke-width="2">
        <circle cx="30" cy="30" r="6"/><circle cx="38" cy="22" r="6"/><circle cx="46" cy="30" r="6"/><circle cx="34" cy="40" r="5"/>
        <circle cx="86" cy="26" r="6"/><circle cx="94" cy="34" r="6"/><circle cx="78" cy="32" r="6"/><circle cx="90" cy="44" r="5"/>
      </g>
      <g fill="#dcc8ff"><circle cx="36" cy="26" r="2"/><circle cx="90" cy="30" r="2"/></g>
      <path d="M62 24 c-3 -8 6 -12 10 -6" fill="none" stroke="#3f8f45" stroke-width="3" stroke-linecap="round"/>
      ${hl('M22 40 H40', .5)}`),

    'bau-pirata': wrap(`
      <rect x="18" y="52" width="84" height="50" rx="8" fill="#b63a3a"/>
      <path d="M18 78 H102 V94 A8 8 0 0 1 94 102 H26 A8 8 0 0 1 18 94 Z" fill="#7f2525"/>
      <rect x="18" y="52" width="84" height="50" rx="8" fill="none" ${st}/>
      <path d="M18 58 A42 26 0 0 1 102 58 V64 H18 Z" fill="#d04646" ${st}/>
      <rect x="30" y="38" width="12" height="64" fill="#f2c14e" ${thin}/>
      <rect x="78" y="38" width="12" height="64" fill="#f2c14e" ${thin}/>
      <rect x="50" y="58" width="20" height="20" rx="5" fill="#f2c14e" ${thin}/>
      <circle cx="60" cy="66" r="3.5" fill="#1a1a1a"/><path d="M60 69 v5" stroke="#1a1a1a" stroke-width="3" stroke-linecap="round"/>
      <g fill="#fff"><circle cx="46" cy="90" r="4"/><circle cx="74" cy="90" r="4"/></g>
      <path d="M96 40 l4 -8 M100 48 l8 -4" stroke="#ffe08a" stroke-width="3" stroke-linecap="round"/>
      ${hl('M26 54 Q42 42 60 40', .35)}`),

    'barril-da-tripulacao': wrap(`
      <path d="M30 36 C 20 54 20 80 30 104 H90 C 100 80 100 54 90 36 Z" fill="#b57c46"/>
      <path d="M26 70 C 26 84 28 94 30 104 H90 C 92 94 94 84 94 70 Z" fill="#8a5a30"/>
      <path d="M30 36 C 20 54 20 80 30 104 H90 C 100 80 100 54 90 36 Z" fill="none" ${st}/>
      <path d="M45 38 C 40 60 40 82 45 102 M60 36 V104 M75 38 C 80 60 80 82 75 102" stroke="${O}" stroke-width="2.5" opacity=".45"/>
      <path d="M24 52 H96 M24 88 H96" stroke="#2d6cb5" stroke-width="7"/>
      <path d="M24 52 H96 M24 88 H96" stroke="${O}" stroke-width="2" opacity=".5" transform="translate(0 4)"/>
      <ellipse cx="60" cy="34" rx="36" ry="9" fill="#f2c94c" ${st}/>
      <path d="M40 30 a20 14 0 0 1 40 0 v6 h-40z" fill="#f6d86c" ${st}/>
      <path d="M40 34 h40" stroke="#d6303e" stroke-width="4"/>
      ${hl('M34 44 Q36 60 36 70', .3)}`),

    'mochila-heroi-classe-s': wrap(bag({ body:'#f6c531', shade:'#d9a21b', flap:'#e53935', strap:'#2b2b2b', pocket:'#f4f1ea', emblem: emblemHero })),

    'mochila-ciborgue': wrap(`
      <rect x="20" y="40" width="11" height="54" rx="5.5" fill="#263241" ${st}/>
      <rect x="89" y="40" width="11" height="54" rx="5.5" fill="#263241" ${st}/>
      <rect x="28" y="28" width="64" height="82" rx="14" fill="#3e8fd6"/>
      <path d="M28 70 H92 V96 A14 14 0 0 1 78 110 H42 A14 14 0 0 1 28 96 Z" fill="#2a66a8"/>
      <rect x="28" y="28" width="64" height="82" rx="14" fill="none" ${st}/>
      <path d="M36 22 H84 A10 10 0 0 1 94 32 V44 H26 V32 A10 10 0 0 1 36 22 Z" fill="#5aa9ea" ${st}/>
      <path d="M60 50 l14 8 v16 l-14 8 -14 -8 v-16z" fill="#1a2b3d" ${thin}/>
      <path d="M60 56 l9 5 v10 l-9 5 -9 -5 v-10z" fill="#3fe0ff"/>
      <circle cx="60" cy="66" r="3" fill="#ffffff"/>
      <path d="M36 88 h10 M36 94 h10 M74 88 h10 M74 94 h10" stroke="#8fd0ff" stroke-width="2.5" stroke-linecap="round"/>
      <rect x="46" y="90" width="28" height="12" rx="4" fill="#1a2b3d" ${thin}/>
      <path d="M46 14 Q60 4 74 14" fill="none" ${st}/>
      ${hl('M31 28 Q33 24 39 23 H52')}`)
  };

  /* ---------- PICARETAS ---------------------------------------------- */
  function pick({ handle, grip = '#2b2b2b', head, headDark, headExtra = '', behind = '', top = '' }){
    return `
      ${behind}
      <path d="M26 104 L74 56" stroke="${O}" stroke-width="18" stroke-linecap="round"/>
      <path d="M26 104 L74 56" stroke="${handle}" stroke-width="11" stroke-linecap="round"/>
      <path d="M32 98 L40 90 M36 102 L44 94" stroke="${grip}" stroke-width="4" stroke-linecap="round"/>
      <path d="M20 66 C 36 30, 92 16, 114 50 C 100 42, 86 44, 78 52 L 70 60 C 62 50, 44 52, 20 66 Z" fill="${head}"/>
      <path d="M20 66 C 40 56, 56 52, 70 60 L 78 52 C 86 46, 98 44, 114 50 C 104 48, 90 50, 80 56 L 70 66 C 58 60, 40 62, 20 66 Z" fill="${headDark}"/>
      <path d="M20 66 C 36 30, 92 16, 114 50 C 100 42, 86 44, 78 52 L 70 60 C 62 50, 44 52, 20 66 Z" fill="none" ${st}/>
      ${headExtra}
      ${hl('M34 50 C 48 36, 70 28, 90 32', .45)}
      ${top}`;
  }

  const PICKS = {
    'kunai-de-treino': wrap(`
      <circle cx="30" cy="96" r="10" fill="none" stroke="${O}" stroke-width="9"/>
      <circle cx="30" cy="96" r="10" fill="none" stroke="#5b6672" stroke-width="4"/>
      <path d="M36 90 L50 76" stroke="${O}" stroke-width="14" stroke-linecap="round"/>
      <path d="M36 90 L50 76" stroke="#2f3b47" stroke-width="7" stroke-linecap="round"/>
      <path d="M96 24 L62 44 L46 70 L72 56 Z" fill="#8f9ba8" ${st}/>
      <path d="M96 24 L62 44 L72 56 Z" fill="#c4ccd6"/>
      <path d="M96 24 L62 44 L46 70 L72 56 Z" fill="none" ${st}/>
      <path d="M42 86 L50 78" stroke="#4b5661" stroke-width="3" stroke-linecap="round"/>
      ${hl('M86 32 L68 44', .6)}`),

    'picareta-rasengan': wrap(`
      <path d="M26 104 L68 62" stroke="${O}" stroke-width="18" stroke-linecap="round"/>
      <path d="M26 104 L68 62" stroke="#a66a34" stroke-width="11" stroke-linecap="round"/>
      <path d="M32 98 L40 90 M36 102 L44 94" stroke="#2b2b2b" stroke-width="4" stroke-linecap="round"/>
      <circle cx="78" cy="46" r="30" fill="#7fc7ff" ${st}/>
      <circle cx="78" cy="46" r="20" fill="#c9ecff"/>
      <path d="M78 46 m-14 0 a14 14 0 0 1 28 0 a10 10 0 0 1 -20 0 a6 6 0 0 1 12 0" fill="none" stroke="#2f8fe0" stroke-width="3.5" stroke-linecap="round"/>
      <circle cx="78" cy="46" r="5" fill="#fff"/>
      <path d="M50 30 l-6 -8 M104 24 l6 -8 M110 60 l8 2" stroke="#7fc7ff" stroke-width="3.5" stroke-linecap="round"/>
      ${hl('M62 30 Q70 22 80 22', .55)}`),

    'bastao-magico': wrap(`
      <path d="M18 110 L92 36" stroke="${O}" stroke-width="18" stroke-linecap="round"/>
      <path d="M18 110 L92 36" stroke="#d83a3a" stroke-width="11" stroke-linecap="round"/>
      <path d="M18 110 L30 98" stroke="#f2c14e" stroke-width="11" stroke-linecap="round"/>
      <path d="M18 110 L30 98" stroke="${O}" stroke-width="3" stroke-linecap="round" fill="none" opacity=".4"/>
      <path d="M84 44 L96 32" stroke="#f2c14e" stroke-width="11" stroke-linecap="round"/>
      <path d="M78 50 C 86 36, 104 30, 112 42 C 104 40, 96 42, 92 46 L 88 52 Z" fill="#f2c14e" ${st}/>
      <path d="M44 86 L52 78" stroke="#8b1f1f" stroke-width="4" stroke-linecap="round"/>
      ${hl('M40 84 L76 48', .4)}
      <path d="M100 24 l4 -8 M108 32 l8 -2" stroke="#ffe08a" stroke-width="3" stroke-linecap="round"/>`),

    'picareta-kamehameha': wrap(pick({
      handle:'#2b5aa8', grip:'#f2c14e', head:'#6fd0ff', headDark:'#2f8fe0',
      headExtra:`<path d="M30 60 C 46 38, 84 28, 106 48" fill="none" stroke="#ffffff" stroke-width="5" stroke-linecap="round" opacity=".8"/>
                 <path d="M40 24 l-4 -8 M96 18 l4 -10 M114 36 l8 -4" stroke="#aee6ff" stroke-width="3.5" stroke-linecap="round"/>`,
      behind:`<circle cx="70" cy="44" r="36" fill="#6fd0ff" opacity=".18"/>`
    })),

    'lamina-das-sombras': wrap(pick({
      handle:'#1d1530', grip:'#8c5bff', head:'#2a1f45', headDark:'#160f29',
      headExtra:`<path d="M24 64 C 42 36, 88 22, 110 48" fill="none" stroke="#b07dff" stroke-width="4" stroke-linecap="round" opacity=".9"/>`,
      behind:`<path d="M20 72 Q 60 90 110 60" fill="none" stroke="#8c5bff" stroke-width="3" stroke-linecap="round" opacity=".45"/>`
    })),

    'picareta-i-am-atomic': wrap(pick({
      handle:'#241a3e', grip:'#5a3fb0', head:'#3b2a66', headDark:'#241a3e',
      headExtra:`<circle cx="70" cy="44" r="7" fill="#d9c4ff" ${thin}/>`,
      behind:`<ellipse cx="70" cy="44" rx="42" ry="16" fill="none" stroke="#8c5bff" stroke-width="3" transform="rotate(-30 70 44)" opacity=".8"/>
              <ellipse cx="70" cy="44" rx="42" ry="16" fill="none" stroke="#5fd3ff" stroke-width="3" transform="rotate(30 70 44)" opacity=".8"/>
              <circle cx="70" cy="44" r="44" fill="#8c5bff" opacity=".12"/>`
    })),

    'picareta-nichirin': wrap(pick({
      handle:'#1a1a1a', grip:'#1a7a4a', head:'#1f2430', headDark:'#101319',
      headExtra:`<path d="M24 64 C 42 38, 86 24, 110 48" fill="none" stroke="#e53935" stroke-width="4" stroke-linecap="round"/>
                 <path d="M24 64 C 42 38, 86 24, 110 48" fill="none" stroke="#ff8a7a" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>
                 <path d="M30 100 h8 v8 h-8z M42 88 h8 v8 h-8z" fill="#1a7a4a"/>`
    })),

    'picareta-respiracao-do-sol': wrap(pick({
      handle:'#4a2a1a', grip:'#f2c14e', head:'#ff8a2b', headDark:'#d9541c',
      headExtra:`<path d="M28 58 C 44 40, 80 28, 104 46" fill="none" stroke="#ffe08a" stroke-width="4" stroke-linecap="round"/>`,
      behind:`<path d="M40 30 c-2 -14 10 -18 10 -30 c6 10 14 14 12 26 c-2 8 -8 10 -14 10 c-6 0 -8 -2 -8 -6z" fill="#ff6a1f" ${thin}/>
              <path d="M44 24 c-1 -8 6 -10 6 -18 c4 6 8 8 7 15 c-1 5 -5 6 -8 6 c-4 0 -5 -1 -5 -3z" fill="#ffd23f"/>
              <path d="M92 22 c-2 -10 8 -14 8 -24 c5 8 12 12 10 22 c-2 6 -7 8 -12 8 c-5 0 -6 -2 -6 -6z" fill="#ff6a1f" ${thin}/>`
    })),

    'picareta-gomu-gomu': wrap(pick({
      handle:'#6b3b1c', grip:'#2d6cb5', head:'#e53935', headDark:'#a82323',
      headExtra:`<path d="M30 56 C 44 42, 72 34, 96 42" fill="none" stroke="#ff8a7a" stroke-width="4" stroke-linecap="round" opacity=".8"/>
                 <path d="M8 70 q6 -6 12 0 q6 6 12 0" fill="none" stroke="#e53935" stroke-width="3.5" stroke-linecap="round"/>`,
      top:`<ellipse cx="22" cy="104" rx="16" ry="5" fill="#f2c94c" ${thin}/>
           <path d="M12 102 a10 8 0 0 1 20 0 v2 h-20z" fill="#f6d86c" ${thin}/>
           <path d="M12 103 h20" stroke="#d6303e" stroke-width="3"/>`
    })),

    'picareta-rei-dos-piratas': wrap(pick({
      handle:'#8a1f1f', grip:'#f2c14e', head:'#f2c14e', headDark:'#c9961c',
      headExtra:`<circle cx="70" cy="46" r="6" fill="#e53935" ${thin}/>
                 <path d="M56 28 l4 -12 6 10 6 -14 6 14 6 -10 4 12z" fill="#ffe08a" ${thin}/>`,
      behind:`<circle cx="72" cy="44" r="40" fill="#f2c14e" opacity=".12"/>`
    })),

    'picareta-heroi-classe-s': wrap(pick({
      handle:'#e53935', grip:'#f4f1ea', head:'#f6c531', headDark:'#d9a21b',
      headExtra:`<path d="M64 40 l-6 11 h5 l-2 8 l7 -12 h-5z" fill="#e53935" stroke="${O}" stroke-width="1.5"/>
                 <path d="M26 64 C 44 40, 86 26, 108 48" fill="none" stroke="#e53935" stroke-width="4" stroke-linecap="round"/>`,
      behind:`<circle cx="70" cy="44" r="40" fill="#f6c531" opacity=".14"/>`
    })),

    'soco-serio': wrap(`
      <circle cx="72" cy="44" r="44" fill="#e53935" opacity=".14"/>
      <path d="M26 104 L64 66" stroke="${O}" stroke-width="18" stroke-linecap="round"/>
      <path d="M26 104 L64 66" stroke="#2b2b2b" stroke-width="11" stroke-linecap="round"/>
      <path d="M32 98 L40 90 M36 102 L44 94" stroke="#f6c531" stroke-width="4" stroke-linecap="round"/>
      <path d="M50 44 h40 a14 14 0 0 1 14 14 v16 a14 14 0 0 1 -14 14 h-30 a10 10 0 0 1 -10 -10z" fill="#e53935" ${st}/>
      <path d="M50 44 v14 a14 14 0 0 0 14 14 h10" fill="none" ${thin}/>
      <path d="M62 44 v-10 a6 6 0 0 1 12 0 v10 M74 44 v-12 a6 6 0 0 1 12 0 v12 M86 46 v-8 a6 6 0 0 1 12 0 v12" fill="#e53935" ${st}/>
      <path d="M50 58 l-8 10 a6 6 0 0 0 8 6" fill="#e53935" ${st}/>
      <path d="M110 28 l8 -8 M114 44 l10 -2 M104 18 l2 -10" stroke="#ffd23f" stroke-width="4" stroke-linecap="round"/>
      ${hl('M66 40 v-4 M78 38 v-4', .5)}`)
  };

  /* ---------- MARCAS D'ÁGUA DAS ILHAS (fundo do showcase) ------------- */
  const ISLAND_PATTERNS = {
    folha: `<svg viewBox="0 0 100 100"><path d="M50 78 C 24 78 18 48 36 36 C 54 24 74 36 70 54 C 67 66 52 68 48 58 C 46 50 54 46 58 50" fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round"/><path d="M68 56 l16 12" stroke="currentColor" stroke-width="7" stroke-linecap="round"/></svg>`,
    namek: `<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" stroke-width="6"/><path d="M50 22l8 18 20 2-15 13 5 20-18-11-18 11 5-20-15-13 20-2z" fill="currentColor"/></svg>`,
    sombras: `<svg viewBox="0 0 100 100"><path d="M60 14 a38 38 0 1 0 0 72 a28 28 0 1 1 0 -72z" fill="currentColor"/></svg>`,
    cacadores: `<svg viewBox="0 0 100 100"><g fill="currentColor"><rect x="10" y="10" width="20" height="20"/><rect x="50" y="10" width="20" height="20"/><rect x="30" y="30" width="20" height="20"/><rect x="70" y="30" width="20" height="20"/><rect x="10" y="50" width="20" height="20"/><rect x="50" y="50" width="20" height="20"/><rect x="30" y="70" width="20" height="20"/><rect x="70" y="70" width="20" height="20"/></g></svg>`,
    grandline: `<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" stroke-width="5"/><path d="M50 12 L58 50 L50 88 L42 50 Z M12 50 L50 42 L88 50 L50 58 Z" fill="currentColor"/><circle cx="50" cy="50" r="6" fill="currentColor"/></svg>`,
    cidadez: `<svg viewBox="0 0 100 100"><path d="M50 8 l34 16 v30 c0 20 -16 34 -34 40 c-18 -6 -34 -20 -34 -40 v-30z" fill="none" stroke="currentColor" stroke-width="6"/><path d="M56 26 l-18 30 h14 l-6 22 l20 -34 h-14z" fill="currentColor"/></svg>`
  };

  window.AMS_ART = { bags: BAGS, picks: PICKS, islands: ISLAND_PATTERNS };
})();
