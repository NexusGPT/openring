import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// Two case options. Each model file holds the case, its inside parts and a US 9 ring.
// Sizes and facts: design/case/out/case_size.txt, design/case/c6/out/case_size.txt, look-notes.md, c6-notes.md.
const OPTIONS = [
  { id: '1', name: 'Soft cube', glb: '../out/case_assembly_US9.glb', params: '../out/case_params.json', pics: '../look/',
    plain: 'The finished soft cube (version C5d): one smooth crown with a thumb dimple, a bright trim line at the seam, a dark dish round the post, a framed USB-C socket and a foot ring. The lid swivels aside.',
    facts: [['Outside size', '45.4 x 45.9 x 41.4 mm'], ['Case battery', '700 mAh, 14 to 25 ring charges'], ['Circuit board', 'as designed'],
            ['Fit check, US 7 to 13', 'passes (3,447 part pairs)'], ['Room for the joystick', '1.31 mm at US 7 to 11, 1.07 at US 12, 0.51 at US 13'], ['Ring turning in its pocket', 'held: under 0.8 degrees at every size'], ['Charging pins', 'read from the ring\'s own pad positions; a moulded black pin holder on the post'], ['Still to do', 'confirm the spring pin part; the moulder\'s word on the pin holder\'s thin walls']],
    worse: 'It is still a cube. The two bars the band rests on stay visible in the dish: they are the seat that lets one post hold every size.',
    shots: [['case-closed.png', 'Closed'], ['case-open.png', 'Open, ring in'], ['case-open-empty.png', 'Open, empty'], ['case-side.png', 'Side'], ['case-underside.png', 'Underside'], ['case-post-closeup.png', 'Charging pins, cut open']],
    view: [0.95, 0.8, 1.15] },
  { id: '2', name: 'Round', glb: '../c6/out/case_assembly_US9.glb', params: '../c6/out/case_params.json', pics: '../c6/look/',
    plain: 'A circle from above with a one-arc dome, a smooth dish round the post and a hidden pivot. The lid swivels aside by 150 degrees.',
    facts: [['Outside size', '48.0 x 48.0 x 42.0 mm'], ['Case battery', '350 mAh, 8 to 12 ring charges'], ['Circuit board', 'must be laid out again (20.6 x 34.4 mm)'],
            ['Fit check, US 7 to 13', 'passes (1,810 part pairs)'], ['Ring turning in its pocket', 'fixed: at most 0.75 degrees']],
    worse: 'It is 2.5 mm wider, holds half the charges, needs a new board layout, and its straight wall makes it a drum.',
    shots: [['case-closed.png', 'Closed'], ['case-open.png', 'Open, ring in'], ['case-open-empty.png', 'Open, empty'], ['case-side.png', 'Side']],
    view: [0.95, 0.8, 1.15] },
];

const MAT = {
  silver:  () => new THREE.MeshPhysicalMaterial({ color: 0xc8cbd0, metalness: 1, roughness: 0.36, clearcoat: 0.15, clearcoatRoughness: 0.4, envMapIntensity: 1.15 }),
  polymer: () => new THREE.MeshStandardMaterial({ color: 0xeceae3, metalness: 0, roughness: 0.78, envMapIntensity: 0.7 }),
  dark:    () => new THREE.MeshStandardMaterial({ color: 0x1c1d20, metalness: 0, roughness: 0.6, envMapIntensity: 0.6 }),
  gold:    () => new THREE.MeshPhysicalMaterial({ color: 0xe0b04a, metalness: 1, roughness: 0.18, clearcoat: 0.3, envMapIntensity: 1.6 }),
  blackmetal: () => new THREE.MeshPhysicalMaterial({ color: 0x15161a, metalness: 1, roughness: 0.3, clearcoat: 0.5, clearcoatRoughness: 0.1 }),
  glass:   () => new THREE.MeshPhysicalMaterial({ color: 0x050506, metalness: 0, roughness: 0.04, clearcoat: 1, clearcoatRoughness: 0, envMapIntensity: 1.4 }),
  board:   () => new THREE.MeshStandardMaterial({ color: 0x1f5a3a, metalness: 0, roughness: 0.7 }),
  cell:    () => new THREE.MeshStandardMaterial({ color: 0x8d9299, metalness: 0.6, roughness: 0.5 }),
  chip:    () => new THREE.MeshStandardMaterial({ color: 0x202226, metalness: 0.1, roughness: 0.6 }),
  steel:   () => new THREE.MeshStandardMaterial({ color: 0x9a9da3, metalness: 1, roughness: 0.4 }),
};
// first matching prefix wins; the name is searched on the mesh and on each of its parents
const RULES = [
  ['ring_US9_glass', 'glass'], ['ring_US9_pads', 'gold'], ['ring_US9', 'blackmetal'],
  ['pin_P', 'gold'], ['pin_board', 'board'], ['main_board', 'board'], ['cell_', 'cell'],
  ['lid_seam_trim', 'steel'], ['seam_trim', 'steel'], ['liner', 'dark'], ['usb_bezel', 'dark'], ['foot', 'dark'], ['light_window', 'glass'],
  ['shell', 'silver'], ['lid', 'silver'], ['base_plate', 'silver'], ['post', 'silver'],
  ['glide_', 'polymer'], ['hinge_pivot', 'steel'], ['magnet_', 'steel'],
  ['U', 'chip'], ['L', 'chip'], ['J1', 'steel'], ['LED1', 'polymer'],
];
const SKIN = ['shell', 'lid', 'base_plate'];          // made see-through by the "See inside" switch
const WITH_LID = ['lid', 'lid_seam_trim', 'magnet_lid', 'hinge_pivot']; // turn with the lid about the pivot

const panelsEl = document.getElementById('panels');
const loader = new GLTFLoader();
const load = (url) => new Promise((res, rej) => loader.load(url, res, undefined, rej));

function seg(parent, label, options, onPick) {
  const wrap = document.createElement('div'); wrap.className = 'seg'; wrap.setAttribute('role', 'group'); wrap.setAttribute('aria-label', label);
  options.forEach((o) => {
    const b = document.createElement('button'); b.textContent = o.text; b.type = 'button';
    if (o.on) b.classList.add('on');
    b.addEventListener('click', () => { [...wrap.children].forEach(c => c.classList.remove('on')); b.classList.add('on'); onPick(o.value); });
    wrap.appendChild(b);
  });
  parent.appendChild(wrap);
  return wrap;
}

function ruleFor(o) {
  for (let p = o; p; p = p.parent) {
    const n = p.name || '';
    for (const [prefix, mat] of RULES) if (n.startsWith(prefix)) return [prefix, mat];
  }
  return ['', 'silver'];
}
function underNamed(o, names) {
  for (let p = o; p; p = p.parent) if (names.includes(p.name)) return true;
  return false;
}

function buildPanel(c) {
  const el = document.createElement('section'); el.className = 'panel';
  const facts = c.facts.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
  const shots = c.shots.map(([f, t]) => `<a href="${c.pics}${f}" target="_blank" rel="noopener"><img src="${c.pics}${f}" alt="Option ${c.id}: ${t}" loading="lazy"><span>${t}</span></a>`).join('');
  el.innerHTML = `<div class="stage"><canvas></canvas><div class="msg">Loading option ${c.id}...</div></div><div class="ctl"></div>
    <div class="info"><div class="t"><span class="badge">${c.id}</span><h2>Option ${c.id}: ${c.name}</h2></div><p>${c.plain}</p>
    <dl>${facts}</dl>
    <div class="worse"><b>Worse at:</b> ${c.worse}</div></div>
    <div class="pics">${shots}</div>`;
  panelsEl.appendChild(el);
  const canvas = el.querySelector('canvas'), msg = el.querySelector('.msg'), ctl = el.querySelector('.ctl');
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  } catch (e) {
    msg.textContent = 'This browser cannot show 3D here. The pictures below show the same option.';
    return;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  const scene = new THREE.Scene();
  const pm = new THREE.PMREMGenerator(renderer);
  scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
  const camera = new THREE.PerspectiveCamera(32, 1, 0.005, 5);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true; controls.dampingFactor = 0.08;
  const key = new THREE.DirectionalLight(0xffffff, 0.6); key.position.set(1, 2, 1.5); scene.add(key);

  const st = { lidPivot: null, lidAngle: 0, lidTarget: 0, openRad: 0, ring: null, ringLift: 0, ringTarget: 0, skins: [], ready: false };

  seg(ctl, 'Lid', [{ text: 'Lid closed', value: false, on: true }, { text: 'Lid open', value: true }], v => { st.lidTarget = v ? st.openRad : 0; });
  seg(ctl, 'Ring', [{ text: 'Ring in', value: true, on: true }, { text: 'Ring out', value: false }], v => { st.ringTarget = v ? 0 : 0.045; });
  seg(ctl, 'Skin', [{ text: 'Solid', value: false, on: true }, { text: 'See inside', value: true }], v => {
    st.skins.forEach(m => { m.transparent = v; m.opacity = v ? 0.22 : 1; m.depthWrite = !v; m.needsUpdate = true; });
  });

  Promise.all([load(c.glb), fetch(c.params).then(r => { if (!r.ok) throw new Error('case_params.json ' + r.status); return r.json(); })]).then(([g, prm]) => {
    const root = g.scene;
    scene.add(root);
    root.traverse(o => {
      if (!o.isMesh) return;
      const [prefix, mat] = ruleFor(o);
      o.material = MAT[mat]();
      if (SKIN.includes(prefix)) st.skins.push(o.material);
    });
    scene.updateMatrixWorld(true);

    // the model's own frame is Z up, in metres, under a top node that turns it to Y up.
    // The lid turns about the vertical line through the pivot, counter-clockwise seen from above (case.py).
    let lid = null;
    root.traverse(o => { if (o.name === 'lid') lid = o; if (o.name === 'ring_US9') st.ring = o; });
    if (lid && lid.parent && Array.isArray(prm.pivot)) {
      const frame = lid.parent;
      const px = prm.pivot[0] / 1000, py = prm.pivot[1] / 1000;
      const pivot = new THREE.Group(); pivot.name = 'lid_pivot';
      pivot.position.set(px, py, 0);
      frame.add(pivot);
      const movers = [];
      frame.children.forEach(ch => { if (WITH_LID.includes(ch.name)) movers.push(ch); });
      movers.forEach(ch => { pivot.add(ch); ch.position.x -= px; ch.position.y -= py; });
      st.lidPivot = pivot;
      st.openRad = THREE.MathUtils.degToRad(Number(prm.lid_open_deg) || 100);
    }

    // camera: frame the closed case
    const box = new THREE.Box3().setFromObject(root);
    const ctr = new THREE.Vector3(); box.getCenter(ctr);
    const size = new THREE.Vector3(); box.getSize(size);
    const rad = size.length() * 0.5;
    const d = rad / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * 1.25;
    const dir = new THREE.Vector3(...c.view).normalize();
    camera.position.copy(ctr).addScaledVector(dir, d);
    controls.target.copy(ctr); controls.update();
    controls.minDistance = d * 0.2; controls.maxDistance = d * 3;
    msg.remove();
    st.ready = true;
  }).catch(e => { msg.textContent = 'Could not load the 3D model (' + e.message + '). The pictures below show the same option.'; });

  function resize() {
    const r = canvas.getBoundingClientRect();
    const w = Math.floor(r.width * renderer.getPixelRatio()), h = Math.floor(r.height * renderer.getPixelRatio());
    if (canvas.width !== w || canvas.height !== h) {
      renderer.setSize(r.width, r.height, false); camera.aspect = r.width / Math.max(r.height, 1); camera.updateProjectionMatrix();
    }
  }
  function frame() {
    resize();
    if (st.lidPivot) { st.lidAngle += (st.lidTarget - st.lidAngle) * 0.1; st.lidPivot.rotation.z = st.lidAngle; }
    if (st.ring) { st.ringLift += (st.ringTarget - st.ringLift) * 0.12; st.ring.position.z = st.ringLift; }
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  frame();
}

OPTIONS.forEach(buildPanel);
