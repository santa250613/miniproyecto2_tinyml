/* Modo Cazador — app.js
   Modo Zoológico: quiz con cantos (YouTube embebido)
   Identificador IA: micrófono → MFCC en JS (metodología KWS) → modelo tfjs en modelo/ */

const AVES = [
  { id:'garrapatero-comun', nombre:'Garrapatero común', emoji:'🦃', yt:'cXy-PI2FzSg',
    dato:'Canto tipo "cacareo en cascada". Negro brillante, pico curvo. Muy común en pastizales del Valle.' },
  { id:'pellar-comun',      nombre:'Pellar común',      emoji:'🐤', yt:'FsAHVK_7mfo',
    dato:'Canto fino y repetitivo desde arbustos bajos. Muy común en jardines de Cali.' },
  { id:'pigua',             nombre:'Pigua',             emoji:'🐦', yt:'r1Hes0l5Mps',
    dato:'Canto melodioso tipo flauta. Se posa en postes y cables al atardecer.' },
  { id:'bichofue-griton',   nombre:'Bichofué gritón',   emoji:'🪶', yt:'Nb5J-ZJmBl0',
    dato:'El gritón del barrio: "quis-kis-kis" fuerte desde cables. Pechos amarillos, cabeza oscura.' },
  { id:'azulejo-comun',     nombre:'Azulejo común',     emoji:'🩵', yt:'xMFmLZLevJY',
    dato:'Chirridos cortos y agudos en bandadas. Azul-gris, siempre en pareja o en grupos.' },
  { id:'lora-andina',       nombre:'Lora andina',       emoji:'🦜', yt:'uJaGIdL4ZSQ',
    dato:'Voces ásperas y escandalosas en vuelo en parejas. Verde con cabeza gris.' },
];

/* ---------------- utilidades ---------------- */
const $ = s => document.querySelector(s);
const shuffle = a => a.map(v=>[Math.random(),v]).sort((x,y)=>x[0]-y[0]).map(p=>p[1]);

/* ---------------- pestañas ---------------- */
$('#tab-quiz').onclick = ()=>{ $('#pane-quiz').classList.remove('oculto'); $('#pane-id').classList.add('oculto');
  $('#tab-quiz').classList.add('activa'); $('#tab-id').classList.remove('activa'); };
$('#tab-id').onclick = ()=>{ $('#pane-id').classList.remove('oculto'); $('#pane-quiz').classList.add('oculto');
  $('#tab-id').classList.add('activa'); $('#tab-quiz').classList.remove('activa'); };

/* ================= MODO ZOOLÓGICO ================= */
let aciertos=0, fallos=0, racha=0, correcta=null;

function nuevaRonda(){
  $('#destapado').classList.add('oculto'); $('#ronda').classList.remove('oculto');
  $('#feedback').classList.add('oculto'); $('#btn-siguiente').classList.add('oculto');
  correcta = AVES[Math.floor(Math.random()*AVES.length)];
  const ops = shuffle([correcta, ...shuffle(AVES.filter(a=>a!==correcta)).slice(0,3)]);
  $('#player').innerHTML = '';   // se arma al tocar
  $('#btn-tocar').disabled = false;
  $('#btn-tocar').textContent = '▶ Tocar el canto';
  const cont = $('#opciones'); cont.innerHTML='';
  ops.forEach(a=>{
    const b=document.createElement('button'); b.className='opt'; b.textContent=a.nombre;
    b.onclick=()=>responder(b,a); cont.appendChild(b);
  });
}

function responder(btn, a){
  document.querySelectorAll('.opt').forEach(x=>{x.disabled=true;
    if(x.textContent===correcta.nombre) x.classList.add('correcta');});
  if(a.id===correcta.id){ aciertos++; racha++; }
  else { fallos++; racha=0; btn.classList.add('equivocada'); }
  $('#aciertos').textContent=aciertos; $('#fallos').textContent=fallos; $('#racha').textContent=racha;
  $('#feedback').classList.remove('oculto');
  $('#feedback').textContent = a.id===correcta.id
    ? pick(['¡Bien ahí! 🎉','¡Ese oído de cazador! 🏹','¡Correcto! 🔥'])
    : `No era esa… era el/la ${correcta.nombre}.`;
  $('#btn-siguiente').classList.remove('oculto');
}
const pick = a => a[Math.floor(Math.random()*a.length)];

// tocar el canto: iframe de YouTube (sin autoplay hasta el clic)
$('#btn-tocar').onclick = ()=>{
  $('#player').innerHTML =
    `<div class="yt-crop"><iframe width="360" height="340" class="yt-clean" src="https://www.youtube-nocookie.com/embed/${correcta.yt}?autoplay=1&controls=0&rel=0&modestbranding=1&iv_load_policy=3&disablekb=1&playsinline=1" title="canto" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>`;
  $('#btn-tocar').disabled = true;
};

$('#btn-siguiente').onclick = nuevaRonda;
$('#btn-revancha').onclick = nuevaRonda;
// ficha: ver el ave destapada tras la respuesta — se usa en responder()
function destapar(){ // disponible por si se quiere mostrar ficha completa
  const a = correcta;
  $('#ronda').classList.add('oculto'); $('#destapado').classList.remove('oculto');
  $('#ficha-emoji').textContent=a.emoji; $('#ficha-nombre').textContent=a.nombre;
  $('#ficha-dato').textContent=a.dato;
  $('#btn-ver-video').onclick=()=>window.open('https://www.youtube.com/watch?v='+a.yt,'_blank');
}
$('#btn-ver-video').addEventListener('click',()=>{});

/* ================= MFCC en JS (metodología KWS) ================= */
const SR=16000, VENTANA=400, SALTO=160, N_FRAMES=98, N_MEL=40, N_COEFS=13,
      N_FEATURES=N_FRAMES*N_COEFS;

function hz_a_mel(f){return 2595*Math.log10(1+f/700);}
function mel_a_hz(m){return 700*(Math.pow(10,m/2595)-1);}
function filtrobankMel(){
  const fb=[], fmin=50, fmax=8000, nF=257; // rfft(512) → 257 bins
  const melPts=[]; for(let m=0;m<=N_MEL+1;m++) melPts.push(mel_a_hz(hz_a_mel(fmin)+(hz_a_mel(fmax)-hz_a_mel(fmin))*m/(N_MEL+1)));
  const bins=melPts.map(f=>Math.floor((512+1)*f/SR));
  for(let m=1;m<=N_MEL;m++){
    const izq=bins[m-1], ctr=Math.max(bins[m],izq+1), der=Math.max(bins[m+1],ctr+1), fila=new Float32Array(nF);
    for(let k=izq;k<ctr;k++) fila[k]=(k-izq)/(ctr-izq);
    for(let k=ctr;k<der;k++) fila[k]=1-(k-ctr)/(der-ctr);
    fb.push(fila);
  }
  return fb;
}
const FB=filtrobankMel();
const DCT=(()=>{const m=[]; for(let k=0;k<N_COEFS;k++){const fila=new Float32Array(N_MEL);
  const c=(k===0?Math.sqrt(1/N_MEL):Math.sqrt(2/N_MEL));
  for(let n=0;n<N_MEL;n++) fila[n]=c*Math.cos(Math.PI*k*(2*n+1)/(2*N_MEL));
  m.push(fila);} return m;})();

function dftReal(x){ // |X_k|^2 para k=0..257
  const n=x.length; if(n!==512){const y=new Float32Array(512); y.set(x); x=y;}
  const out=new Float32Array(257);
  for(let k=0;k<257;k++){
    let cr=0, ci=0;
    for(let i=0;i<512;i++){const ang=2*Math.PI*k*i/512; cr+=x[i]*Math.cos(ang); ci-=x[i]*Math.sin(ang);}
    out[k]=cr*cr+ci*ci;
  }
  return out;
}
// Hasta K_VENT ventanas de ~1 s sin solaparse, las de más energía (bloques de 1000 muestras).
// Solo cuentan bloques con ≥ REL_VENT (50 %) de la energía del más fuerte (evita meter silencios).
// Igual que ventanas_app() del notebook.
const K_VENT=3, REL_VENT=0.50;
function ventanasApp(x, n=N_FRAMES*160){
  if(x.length<=n){const y=new Float32Array(n); y.set(x); return [y];}
  const paso=1000, e=[];
  for(let i=0;i+paso<=x.length;i+=paso){let s=0; for(let j=i;j<i+paso;j+=4) s+=x[j]*x[j]; e.push(s);}
  const orden=e.map((v,b)=>b).sort((a,b)=>(e[b]-e[a])||(a-b));
  const inicios=[];
  for(const b of orden){
    if(e[b]<REL_VENT*e[orden[0]]) break;
    const s=b*paso;
    if(inicios.every(t=>Math.abs(s-t)>=n)) inicios.push(s);
    if(inicios.length===K_VENT) break;
  }
  return inicios.map(s=>x.slice(s,s+n));
}
function mfccJS(x){ // x = una ventana de ~1 s (ver ventanasApp)
  // pre-énfasis
  const y=new Float32Array(x.length); y[0]=x[0];
  for(let i=1;i<x.length;i++) y[i]=x[i]-0.97*x[i-1];
  const hann=new Float32Array(VENTANA);
  for(let i=0;i<VENTANA;i++) hann[i]=0.5-0.5*Math.cos(2*Math.PI*i/VENTANA);
  const m=[];
  let frame=0;
  for(let i=0; i+VENTANA<=y.length && frame<N_FRAMES; i+=SALTO, frame++){
    const seg=new Float32Array(VENTANA);
    for(let j=0;j<VENTANA;j++) seg[j]=y[i+j]*hann[j];
    const pw=dftReal(seg), mel=new Float32Array(N_MEL);
    for(let mI=0;mI<N_MEL;mI++){let s=0; const fila=FB[mI];
      for(let k=0;k<pw.length;k++) s+=fila[k]*pw[k];
      mel[mI]=Math.log(s+1e-10);}
    const c=new Float32Array(N_COEFS);
    for(let k=0;k<N_COEFS;k++){let s=0;
      for(let nI=0;nI<N_MEL;nI++) s+=DCT[k][nI]*mel[nI];
      c[k]=s;}
    m.push(Array.from(c));
  }
  while(m.length<N_FRAMES) m.push(new Array(N_COEFS).fill(0));
  return m.slice(0,N_FRAMES).flat(); // 1.274
}

/* ================= grabación + inferencia ================= */
let modelo=null, etiquetas=null;

function cargaModelo(){
  fetch('modelo/labels.json').then(r=>{ if(!r.ok) throw 0; return r.json();})
    .then(async lbl=>{
      etiquetas=lbl;
      modelo=await tf.loadLayersModel('modelo/model.json');
      $('#estado-mic').textContent=`✅ Modelo cargado — ${lbl.clases.length} clases. ¡Lista para cazar!`;
      $('#estado-mic').className='estado ok';
    })
    .catch(()=>{ $('#estado-mic').textContent='⏳ Sin modelo todavía: entrena en Colab y descomprime modelo_aves.zip en app/modelo/. El desafío ya funciona sin modelo.';
      $('#estado-mic').className='estado warn'; });
}
cargaModelo();

const DURACION_S=7;   // segundos de grabación (los cantos necesitan tiempo para aparecer)

$('#btn-grabar').onclick = async ()=>{
  if(!navigator.mediaDevices){alert('Este navegador no da acceso al micrófono. Usa Chrome + HTTPS o localhost.');return;}
  const btn=$('#btn-grabar'); btn.disabled=true;
  try{
    // audio "crudo" como el del Nano: los filtros del celular borran parte del canto
    const stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:false,noiseSuppression:false,autoGainControl:false}});
    // 128 kbps: con la calidad por defecto (~32 kbps) la compresión borra detalle del canto
    const rec=new MediaRecorder(stream,{audioBitsPerSecond:128000}), chunks=[];
    rec.ondataavailable=e=>chunks.push(e.data);
    rec.onstop=async ()=>{
      const blob=new Blob(chunks,{type:rec.mimeType});
      const buf=await blob.arrayBuffer();
      const ctx=new (window.AudioContext||window.webkitAudioContext)({sampleRate:SR});
      const audio=await ctx.decodeAudioData(buf);
      let x=audio.getChannelData(0);
      if(audio.sampleRate!==SR){ // remuestreo lineal
        const y=new Float32Array(Math.floor(x.length*SR/audio.sampleRate));
        for(let i=0;i<y.length;i++){const p=i*audio.sampleRate/SR, i0=Math.floor(p);
          y[i]=p+1<x.length? x[i0]+(p-i0)*(x[i0+1]-x[i0]) : x[x.length-1];}
        x=y;
      }
      dibujaOnda(x); stream.getTracks().forEach(t=>t.stop());
      if(modelo && etiquetas){inferir(x);} else {
        $('#estado-mic').textContent='🎙️ Audio capturado, pero el modelo no está cargado (sube modelo_aves.zip a app/modelo/).';
      }
      btn.disabled=false; btn.textContent=`🎙️ Grabar ${DURACION_S} s`;
    };
    rec.start();
    btn.textContent=`⏺ Grabando… ${DURACION_S} s`;
    let ms=0; const t0=Date.now();
    const iv=setInterval(()=>{ms=Math.min(DURACION_S*1000,Date.now()-t0);
      btn.textContent=`⏺ Grabando… ${Math.ceil((DURACION_S*1000-ms)/1000)}s`;},100);
    setTimeout(()=>{clearInterval(iv); rec.stop();},DURACION_S*1000);
  }catch(err){ btn.disabled=false; btn.textContent=`🎙️ Grabar ${DURACION_S} s`;
    $('#estado-mic').textContent='❌ No se pudo usar el micrófono: '+(err.message||err); $('#estado-mic').className='estado warn';}
};

/* ---- plan B sin micrófono: cargar un archivo de audio (mismo pipeline) ---- */
$('#cargar-wav').onchange = async ()=>{
  const f=$('#cargar-wav').files[0]; if(!f) return;
  if(!modelo||!etiquetas){$('#estado-mic').textContent='⏳ El modelo aún no está cargado.';return;}
  try{
    const ctx=new (window.AudioContext||window.webkitAudioContext)({sampleRate:SR});
    const audio=await ctx.decodeAudioData(await f.arrayBuffer());
    let x=audio.getChannelData(0);
    if(audio.sampleRate!==SR){
      const y=new Float32Array(Math.floor(x.length*SR/audio.sampleRate));
      for(let i=0;i<y.length;i++){const p=i*audio.sampleRate/SR, i0=Math.floor(p);
        y[i]=p+1<x.length? x[i0]+(p-i0)*(x[i0+1]-x[i0]) : x[x.length-1];}
      x=y;
    }
    dibujaOnda(x); inferir(x);
  }catch(err){$('#estado-mic').textContent='❌ No se pudo leer el audio: '+(err.message||err);$('#estado-mic').className='estado warn';}
  $('#cargar-wav').value='';
};

function dibujaOnda(x){
  const c=$('#onda'), g=c.getContext('2d');
  g.fillStyle='#0b1c12'; g.fillRect(0,0,c.width,c.height);
  g.strokeStyle='#57b46f'; g.lineWidth=1; g.beginPath();
  const paso=Math.max(1,Math.floor(x.length/c.width));
  for(let i=0;i<c.width;i++){
    let v=0; for(let j=0;j<paso*4&&i*paso+j<x.length;j+=4) v=Math.max(v,Math.abs(x[i*paso+j]));
    const y=c.height/2 - v*c.height/2*(i%2?1:-1);
    i?g.lineTo(i,y):g.moveTo(i,y);
  }
  g.stroke();
}

// "Ave no registrada": gana la clase de rechazo, la mejor ave no llega al umbral, o casi no hubo sonido
const NO_REG='ave-no-registrada', UMBRAL=0.40, PICO_MIN=0.02;

async function inferir(x){
  // normalizar primero (mismo preprocesamiento del entrenamiento: cargar_wav divide por el maximo)
  let pico=0; for(let i=0;i<x.length;i++) pico=Math.max(pico,Math.abs(x[i]));
  if(pico>0){ const g=1/pico; for(let i=0;i<x.length;i++) x[i]*=g; }
  const silencio=pico<PICO_MIN;
  const mu=etiquetas.mu, sd=etiquetas.sd, nC=etiquetas.clases.length;
  const filas=ventanasApp(x).map(v=>mfccJS(v).map((f,i)=>(f-mu[i])/(sd[i]+1e-6))); // 1.274 c/u
  const t=tf.tensor2d(filas);
  const p=modelo.predict(t); t.dispose();
  const todas=(await p.data()); p.dispose();
  const probs=new Float32Array(nC);                       // promedio de las ventanas
  for(let r=0;r<filas.length;r++) for(let c=0;c<nC;c++) probs[c]+=todas[r*nC+c]/filas.length;
  let pares=etiquetas.clases.map((c,i)=>({c,p:probs[i]})).sort((a,b)=>b.p-a.p);
  const mejor=pares[0];
  const noRegistrada= silencio || mejor.c===NO_REG || mejor.p<UMBRAL;

  pares=pares.filter(({c})=>c!==NO_REG);                 // las barras solo muestran las 6 aves
  if(noRegistrada) pares=pares.map(({c})=>({c,p:0}));   // nada registrado → todas en 0
  const info=AVES.find(a=>a.id===mejor.c)||{emoji:'❓',nombre:mejor.c};
  $('#resultado').classList.remove('oculto');
  $('#veredicto-txt').textContent= noRegistrada
    ? (silencio ? '🔇 Ave no registrada — no se escuchó nada' : '🚫 Ave no registrada')
    : `Es un ${info.nombre} (${(mejor.p*100)|0}%) ${info.emoji}`;
  const cont=$('#barras'); cont.innerHTML='';
  pares.forEach(({c,p:pr})=>{
    const info2=AVES.find(a=>a.id===c)||{nombre:c,emoji:''};
    cont.insertAdjacentHTML('beforeend',
      `<div class="barra"><div class="nombre"><span>${info2.emoji} ${info2.nombre}</span><span>${(pr*100).toFixed(1)}%</span></div>
       <div class="pista"><div class="lleno" style="width:${(pr*100)|0}%"></div></div></div>`);
  });
  if(DEBUG) mostrarDiagnostico(x, probs, pico);
}

/* ---- modo diagnóstico: abrir la página con ?debug=1 (la app normal no cambia) ---- */
const DEBUG=new URLSearchParams(location.search).has('debug');
function wav16k(x){ // Float32 [-1,1] → WAV PCM 16 bits mono 16 kHz
  const b=new ArrayBuffer(44+x.length*2), v=new DataView(b), s=(o,t)=>[...t].forEach((c,i)=>v.setUint8(o+i,c.charCodeAt(0)));
  s(0,'RIFF'); v.setUint32(4,36+x.length*2,true); s(8,'WAVEfmt '); v.setUint32(16,16,true); v.setUint16(20,1,true);
  v.setUint16(22,1,true); v.setUint32(24,SR,true); v.setUint32(28,SR*2,true); v.setUint16(32,2,true); v.setUint16(34,16,true);
  s(36,'data'); v.setUint32(40,x.length*2,true);
  for(let i=0;i<x.length;i++) v.setInt16(44+i*2,Math.max(-1,Math.min(1,x[i]))*32767,true);
  return new Blob([b],{type:'audio/wav'});
}
function mostrarDiagnostico(x, probs, pico){
  const txt=`${ventanasApp(x).length} ventana(s) · `+etiquetas.clases.map((c,i)=>`${c}: ${(probs[i]*100).toFixed(1)}%`).join(' · ');
  const url=URL.createObjectURL(wav16k(x)), nombre=`grabacion_${Date.now()}.wav`;
  $('#barras').insertAdjacentHTML('beforeend',
    `<p style="font-size:.8em;opacity:.85;margin-top:.8em">🛠️ pico ${pico.toFixed(3)} · ${(x.length/SR).toFixed(1)} s<br>${txt}<br>
     <a href="${url}" download="${nombre}">⬇️ Descargar audio grabado</a></p>`);
}

/* ================= fichas del identificador ================= */
AVES.forEach(a=>{
  $('#grid-aves').insertAdjacentHTML('beforeend',
    `<div class="mini" onclick="window.open('https://www.youtube.com/watch?v=${a.yt}','_blank')">
       <div class="e">${a.emoji}</div><b>${a.nombre}</b><p>${a.dato}</p></div>`);
});

/* arranca */
nuevaRonda();
console.log('🐦 Modo Cazador listo — quiz activo; MFCC JS:', (()=>{const x=new Float32Array(16000);
  for(let i=0;i<16000;i++)x[i]=Math.sin(2*Math.PI*1200*i/16000); const f=mfccJS(x); return `${f.length} features (esperado ${N_FEATURES})`;})());