// The Last Day Inn, web layer. It only shows what the engine reports through serve.py:
// story text comes from world.json, rules from engine.py, positions from layout.json.

let W = null;         // labels, title, layout and phases (/api/world)
let state = null;     // the screen the engine reports (engine.state())
let seenNotes = 0;    // journal notes the player has seen, for the red dot
let seenItems = new Set();  // items the player has seen in the bag
let showing = null;   // the item picked in the Show flow
let busy = false;

const $ = id => document.getElementById(id);
const L = key => W.ui[key];
const fmt = (s, vals) => s.replace(/\{(\w+)\}/g, (_, k) => vals[k]);
const esc = t => t.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const rich = t => esc(t).replace(/\*\*([\s\S]+?)\*\*/g, "<strong>$1</strong>");  // **key line** in world.json
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function api(path, body) {
  const opts = body === undefined ? {} :
    { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const res = await fetch(path, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function fit() {
  $("stage").style.transform = `scale(${Math.min(innerWidth / 1600, innerHeight / 900)})`;
}

// ---------- scene ----------

function roomOf(s) { return W.layout.rooms[s.location]; }

function lightFor(s, part) {
  const room = roomOf(s);
  if (s.phase === "night" && room.night_art) return part === "room" ? "transparent" : "var(--light-night-figure)";
  return `var(--light-${s.phase})`;
}

// An image with its own time-of-day light, masked to its shape (figures and objects).
function lit(src, tint) {
  const box = document.createElement("div");
  const img = document.createElement("img");
  img.src = src; img.alt = "";
  const light = document.createElement("div");
  light.className = "figure-light";
  light.style.background = tint;
  light.style.webkitMaskImage = light.style.maskImage = `url("${src}")`;
  box.append(img, light);
  return box;
}

function propVisible(prop, s) {
  const rule = prop.show_if;
  if (!rule) return true;
  if (rule.look) return s.actions.look.some(a => a.action === "examine:" + rule.look);
  if (rule.not_carried) return !s.carried.some(c => c.id === rule.not_carried);
  return true;
}

function renderScene(s, beats) {
  const room = roomOf(s);
  const night = s.phase === "night" && room.night_art;
  $("room").src = "art/" + (night ? room.night_art : room.art);
  $("room-light").style.background = lightFor(s, "room");

  $("props").replaceChildren();
  for (const [id, p] of Object.entries(room.props || {})) {
    if (id.startsWith("_") || !propVisible(p, s)) continue;
    const box = lit("art/" + p.image, lightFor(s, "figure"));
    box.className = "prop";
    Object.assign(box.style, { left: p.center_x + "px", bottom: 900 - p.bottom_y + "px", width: p.width + "px" });
    box.querySelector("img").style.width = "100%";
    $("props").append(box);
  }

  const speech = beats.filter(b => b.type === "speech" && room.spots[b.speaker] && s.people.some(p => p.id === b.speaker));
  const speakers = speech.map(b => b.speaker);
  $("figures").replaceChildren();
  $("speech").replaceChildren();
  for (const person of s.people) {
    const spot = room.spots[person.id];
    if (!spot) continue;
    const box = lit("art/" + W.layout.figures[person.id], lightFor(s, "figure"));
    box.className = "figure" + (spot.flip ? " flip" : "") + (speakers.length && !speakers.includes(person.id) ? " muted" : "");
    Object.assign(box.style, { left: spot.center_x + "px", bottom: 900 - spot.feet_y + "px", height: spot.height + "px" });
    const tag = document.createElement("div");
    tag.className = "nametag";
    tag.style.left = spot.center_x + "px";
    tag.textContent = person.name;
    $("figures").append(box, tag);
  }
  for (const b of speech) bubble(b, room.spots[b.speaker]);
}

function bubble(beat, spot) {
  const sb = W.layout.speech_box, fw = W.layout.figure_width;
  const x0 = spot.center_x - fw / 2;
  let left = spot.speech === "left" ? x0 - sb.gap - sb.width : x0 + fw + sb.gap;
  left = Math.max(16, Math.min(1600 - 16 - sb.width, left));
  const box = document.createElement("div");
  box.className = "bubble";
  Object.assign(box.style, { left: left + "px", top: sb.top + "px", width: sb.width + "px" });
  box.classList.add(spot.speech === "left" ? "tail-right" : "tail-left");  // the arrow points back at the speaker
  $("speech").append(box);
  const lines = beat.lines || [beat.text];
  const cut = lines.indexOf("(pause)");
  const aim = () => {  // at the speaker's face, kept inside the box
    const face = spot.feet_y - spot.height * 0.9 - sb.top;
    box.style.setProperty("--tail-y", Math.max(22, Math.min(box.offsetHeight - 22, face)) + "px");
  };
  if (cut < 0) { box.innerHTML = rich(lines.join(" ")); aim(); return; }
  // The reveal: "Morning…", a pause, then the rest in the same box.
  box.innerHTML = rich(lines.slice(0, cut).join(" "));
  aim();
  setTimeout(() => { box.innerHTML += " " + rich(lines.slice(cut + 1).join(" ")); aim(); }, W.layout.reveal_pause_ms);
}

// ---------- overlays on the painting ----------

function renderHud(s, left) {
  const per = s.actions_per_phase, used = s.phase_index * per + (per - left), total = W.phases.length * per;
  let svg = '<circle cx="32" cy="32" r="28" fill="var(--paper)" stroke="var(--brass)" stroke-width="3"/>';
  for (let i = 0; i < total; i++) {
    const a = (i + 0.5) / total * 2 * Math.PI;
    const x = 32 + 21 * Math.sin(a), y = 32 - 21 * Math.cos(a);
    svg += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.2" fill="${i < used ? "var(--clock-mark-used)" : "var(--brass)"}"/>`;
  }
  const h = used / total * 2 * Math.PI;
  svg += `<line x1="32" y1="32" x2="${(32 + 17 * Math.sin(h)).toFixed(1)}" y2="${(32 - 17 * Math.cos(h)).toFixed(1)}" stroke="var(--ink)" stroke-width="3" stroke-linecap="round"/>`;
  svg += '<circle cx="32" cy="32" r="3" fill="var(--ink)"/>';
  $("clock").innerHTML = svg;
  $("time").textContent = fmt(L("status"), {
    phase: s.phase_name, left: left === 1 ? L("action_left_one") : fmt(L("actions_left"), { n: left }) });
  $("place").textContent = s.place;
}

// A button label with a red dot when something new is inside.
function labelWithDot(el, text, isNew, newText, icon = "") {
  el.innerHTML = icon + esc(text) + (isNew ? '<span class="dot"></span>' : "");
  el.setAttribute("aria-label", isNew ? newText : text);
}

function renderJournalButton(s) {
  const j = s.journal;
  $("journal-btn").hidden = !j.on;
  if (!j.on) { $("journal").hidden = true; return; }
  labelWithDot($("journal-btn"), L("web_journal"), j.count > seenNotes, L("web_journal_new"));
  if (!$("journal").hidden) openJournal(true);
}

const BAG_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" ' +
  'stroke-linejoin="round" aria-hidden="true"><path d="M9 6V5a3 3 0 0 1 6 0v1"/><path d="M5 9a3 3 0 0 1 3-3h8a3 3 0 0 1 3 3v9a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3z"/>' +
  '<path d="M8 13h8v4H8z"/></svg>';
const things = s => s.carried.concat(s.known);

function renderBagButton(s) {
  labelWithDot($("bag-btn"), L("web_bag"), things(s).some(t => !seenItems.has(t.id)), L("web_bag") + " · " + L("web_new_item"), BAG_ICON);
  if (!$("bag").hidden) openBag(true);
}

function openBag(keepOpen) {
  if (!keepOpen && !$("bag").hidden) { $("bag").hidden = true; return; }
  $("journal").hidden = true;
  const list = things(state);
  let html = `<button class="close link">${esc(L("web_close"))}</button><div class="label">${esc(L("web_bag"))}</div>`;
  if (!list.length) html += `<p class="empty">${esc(L("inventory_empty"))}</p>`;
  html += list.map(t => `<button class="item" data-id="${t.id}"><img src="art/${W.layout.items[t.id]}" alt="">` +
    `<div><b>${esc(t.name)}</b>${t.content ? `<span>${rich(t.reads ? "“" + t.content + "”" : t.content)}</span>` : ""}</div></button>`).join("");
  $("bag").innerHTML = html;
  $("bag").querySelector(".close").onclick = () => { $("bag").hidden = true; };
  $("bag").querySelectorAll(".item").forEach(b => { b.onclick = () => { $("bag").hidden = true; showItem(b.dataset.id, "look"); }; });
  $("bag").hidden = false;
  list.forEach(t => seenItems.add(t.id));
  labelWithDot($("bag-btn"), L("web_bag"), false, "", BAG_ICON);
}

function openJournal(keepOpen) {
  const j = state.journal;
  if (!keepOpen && !$("journal").hidden) { $("journal").hidden = true; return; }
  $("bag").hidden = true;
  const list = facts => facts.length ? "<ul>" + facts.map(f => `<li>${rich(f)}</li>`).join("") + "</ul>"
                                     : `<p class="empty">${esc(L("journal_today_empty"))}</p>`;
  const label = key => `<div class="label">${esc(L(key).replace(/:$/, ""))}</div>`;
  let html = `<button class="close link" aria-label="${esc(L("web_journal_close"))}">${esc(L("web_journal_close"))}</button>`;
  if (!j.count) html += `<p class="empty">${esc(L("journal_empty"))}</p>`;
  else if (j.before.length) html += label("journal_before") + list(j.before) + label("journal_today") + list(j.today);
  else html += label("journal_header") + list(j.today);
  $("journal").innerHTML = html;
  $("journal").querySelector(".close").onclick = () => { $("journal").hidden = true; };
  $("journal").hidden = false;
  seenNotes = j.count;
  labelWithDot($("journal-btn"), L("web_journal"), false, "");
}

// An item large over the scene: "new" when just found (the player reads it before anything else),
// "look" when opened from the bag, "show" while choosing who to show it to (Cancel sits in the menu).
function showItem(id, mode) {
  const card = things(state).find(t => t.id === id);
  if (!card) return Promise.resolve();
  $("showcase-img").src = "art/" + W.layout.items[id];
  $("showcase-name").textContent = (mode === "new" ? L("web_new_item") + " · " : "") + card.name;
  $("showcase-text").innerHTML = card.content ? rich(card.reads ? "“" + card.content + "”" : card.content) : "";
  const close = $("showcase-close");
  close.hidden = mode === "show";
  close.textContent = mode === "new" ? L("web_item_close") : L("web_close");
  $("showcase").hidden = false;
  if (mode !== "show") close.focus();
  return new Promise(resolve => { close.onclick = () => { $("showcase").hidden = true; resolve(); }; });
}

async function showNewItems(beats) {
  for (const b of beats) {
    if (b.type !== "item") continue;
    await showItem(b.item, "new");
    seenItems.add(b.item);  // the card already showed it, so the bag needs no dot for it
    renderBagButton(state);
  }
}

// ---------- bottom panel ----------

function renderStory(s, beats, withRoom) {
  const shown = new Set(s.people.map(p => p.id));
  let html = withRoom && s.room ? `<p class="room">${rich(s.room)}</p>` : "";
  for (const b of beats) {
    if (b.type === "speech") {
      if (!shown.has(b.speaker)) html += `<p class="said">“${rich(b.text)}”</p>`;  // speaker not on screen
      continue;
    }
    if (b.type === "item" || !b.text) continue;  // found items show as a card over the scene
    html += `<p class="${b.type === "thought" ? "thought" : ""}">${rich(b.text)}</p>`;
  }
  $("story").innerHTML = html;
  $("story").scrollTop = 0;
  const known = s.known.map(k => "“" + k.text + "”").join(" ");
  $("you-know").hidden = !known;
  $("you-know").innerHTML = known ? `<span class="label">${esc(L("you_know").split(":")[0])}</span>${rich(known)}` : "";
}

function button(text, onclick, cls = "act", thumb) {
  const b = document.createElement("button");
  b.className = cls;
  if (thumb) { const i = document.createElement("img"); i.src = "art/" + thumb; i.alt = ""; b.append(i); }
  b.append(document.createTextNode(text));
  b.onclick = onclick;
  return b;
}

function group(cls, heading, buttons, extra) {
  const g = document.createElement("div");
  g.className = "group " + cls;
  const head = document.createElement("div");
  head.className = "head";
  head.innerHTML = `<span class="label">${esc(heading)}</span>`;
  if (extra) head.append(extra);
  const list = document.createElement("div");
  list.className = "buttons";
  list.append(...buttons);
  g.append(head, list);
  return g;
}

function entryButton(e) {
  const b = button(e.label, () => act(e.action));
  if (e.done) b.classList.add("done");
  return b;
}

function renderMenu(s) {
  $("warning").hidden = !s.warning;
  $("warning").innerHTML = s.warning ? rich(s.warning) : "";
  const m = $("menu");
  m.replaceChildren();
  const a = s.actions;
  if (a.go.length) m.append(group("go", L("group_move"), a.go.map(entryButton)));
  if (a.look.length) m.append(group("look", L("group_examine"), a.look.map(entryButton)));
  if (showing) {
    const cancel = button(L("web_cancel"), () => { showing = null; $("showcase").hidden = true; renderMenu(state); }, "link");
    m.append(group("show", fmt(L("web_show_to"), { item: showing.name }),
      showing.targets.map(t => entryButton({ action: t.action, label: t.name, done: t.done })), cancel));
  } else if (a.show.length) {
    m.append(group("show", L("group_present"), a.show.map(item =>
      button(item.name, () => { showing = item; showItem(item.item, "show"); renderMenu(state); }, "act", W.layout.items[item.item]))));
  }
}

function render(s, beats, { withRoom = true, waiting = false, timeUp = waiting } = {}) {
  renderScene(s, beats);
  renderHud(s, timeUp ? 0 : s.actions_left);
  renderJournalButton(s);
  renderBagButton(s);
  renderStory(s, beats, withRoom);
  $("menu").hidden = waiting;
  $("continue-row").hidden = !waiting;
  if (waiting) $("warning").hidden = true; else renderMenu(s);
  showNewItems(beats);
}

function waitForContinue(label) {
  $("no-actions").textContent = label || "";
  $("continue").textContent = L("web_continue");
  $("continue").focus();
  return new Promise(resolve => { $("continue").onclick = () => { $("continue").onclick = null; resolve(); }; });
}

// ---------- turns ----------

async function act(action) {
  if (busy) return;
  busy = true;
  showing = null;
  $("showcase").hidden = true;
  try {
    const { state: next, turn } = await api("/api/act", { action });
    await playTurn(next, turn);
  } catch (e) {
    console.error(e);
  } finally {
    busy = false;
  }
}

async function playTurn(next, turn) {
  if (turn.midnight || turn.time_moved) {
    // Keep the scene as it was right after the action until Continue, so nobody vanishes mid-sentence.
    state = turn.held;
    render(turn.held, turn.result, { waiting: true });
    await waitForContinue(L("web_no_actions"));
    if (turn.midnight) {
      await midnight(turn.midnight);
      if (next.ended === "loop_limit") return endScreen();
    }
  }
  state = next;
  if (next.ended === "anomaly_seen") {
    render(next, next.story, { waiting: true, timeUp: false });
    await waitForContinue();
    return endScreen();
  }
  // After a new time of day, the held screen already showed the action's result and the room:
  // show only who left and what happens next.
  const fresh = turn.time_moved && !turn.midnight;
  render(next, fresh ? turn.leaves.concat(turn.after) : next.story, { withRoom: !(fresh && turn.held.room) });
}

// ---------- full-screen moments ----------

function overlay(cls, html, art) {
  const o = $("overlay");
  o.className = cls + (art ? " art" : "");
  o.style.backgroundImage = art ? `url("art/${art}")` : "";
  o.innerHTML = html;
  o.hidden = false;
  return o;
}

function overlayContinue() {
  return new Promise(resolve => {
    const b = $("overlay").querySelector(".primary");
    b.focus();
    b.onclick = resolve;
  });
}

async function midnight(m) {
  const cont = `<button class="primary">${esc(L("web_continue"))}</button>`;
  if (m.lead_in) {  // 1: the painting dims, the lead-in line in the panel
    $("dim").hidden = false;
    $("speech").replaceChildren();
    $("story").innerHTML = `<p>${rich(m.lead_in)}</p>`;
    await waitForContinue();
  }
  const word = (L("midnight_banner").match(/[A-Z]{3,}/) || ["MIDNIGHT"])[0];
  overlay("midnight", `<div class="big">${esc(word)}</div><br>${cont}`);                      // 2
  await overlayContinue();
  overlay("chime", `<img src="art/fx_midnight.png" alt=""><p class="line strong">${rich(m.text)}</p>${cont}`);  // 3
  await overlayContinue();
  overlay("wash", `<p class="line strong">${rich(m.fade)}</p>${cont}`);                         // 4
  await overlayContinue();
  $("overlay").hidden = true;
  $("dim").hidden = true;
}

function endScreen() {
  const o = overlay("ending", `
    <div class="end">
      <h2>${esc(state.end_prompt)}</h2>
      <textarea id="answer" placeholder="${esc(L("web_answer_placeholder"))}"></textarea>
      <div class="row"><span class="error" id="answer-error"></span><button class="primary" id="send">${esc(L("web_send"))}</button></div>
    </div>`, "title.png");
  o.querySelector("#answer").focus();
  o.querySelector("#answer").oninput = () => { o.querySelector("#answer-error").textContent = ""; };
  o.querySelector("#send").onclick = async () => {
    const answer = o.querySelector("#answer").value.trim();
    if (!answer) { o.querySelector("#answer-error").textContent = L("web_answer_empty"); return; }
    await api("/api/answer", { answer });
    o.querySelector(".end").innerHTML = `<h2>${esc(L("web_thanks"))}</h2>
      <div class="row"><button class="primary" id="again">${esc(L("web_play_again"))}</button></div>`;
    o.querySelector("#again").onclick = titleScreen;
  };
}

function titleScreen() {
  const o = overlay("title", `
    <div class="card">
      <h1>${esc(W.title)}</h1>
      <button class="primary" id="begin">${esc(L("web_begin"))}</button>
      <label class="toggle"><input type="checkbox" id="journal-on" checked> ${esc(L("web_journal_toggle"))}</label>
    </div>`, "title.png");
  o.querySelector("#begin").focus();
  o.querySelector("#begin").onclick = async () => {
    const data = await api("/api/new", { journal: o.querySelector("#journal-on").checked });
    state = data.state;
    seenNotes = 0;
    seenItems = new Set();
    showing = null;
    $("showcase").hidden = $("journal").hidden = $("bag").hidden = true;
    o.hidden = true;
    render(state, state.story);
  };
}

async function start() {
  fit();
  addEventListener("resize", fit);
  W = await api("/api/world");
  // Preload the paintings and figures, so a scene never appears half-drawn.
  const art = [...Object.values(W.layout.rooms).flatMap(r => [r.art, r.night_art,
    ...Object.entries(r.props || {}).filter(([k]) => !k.startsWith("_")).map(([, p]) => p.image)]),
    ...Object.values(W.layout.figures), ...Object.values(W.layout.items), "fx_midnight.png"];
  window.preloaded = art.filter(Boolean).map(f => Object.assign(new Image(), { src: "art/" + f }));
  $("journal-btn").onclick = () => openJournal(false);
  $("bag-btn").onclick = () => openBag(false);
  titleScreen();
}

start();
