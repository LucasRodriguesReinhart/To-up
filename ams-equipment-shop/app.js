/* =====================================================================
   AMS — Equipamentos · lógica do protótipo (sem frameworks)
   Responsável por: dados fictícios, estados, seleção, compra, equipar,
   troca de categoria, teclado e feedback.
   ===================================================================== */
(function(){
  'use strict';
  const ART = window.AMS_ART;

  /* ---------- Ilhas (progressão de mundo) ----------------------------- */
  const ISLANDS = {
    folha:     { n:1, name:'Vila da Folha',       color:'#7fc24a' },
    namek:     { n:2, name:'Planeta Namekusei',   color:'#ff9b2f' },
    sombras:   { n:3, name:'Reino das Sombras',   color:'#9b6cff' },
    cacadores: { n:4, name:'Vila dos Caçadores',  color:'#ff5e6c' },
    grandline: { n:5, name:'Grand Line',          color:'#3aa0ff' },
    cidadez:   { n:6, name:'Cidade Z',            color:'#ffd23f' }
  };
  const RARITY = {
    common:'Comum', uncommon:'Incomum', rare:'Raro', epic:'Épico', legendary:'Lendário', mythic:'Mítico'
  };
  const rarityByTier = t => t<=1?'common': t<=2?'uncommon': t<=4?'rare': t<=7?'epic': t<=10?'legendary':'mythic';
  const islandByTier = t => t<=2?'folha': t<=4?'namek': t<=6?'sombras': t<=8?'cacadores': t<=10?'grandline':'cidadez';

  /* ---------- Dados fictícios ----------------------------------------- */
  function build(cat, names, stats, prices, ownedUpTo, equippedTier, newTiers, speeds, bonuses){
    return names.map((name, i) => {
      const tier = i + 1;
      return {
        id: slug(name), cat, name, tier,
        rarity: rarityByTier(tier), island: islandByTier(tier),
        stat: stats[i], price: prices[i], speed: speeds ? speeds[i] : null, bonus: bonuses ? bonuses[i] : null,
        owned: tier <= ownedUpTo, equipped: tier === equippedTier,
        isNew: newTiers.includes(tier)
      };
    });
  }
  const slug = s => s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/(^-|-$)/g,'');

  const state = {
    cat: 'mochilas',
    coins: 1850000,
    unlockedIslands: 4,       // Vila da Folha … Vila dos Caçadores
    selected: null,
    data: {
      mochilas: build('mochilas',
        ['Pergaminho Ninja','Mochila Akatsuki','Casco do Mestre Kame','Cápsula Hoi-Poi','Manto das Sombras','Baú da Shadow Garden','Caixa Nichirin','Cesto de Glicínias','Baú Pirata','Barril da Tripulação','Mochila Herói Classe S','Mochila Ciborgue'],
        [39, 90, 300, 750, 1600, 3200, 6500, 11000, 20000, 34000, 55000, 90000],
        [0, 2500, 18500, 65000, 240000, 2400000, 7500000, 18000000, 42000000, 95000000, 210000000, 480000000],
        4, 4, [7], null, [0, 0, 2, 4, 6, 8, 10, 12, 15, 18, 22, 25]),
      picaretas: build('picaretas',
        ['Kunai de Treino','Picareta Rasengan','Bastão Mágico','Picareta Kamehameha','Lâmina das Sombras','Picareta I Am Atomic','Picareta Nichirin','Picareta Respiração do Sol','Picareta Gomu Gomu','Picareta Rei dos Piratas','Picareta Herói Classe S','Soco Sério'],
        [1, 4, 12, 30, 75, 160, 320, 600, 1100, 2000, 3500, 6000],
        [0, 1800, 14000, 52000, 1200000, 3900000, 9800000, 24000000, 55000000, 120000000, 260000000, 600000000],
        4, 4, [7], [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6])
    }
  };

  const CAT = {
    mochilas:  { title:'Mochilas',  stat:'Capacidade', unit:'cap.',  icon:'#i-box',  art: ART.bags,
                 note: it => `Carrega até <b>${fmtFull(it.stat)} minérios</b> antes de precisar vender.` },
    picaretas: { title:'Picaretas', stat:'Poder',      unit:'poder', icon:'#i-bolt', art: ART.picks,
                 note: it => `Cada golpe causa <b>${fmtFull(it.stat)} de dano</b> aos minérios.` }
  };

  /* ---------- Formatação pt-BR ---------------------------------------- */
  const fmtFull = n => n.toLocaleString('pt-BR');
  function fmtShort(n){
    const f = (v, s) => (Math.round(v * 100) / 100).toLocaleString('pt-BR', { maximumFractionDigits: v < 10 ? 2 : v < 100 ? 1 : 0 }) + s;
    if (n >= 1e9) return f(n/1e9, 'B');
    if (n >= 1e6) return f(n/1e6, 'M');
    if (n >= 1e4) return Math.round(n/1e3) + 'K';
    return fmtFull(n);
  }

  /* ---------- Derivações ---------------------------------------------- */
  const items   = () => state.data[state.cat];
  const byId    = id => items().find(i => i.id === id);
  const equipped= () => items().find(i => i.equipped);
  const nextUp  = () => items().find(i => !i.owned) || null;         // próximo degrau da escada
  const isLocked= it => ISLANDS[it.island].n > state.unlockedIslands;
  const isBest  = it => it.tier === items().length;
  const ownedCount = cat => state.data[cat].filter(i => i.owned).length;
  const artOf   = it => CAT[it.cat].art[it.id] || '';

  /* ---------- DOM ----------------------------------------------------- */
  const $ = s => document.querySelector(s);
  const grid = $('#grid'), showcase = $('#showcase'), ladder = $('#ladder'), toast = $('#toast');
  const shop = $('#shop');

  /* ---------- Render: tudo -------------------------------------------- */
  function render({ swap = false, animate = true } = {}){
    document.body.dataset.cat = state.cat;
    document.querySelectorAll('.tab').forEach(t => {
      const on = t.dataset.cat === state.cat;
      t.classList.toggle('is-active', on);
      t.setAttribute('aria-selected', on);
    });
    document.querySelectorAll('.tab__count').forEach(c => c.textContent = `${ownedCount(c.dataset.count)}/12`);
    $('#collection-title').textContent = CAT[state.cat].title;
    $('#owned-count').textContent = ownedCount(state.cat);
    $('#wallet-value').textContent = fmtShort(state.coins);
    $('#hud-coins').textContent = fmtShort(state.coins);
    renderLadder();
    renderGrid(animate);
    renderShowcase(swap);
  }

  function renderLadder(){
    const nx = nextUp();
    ladder.innerHTML = items().map(it => {
      const cls = it.equipped ? 'is-equipped' : it.owned ? 'is-owned' : (nx && nx.id === it.id) ? 'is-next' : isLocked(it) ? '' : 'is-available';
      return `<li class="${cls}" title="${it.name}"></li>`;
    }).join('');
  }

  function renderGrid(animate){
    const cur = equipped(), nx = nextUp(), c = CAT[state.cat];
    grid.classList.toggle('is-static', !animate);
    grid.innerHTML = items().map((it, i) => {
      const locked = isLocked(it), isNext = nx && nx.id === it.id, sel = state.selected === it.id;
      const cls = ['tile', `r-${it.rarity}`,
        it.owned && 'is-owned', it.equipped && 'is-equipped', locked && 'is-locked',
        isNext && 'is-next', sel && 'is-selected'].filter(Boolean).join(' ');

      let flag = '';
      if (isNext) flag = `<span class="tile__flag tile__flag--next">Próximo</span>`;
      else if (it.isNew && !it.owned) flag = `<span class="tile__flag tile__flag--new">Novo</span>`;

      const seal = it.equipped ? `<span class="tile__seal"><svg><use href="#i-check"/></svg></span>`
                 : locked      ? `<span class="tile__seal"><svg><use href="#i-lock"/></svg></span>` : '';

      const delta = (!it.owned && cur && !locked) ? `<span class="tile__delta">+${fmtShort(it.stat - cur.stat)}</span>` : '';

      let right;
      if (it.equipped) right = `<span class="tile__state"><svg><use href="#i-check"/></svg>Equipado</span>`;
      else if (it.owned) right = `<span class="tile__state">Adquirido</span>`;
      else if (locked) right = `<span class="tile__state"><svg><use href="#i-lock"/></svg>Ilha ${ISLANDS[it.island].n}</span>`;
      else right = `<span class="tile__price ${it.price > state.coins ? 'is-short' : ''}"><svg><use href="#i-coin"/></svg>${fmtShort(it.price)}</span>`;

      const label = `${it.name}, nível ${it.tier}, ${c.stat} ${fmtFull(it.stat)}, ${it.equipped ? 'equipado' : it.owned ? 'adquirido' : locked ? 'bloqueado' : 'preço ' + fmtFull(it.price)}`;
      return `
        <button class="${cls}" style="--i:${i}" data-id="${it.id}" role="option" aria-selected="${sel}" aria-label="${label}">
          ${flag}
          <span class="tile__stage">
            <span class="tile__index">${String(it.tier).padStart(2,'0')}</span>
            ${seal}
            <span class="tile__shadow"></span>
            <span class="tile__art">${artOf(it)}</span>
            ${delta}
          </span>
          <span class="tile__info">
            <span class="tile__name">${it.name}</span>
            <span class="tile__row">
              <span class="tile__stat"><b>${fmtFull(it.stat)}</b><small>${c.unit}</small></span>
              ${right}
            </span>
          </span>
        </button>`;
    }).join('');
  }

  function renderShowcase(swap){
    const it = byId(state.selected); if (!it) return;
    const c = CAT[state.cat], cur = equipped(), nx = nextUp(), locked = isLocked(it), isl = ISLANDS[it.island];
    const isNext = nx && nx.id === it.id;

    showcase.className = `showcase r-${it.rarity}${locked ? ' is-locked' : ''}${swap ? ' is-swapping' : ''}`;
    showcase.style.setProperty('--island', isl.color);

    /* eyebrow: um único rótulo de contexto, nunca uma feira de badges */
    let eyebrow;
    if (it.equipped) eyebrow = `<span class="stage__eyebrow e-equipped"><svg><use href="#i-check"/></svg>Equipado</span>`;
    else if (locked) eyebrow = `<span class="stage__eyebrow e-locked"><svg><use href="#i-lock"/></svg>Bloqueado</span>`;
    else if (isNext) eyebrow = `<span class="stage__eyebrow e-next">Próximo upgrade</span>`;
    else if (it.owned) eyebrow = `<span class="stage__eyebrow e-owned"><svg><use href="#i-check"/></svg>Adquirido</span>`;
    else if (isBest(it)) eyebrow = `<span class="stage__eyebrow e-best">Melhor da categoria</span>`;
    else eyebrow = `<span class="stage__eyebrow">Disponível</span>`;

    /* comparação */
    let compare;
    if (it.equipped || !cur) {
      compare = `<div class="compare__single"><span class="compare__v">${fmtFull(it.stat)}</span><small>${it.equipped ? 'em uso agora' : ''}</small></div>`;
    } else {
      const d = it.stat - cur.stat, pct = Math.round((d / cur.stat) * 100);
      const pctLabel = pct >= 300 ? `×${(it.stat / cur.stat).toLocaleString('pt-BR', { maximumFractionDigits: 1 })} do atual` : `${d >= 0 ? '+' : '−'}${Math.abs(pct)}%`;
      compare = `
        <div class="compare">
          <div class="compare__col"><span class="compare__k">Atual</span><span class="compare__v">${fmtFull(cur.stat)}</span></div>
          <svg class="compare__arrow"><use href="#i-arrow"/></svg>
          <div class="compare__col compare__col--new"><span class="compare__k">Este item</span><span class="compare__v">${fmtFull(it.stat)}</span></div>
          <div class="delta ${d < 0 ? 'is-down' : ''}">
            <span class="delta__abs">${d >= 0 ? '+' : '−'}${fmtFull(Math.abs(d))}</span>
            <span class="delta__pct">${pctLabel}</span>
          </div>
        </div>`;
    }

    /* rodapé: preço + ação, ou atalho para o próximo */
    let footer;
    if (it.equipped) {
      footer = `<div class="seal"><svg><use href="#i-check"/></svg>Equipado</div>${nextLink(nx, cur)}`;
    } else if (it.owned) {
      footer = `<button class="btn btn--equip is-invite" id="act" type="button"><svg><use href="#i-check"/></svg>Equipar</button>`;
    } else if (locked) {
      footer = `
        <div class="price is-locked">
          <span class="price__value"><svg><use href="#i-lock"/></svg>Desbloqueie ${isl.name} · Ilha ${isl.n}</span>
          <span class="price__note"><svg class="price__coin"><use href="#i-coin"/></svg>${fmtShort(it.price)}</span>
        </div>
        <button class="btn btn--steel" id="act" type="button" aria-disabled="true"><svg><use href="#i-lock"/></svg>Bloqueado</button>`;
    } else {
      const short = it.price - state.coins;
      footer = `
        <div class="price">
          <span class="price__value"><svg><use href="#i-coin"/></svg>${fmtFull(it.price)}</span>
          ${short > 0
            ? `<span class="price__note is-short">Faltam ${fmtFull(short)}</span>`
            : `<span class="price__note">Restarão <b>${fmtShort(state.coins - it.price)}</b></span>`}
        </div>
        ${short > 0
          ? `<button class="btn btn--steel" id="act" type="button" aria-disabled="true">Moedas insuficientes</button>`
          : `<button class="btn" id="act" type="button"><svg><use href="#i-coin"/></svg>Comprar</button>`}`;
    }

    showcase.innerHTML = `
      <div class="stage">
        <div class="stage__pattern">${ART.islands[it.island]}</div>
        <div class="stage__floor"></div>
        <div class="stage__burst"></div>
        <div class="stage__art">${artOf(it)}</div>
        ${eyebrow}
        <span class="stage__rarity">${RARITY[it.rarity]}</span>
        <span class="stage__island"><i></i>${isl.name}</span>
        <span class="stage__tier">Nível <b>${String(it.tier).padStart(2,'0')}</b> / ${items().length}</span>
      </div>
      <div class="showcase__body">
        <h3 class="showcase__name">${it.name}</h3>
        <p class="showcase__sub"><b>${RARITY[it.rarity]}</b> · ${isl.name}</p>
        <div class="stat">
          <div class="stat__label"><svg><use href="${c.icon}"/></svg>${c.stat}</div>
          ${compare}
          <p class="stat__note">${c.note(it)}</p>
        </div>
        ${secondary(it, cur)}
      </div>
      <div class="showcase__footer">${footer}</div>`;
  }

  /* atributo secundário: Velocidade (picaretas) / Bônus de venda (mochilas) */
  function secondary(it, cur){
    const f1 = v => v.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    let k, v, unit, d = null;
    if (it.speed != null) { k = 'Velocidade'; v = f1(it.speed); unit = 'golpes/s'; if (cur && !it.equipped && it.speed !== cur.speed) d = `${it.speed > cur.speed ? '+' : '−'}${f1(Math.abs(it.speed - cur.speed))}`; }
    else if (it.bonus != null) { k = 'Bônus de venda'; v = `+${it.bonus}%`; unit = ''; if (cur && !it.equipped && it.bonus !== cur.bonus) d = `${it.bonus > cur.bonus ? '+' : '−'}${Math.abs(it.bonus - cur.bonus)}%`; }
    else return '';
    return `<div class="stat2"><span class="stat2__k">${k}</span><span class="stat2__v">${v}${unit ? `<small>${unit}</small>` : ''}${d ? `<em class="${d.startsWith('−') ? 'is-down' : ''}">${d}</em>` : ''}</span></div>`;
  }

  function nextLink(nx, cur){
    if (!nx) return `<p class="showcase__sub" style="text-align:center">Você possui a melhor ${state.cat === 'mochilas' ? 'mochila' : 'picareta'} do jogo.</p>`;
    const locked = isLocked(nx);
    return `
      <button class="nextlink" type="button" data-goto="${nx.id}">
        <span class="nextlink__art">${artOf(nx)}</span>
        <span class="nextlink__text">
          <span class="nextlink__k">Próximo upgrade</span>
          <span class="nextlink__v">${nx.name}<small>+${fmtShort(nx.stat - cur.stat)}</small></span>
        </span>
        <svg class="nextlink__go"><use href="${locked ? '#i-lock' : '#i-arrow'}"/></svg>
      </button>`;
  }

  /* ---------- Ações --------------------------------------------------- */
  function select(id, { swap = true } = {}){
    if (state.selected === id) return;
    state.selected = id;
    grid.querySelectorAll('.tile').forEach(t => {
      const on = t.dataset.id === id;
      t.classList.toggle('is-selected', on); t.setAttribute('aria-selected', on);
    });
    renderShowcase(swap);
  }

  function buy(it){
    if (it.owned || isLocked(it) || it.price > state.coins) return;
    state.coins -= it.price;
    it.owned = true; it.isNew = false;
    render({ animate:false });
    const w = $('#wallet'); w.classList.remove('is-spent'); void w.offsetWidth; w.classList.add('is-spent');
    showcase.classList.add('is-burst');
    const tile = grid.querySelector(`[data-id="${it.id}"]`); if (tile) tile.classList.add('is-fresh');
    say('t-gold', '#i-coin', `${it.name} adquirido!`);
  }

  function equip(it){
    if (!it.owned) return;
    items().forEach(i => i.equipped = (i.id === it.id));
    render({ animate:false });
    say('t-ok', '#i-check', `${it.name} equipado`);
  }

  function act(){
    const it = byId(state.selected); if (!it) return;
    const btn = $('#act');
    if (isLocked(it)) { shake(btn); say('t-warn', '#i-lock', `Desbloqueie ${ISLANDS[it.island].name} para comprar`); return; }
    if (!it.owned && it.price > state.coins) { shake(btn); say('t-warn', '#i-coin', `Faltam ${fmtFull(it.price - state.coins)} moedas`); return; }
    if (!it.owned) buy(it); else if (!it.equipped) equip(it);
  }
  function shake(el){ if (!el) return; el.classList.remove('is-shake'); void el.offsetWidth; el.classList.add('is-shake'); }

  let toastT;
  function say(kind, icon, text){
    toast.className = `toast ${kind} is-on`;
    toast.innerHTML = `<svg><use href="${icon}"/></svg>${text}`;
    clearTimeout(toastT); toastT = setTimeout(() => toast.classList.remove('is-on'), 2200);
  }

  function setCat(cat){
    if (state.cat === cat) return;
    state.cat = cat;
    state.selected = (nextUp() || equipped() || items()[0]).id;
    render({ swap: true });
  }

  function close(){
    shop.classList.add('is-closing');
    setTimeout(() => { shop.hidden = true; shop.classList.remove('is-closing'); $('#reopen').hidden = false; }, 220);
  }
  function open(){ $('#reopen').hidden = true; shop.hidden = false; }

  /* ---------- Eventos ------------------------------------------------- */
  grid.addEventListener('click', e => { const t = e.target.closest('.tile'); if (t) select(t.dataset.id); });
  showcase.addEventListener('click', e => {
    if (e.target.closest('#act')) act();
    const g = e.target.closest('[data-goto]'); if (g) select(g.dataset.goto);
  });
  showcase.addEventListener('animationend', e => { if (e.animationName === 'burst') showcase.classList.remove('is-burst'); if (e.animationName === 'artSwap') showcase.classList.remove('is-swapping'); });
  document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => setCat(t.dataset.cat)));
  $('#close').addEventListener('click', close);
  $('#reopen').addEventListener('click', open);

  document.addEventListener('keydown', e => {
    if (shop.hidden) { if (e.key === 'Enter') open(); return; }
    const list = items(), idx = list.findIndex(i => i.id === state.selected);
    const cols = 4;
    const go = i => { if (i >= 0 && i < list.length) { select(list[i].id); grid.querySelector(`[data-id="${list[i].id}"]`)?.scrollIntoView({ block:'nearest' }); } };
    switch (e.key) {
      case 'Escape': close(); break;
      case 'ArrowRight': go(idx + 1); e.preventDefault(); break;
      case 'ArrowLeft':  go(idx - 1); e.preventDefault(); break;
      case 'ArrowDown':  go(idx + cols); e.preventDefault(); break;
      case 'ArrowUp':    go(idx - cols); e.preventDefault(); break;
      case 'Enter': if (!e.target.closest('.tile') && !e.target.closest('button')) act(); break;
      case 'Tab': break;
      case '1': setCat('picaretas'); break;
      case '2': setCat('mochilas'); break;
    }
  });

  /* ---------- Boot ---------------------------------------------------- */
  state.selected = (nextUp() || equipped() || items()[0]).id;   // o próximo upgrade é o produto principal da tela
  render();

  // utilidades de QA (console): AMS.state, AMS.unlock(n), AMS.coins(v), AMS.select(id)
  window.AMS = {
    state, render,
    unlock: n => { state.unlockedIslands = n; render(); },
    coins: v => { state.coins = v; render(); },
    select: id => select(id, { swap:false }),
    cat: setCat, act
  };
})();
