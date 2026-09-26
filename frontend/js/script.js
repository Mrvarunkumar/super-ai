// ---------- matrix rain ----------
const canvas = document.getElementById('canvas-rain');
const ctx = canvas.getContext('2d');
function resize(){canvas.width=window.innerWidth; canvas.height=window.innerHeight;}
resize(); window.addEventListener('resize', resize);
const chars = "01ｱｲｳｴｵｶｷｸｹｺRED-SHADE";
const fontSize = 15;
let columns, drops;
function initDrops(){
  columns = Math.floor(canvas.width / fontSize);
  drops = new Array(columns).fill(1);
}
initDrops(); window.addEventListener('resize', initDrops);
function drawRain(){
  ctx.fillStyle = 'rgba(5,5,6,0.08)';
  ctx.fillRect(0,0,canvas.width,canvas.height);
  ctx.font = fontSize + 'px monospace';
  for(let i=0;i<drops.length;i++){
    const text = chars[Math.floor(Math.random()*chars.length)];
    const grad = Math.random() > 0.96 ? '#ffffff' : (Math.random()>0.5 ? '#ff1f3d' : '#7a0e1e');
    ctx.fillStyle = grad;
    ctx.fillText(text, i*fontSize, drops[i]*fontSize);
    if(drops[i]*fontSize > canvas.height && Math.random() > 0.975) drops[i]=0;
    drops[i]++;
  }
}
setInterval(drawRain, 55);

// ---------- clock ----------
function tickClock(){
  document.getElementById('clock').textContent = new Date().toLocaleTimeString();
}
tickClock(); setInterval(tickClock,1000);

// ---------- fake system metrics ----------
function jitter(el, base, range, min, max){
  let v = Math.max(min, Math.min(max, base + (Math.random()-0.5)*range));
  return Math.round(v);
}
setInterval(()=>{
  const cpu = jitter(null, 24, 20, 8, 70);
  const ram = jitter(null, 53, 12, 30, 80);
  document.getElementById('cpuVal').textContent = cpu+'%';
  document.getElementById('cpuBar').style.width = cpu+'%';
  document.getElementById('ramVal').textContent = ram+'%';
  document.getElementById('ramBar').style.width = ram+'%';
}, 2200);

// ---------- chat + avatar state ----------
const chatWindow = document.getElementById('chatWindow');
const input = document.getElementById('cmdInput');
const sendBtn = document.getElementById('sendBtn');
const micBtn = document.getElementById('micBtn');
const avatarState = document.getElementById('avatarState');
const footerLog = document.getElementById('footerLog');
const aiCoreStat = document.getElementById('aiCoreStat');
const taskN = document.getElementById('taskN');

function setState(s){
  avatarState.innerHTML = 'STATUS: <em>'+s+'</em>';
  aiCoreStat.textContent = s;
}
function addMsg(text, who){
  const div = document.createElement('div');
  div.className = 'msg '+who;
  div.innerHTML = '<span class="tag">'+(who==='ai'?'REDSHADE':'YOU')+'</span>'+text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}
const dummyReplies = [
  "Command received. Executing...",
  "Scanning network topology... done.",
  "No anomalies detected in current cycle.",
  "Task queued. I'll notify you when it completes.",
  "Accessing local tools now.",
  "Confirmed. Standing by for next instruction."
];
function handleSend(){
  const val = input.value.trim();
  if(!val) return;
  addMsg(val, 'user');
  input.value = '';
  let n = parseInt(taskN.textContent,10)+1;
  taskN.textContent = String(n).padStart(2,'0');
  setState('THINKING');
  footerLog.textContent = '> parsing: "'+val+'"_';
  setTimeout(()=>{
    setState('WORKING');
    setTimeout(()=>{
      const reply = dummyReplies[Math.floor(Math.random()*dummyReplies.length)];
      addMsg(reply, 'ai');
      setState('IDLE');
      footerLog.textContent = '> task complete. awaiting input_';
    }, 900);
  }, 700);
}
sendBtn.addEventListener('click', handleSend);
input.addEventListener('keydown', e=>{ if(e.key==='Enter') handleSend(); });
input.addEventListener('focus', ()=> setState('LISTENING'));
input.addEventListener('blur', ()=> { if(avatarState.textContent.includes('LISTENING')) setState('IDLE'); });

let micOn = false;
micBtn.addEventListener('click', ()=>{
  micOn = !micOn;
  micBtn.classList.toggle('on', micOn);
  if(micOn){
    setState('LISTENING');
    footerLog.textContent = '> mic active — listening for voice command_';
  } else {
    setState('IDLE');
    footerLog.textContent = '> mic disabled_';
  }
});