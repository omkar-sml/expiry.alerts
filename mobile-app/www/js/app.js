// Offline storage + expiry + phone notification bar
const LS_KEY = 'expiry_alert_items_v1';
let filter = 'all';

function load(){ try{ return JSON.parse(localStorage.getItem(LS_KEY)||'[]'); } catch(e){ return []; } }
function save(arr){ localStorage.setItem(LS_KEY, JSON.stringify(arr)); }
function daysUntil(dateStr){
  const today = new Date(); today.setHours(0,0,0,0);
  const d = new Date(dateStr); d.setHours(0,0,0,0);
  return Math.round((d - today)/86400000);
}
function statusOf(days){
  if(days<0) return {label:'Expired', badge:'bg-danger', level:'danger'};
  if(days<=7) return {label:'Expiring Soon', badge:'bg-warning text-dark', level:'warning'};
  return {label:'Safe', badge:'bg-success', level:'safe'};
}
function render(){
  const data = load();
  const tbody = document.querySelector('#tbl tbody');
  const empty = document.getElementById('empty');
  tbody.innerHTML='';
  let counts={all:data.length, Safe:0, 'Expiring Soon':0, Expired:0};
  let toShow = data.filter(it=>{
    const days = daysUntil(it.expiry);
    const s = statusOf(days).label;
    counts[s] = (counts[s]||0)+1;
    return filter==='all' || s===filter;
  });
  // also count for stats
  counts['Safe'] = data.filter(it=> statusOf(daysUntil(it.expiry)).label==='Safe').length;
  counts['Expiring Soon'] = data.filter(it=> statusOf(daysUntil(it.expiry)).label==='Expiring Soon').length;
  counts['Expired'] = data.filter(it=> statusOf(daysUntil(it.expiry)).label==='Expired').length;

  document.getElementById('count').textContent = `${toShow.length} shown / ${data.length} total`;

  // stats cards
  const stats = document.getElementById('stats');
  stats.innerHTML = `
    <div class="col-6 col-lg-3"><div class="card p-3" style="border-left:4px solid #00c2a8;"><div class="small text-muted">Total</div><div class="h4 mb-0">${data.length}</div></div></div>
    <div class="col-6 col-lg-3"><div class="card p-3" style="border-left:4px solid #198754;"><div class="small text-muted">Safe</div><div class="h4 mb-0 text-success">${counts['Safe']}</div></div></div>
    <div class="col-6 col-lg-3"><div class="card p-3" style="border-left:4px solid #ffc857;"><div class="small text-muted">Expiring Soon</div><div class="h4 mb-0 text-warning">${counts['Expiring Soon']}</div></div></div>
    <div class="col-6 col-lg-3"><div class="card p-3" style="border-left:4px solid #dc3545;"><div class="small text-muted">Expired</div><div class="h4 mb-0 text-danger">${counts['Expired']}</div></div></div>
  `;

  // alert box
  const alertBox = document.getElementById('alert-box');
  if(counts['Expired']>0){
    alertBox.innerHTML = `<div class="alert alert-danger d-flex justify-content-between align-items-center"><span><i class="bi bi-exclamation-triangle-fill"></i> ${counts['Expired']} expired — do not use!</span><button class="btn btn-sm btn-danger" onclick="document.querySelector('[data-f=\\'Expired\\']').click()">View</button></div>`;
  } else if(counts['Expiring Soon']>0){
    alertBox.innerHTML = `<div class="alert alert-warning d-flex justify-content-between align-items-center"><span><i class="bi bi-clock-history"></i> ${counts['Expiring Soon']} expiring within 7 days (tomorrow counts!)</span><button class="btn btn-sm btn-warning" onclick="document.querySelector('[data-f=\\'Expiring Soon\\']').click()">View</button></div>`;
  } else {
    alertBox.innerHTML = data.length ? `<div class="alert alert-success">All good — no expiring items.</div>` : '';
  }

  if(toShow.length===0){
    empty.style.display='block';
    document.getElementById('tbl').style.display='none';
  } else {
    empty.style.display='none';
    document.getElementById('tbl').style.display='';
    toShow.sort((a,b)=> new Date(a.expiry) - new Date(b.expiry));
    toShow.forEach((it, idx)=>{
      const days = daysUntil(it.expiry);
      const s = statusOf(days);
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="small text-muted">${idx+1}</td>
        <td class="small">${it.type==='medicine'?'💊':'🥫'} ${it.type}</td>
        <td class="fw-semibold">${it.name}</td>
        <td>${it.qty}</td>
        <td class="small">${it.expiry}</td>
        <td><span class="badge ${s.badge}">${s.label} ${days<0?`(${days}d)`:days<=7?`(${days}d)`:''}</span></td>
        <td><button class="btn btn-sm btn-outline-danger" onclick="del(${it.id})"><i class="bi bi-trash"></i></button></td>
      `;
      tbody.appendChild(tr);
    });
  }
  // fire phone notification bar if needed
  maybeNotify(counts, data);
}

let notifiedSession = false;
async function maybeNotify(counts, data){
  if(counts['Expired']===0 && counts['Expiring Soon']===0) return;
  if(notifiedSession) return;
  // prefer Capacitor LocalNotifications, fallback to Web Notifications
  const expSoon = data.filter(it=> statusOf(daysUntil(it.expiry)).label==='Expiring Soon').slice(0,3);
  const expired = data.filter(it=> statusOf(daysUntil(it.expiry)).label==='Expired').slice(0,3);
  const list = [...expired, ...expSoon];
  if(list.length===0) return;

  // Try Capacitor
  if(window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.LocalNotifications){
    const {LocalNotifications} = window.Capacitor.Plugins;
    try{
      await LocalNotifications.requestPermissions();
      await LocalNotifications.schedule({
        notifications: list.map((it, i)=>({
          title: it.expiry && daysUntil(it.expiry)<0 ? `Expired: ${it.name}` : `Expiring soon: ${it.name}`,
          body: `${it.type} Qty ${it.qty} — ${statusOf(daysUntil(it.expiry)).label} on ${it.expiry} (${daysUntil(it.expiry)}d)`,
          id: 100+i,
          schedule: {at: new Date(Date.now()+ 1000 + i*1500)},
          smallIcon: "ic_stat_icon_config_sample"
        }))
      });
      notifiedSession=true;
      return;
    }catch(e){ console.log("capacitor notif fail",e); }
  }
  // Fallback Web Notifications (works in PWA on Android)
  if('Notification' in window && Notification.permission==='granted'){
    list.slice(0,2).forEach((it,i)=>{
      setTimeout(()=>{
        new Notification(it.expiry && daysUntil(it.expiry)<0 ? `Expired: ${it.name}` : `Expiring soon: ${it.name}`, {
          body: `${it.type} — ${statusOf(daysUntil(it.expiry)).label} ${it.expiry} (${daysUntil(it.expiry)}d)`,
          icon: 'icons/icon-192.png'
        });
      }, i*1200);
    });
    notifiedSession=true;
  }
}

function del(id){
  if(!confirm('Delete?')) return;
  let arr = load().filter(x=> x.id!==id);
  save(arr); render();
}

// form
document.getElementById('addForm').addEventListener('submit', async e=>{
  e.preventDefault();
  const type = document.getElementById('type').value;
  const name = document.getElementById('name').value.trim();
  const qty = parseInt(document.getElementById('qty').value,10);
  const expiry = document.getElementById('expiry').value;
  if(!name || !qty || !expiry) return;
  const arr = load();
  arr.push({id: Date.now(), type, name, qty, expiry});
  save(arr);
  e.target.reset();
  render();
  // immediate phone notify if expiring soon/expired (tomorrow = 1 day)
  const days = daysUntil(expiry);
  const s = statusOf(days);
  if(s.label!=='Safe'){
    // trigger now
    notifiedSession=false;
    maybeNotify({Expired: s.label==='Expired'?1:0, 'Expiring Soon': s.label==='Expiring Soon'?1:0}, arr);
  }
});

// filters
document.querySelectorAll('.filter').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    document.querySelectorAll('.filter').forEach(b=> b.classList.remove('btn-dark'));
    btn.classList.add('btn-dark');
    filter = btn.dataset.f;
    render();
  });
});

document.getElementById('clear').onclick=()=>{ if(confirm('Clear all?')){ localStorage.removeItem(LS_KEY); render(); }};
document.getElementById('export').onclick=()=>{
  const blob = new Blob([localStorage.getItem(LS_KEY)||'[]'], {type:'application/json'});
  const url= URL.createObjectURL(blob);
  const a=document.createElement('a'); a.href=url; a.download='expiry_alert.json'; a.click(); URL.revokeObjectURL(url);
};
document.getElementById('notify-perm').onclick= async ()=>{
  if('Notification' in window){
    const p = await Notification.requestPermission();
    if(p==='granted'){
      new Notification("EXPIRY.ALERT", {body:"Phone alerts enabled — you'll get bar notifications for tomorrow/expired even offline.", icon:'icons/icon-192.png'});
      document.getElementById('notify-perm').textContent='Alerts enabled ✓';
    } else {
      alert('Please allow notifications in browser settings.');
    }
  } else if(window.Capacitor){
    const {LocalNotifications}= window.Capacitor.Plugins;
    await LocalNotifications.requestPermissions();
    alert('Capacitor permission requested');
  } else {
    alert('Notifications not supported in this browser. Install as PWA or APK.');
  }
};
document.getElementById('test-notif').onclick=()=>{
  notifiedSession=false;
  const data=load();
  if(data.length===0){
    // demo data
    const demo = [{type:'medicine', name:'TestTomorrow', qty:1, expiry: new Date(Date.now()+86400000).toISOString().slice(0,10)}];
    if('Notification' in window && Notification.permission==='granted'){
      new Notification("Expiring soon: TestTomorrow", {body:"Medicine — Expiring Soon on tomorrow (1d) — demo phone bar", icon:'icons/icon-192.png'});
    } else {
      alert('Allow phone alerts first (top button), then test again. Demo: TestTomorrow expiring tomorrow would notify.');
    }
    return;
  }
  maybeNotify({Expired:1,'Expiring Soon':1}, data);
};

render();
// seed demo if empty
if(load().length===0){
  const today = new Date();
  const tomorrow = new Date(Date.now()+86400000).toISOString().slice(0,10);
  const in3 = new Date(Date.now()+3*86400000).toISOString().slice(0,10);
  const yesterday = new Date(Date.now()-86400000).toISOString().slice(0,10);
  const demo=[
    {id:1, type:'medicine', name:'Paracetamol', qty:10, expiry: tomorrow},
    {id:2, type:'food', name:'Milk', qty:1, expiry: in3},
    {id:3, type:'food', name:'Bread', qty:2, expiry: yesterday},
  ];
  localStorage.setItem(LS_KEY, JSON.stringify(demo));
  render();
}
