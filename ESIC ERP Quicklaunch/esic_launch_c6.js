(function(){
/* ESIC Quick Launch (Staff): Employer Code + C6 (PDF / Excel) + Be Live.
   Click the bookmarklet again to close the panel (Be Live timer keeps running). */
var old=document.getElementById('_esic_launcher');
if(old){old.remove();return;}

/* ---------- Settings ---------- */
var LIVE_MINUTES=4;
var BASE='/InsuranceGlobalWebV12/';
var C6_URL=BASE+'RevenueOne/Monthly%20Contribution/C6Register.aspx';
var C6_FROM='01/01/2010';
var LIVE_URLS=[
  BASE+'Staff/ViewEMR.aspx',
  BASE+'RevenueOne/Monthly%20Contribution/ViewContributionHistory.aspx',
  BASE+'RevenueOne/Action%20On%20Defaulter/DefaulterLetterHistory.aspx',
  BASE+'RevenueOne/Inspection%20And%20Survey/InsActionRegister.aspx'
];

/* ---------- Helpers ---------- */
function today(){var d=new Date();return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+d.getFullYear();}
function fillEl(f,val){if(!f)return;f.value=val;f.dispatchEvent(new Event('input',{bubbles:true}));f.dispatchEvent(new Event('change',{bubbles:true}));}
function vis(el){return !!(el.offsetWidth||el.offsetHeight||el.getClientRects().length);}
function waitFor(w,test,cb,failMsg,timeoutMs){
  var waited=0;
  var iv=setInterval(function(){
    var ok=false;try{ok=test();}catch(e){ok=false;}
    if(ok){clearInterval(iv);cb();}
    else{waited+=300;if(waited>=(timeoutMs||20000)){clearInterval(iv);alert(failMsg);}}
  },300);
}

/* ---------- C6 ---------- */
function c6Inputs(w){
  var all=Array.prototype.slice.call(w.document.querySelectorAll('input[type=text],input:not([type])')).filter(function(e){return !e.readOnly&&!e.disabled&&vis(e);});
  var res={code:null,from:null,to:null};
  all.forEach(function(e){
    var k=(e.id+' '+e.name).toLowerCase();
    if(!res.from&&/from|frm/.test(k))res.from=e;
    else if(!res.to&&/(^|[^a-z])(to|upto|end)[a-z]*date|todate|dtto|_to/.test(k))res.to=e;
    else if(!res.code&&/emp|code|ecode/.test(k))res.code=e;
  });
  /* fallback: order = code, from, to */
  if(!res.code&&all[0])res.code=all[0];
  if(!res.from&&all[1])res.from=all[1];
  if(!res.to&&all[2])res.to=all[2];
  return res;
}
function c6Button(w,kind){
  var re=kind==='pdf'?/pdf/i:/excel|xls/i;
  var els=w.document.querySelectorAll('input[type=submit],input[type=button],input[type=image],button,a');
  for(var i=0;i<els.length;i++){
    var t=(els[i].value||els[i].textContent||els[i].alt||els[i].title||'')+' '+(els[i].id||'');
    if(re.test(t)&&(kind!=='pdf'||!/excel|xls/i.test(t)))return els[i];
  }
  return null;
}
function runC6(kind){
  var code=document.getElementById('_esic_empcode').value.trim();
  if(!/^\d{17}$/.test(code)){alert('Employer Code must be exactly 17 digits.');return;}
  var w=window.open(C6_URL,'_blank');
  if(!w){alert('Pop-up blocked. Allow pop-ups for this site and try again.');return;}
  waitFor(w,function(){
    var i=c6Inputs(w);
    return i.code&&i.from&&i.to&&c6Button(w,kind);
  },function(){
    var i=c6Inputs(w);
    fillEl(i.code,code);
    fillEl(i.from,C6_FROM);
    fillEl(i.to,today());
    setTimeout(function(){
      var b=c6Button(w,kind);
      if(b)b.click();else alert('Print '+(kind==='pdf'?'PDF':'Excel')+' button not found on the C6 page.');
    },600);
  },'C6 page did not show the expected fields/buttons. Run the inspector on the C6 Register page and send me the report.');
}

/* ---------- Be Live (silent; button turns green while running) ---------- */
function liveTime(t){return t?new Date(t).toLocaleString():'never';}
function isLoginUrl(u){var path=u.split('?')[0];return /login/i.test(path)&&!/staff_home/i.test(path);}
function liveColor(){
  var b=document.getElementById('_esic_btnLive');
  if(b)b.style.background=window._esicLiveTimer?'#2e7d32':'#37474F';
}
function pingOne(url){
  return fetch(url,{credentials:'include',cache:'no-store'}).then(function(r){
    return {url:url,status:r.status,login:isLoginUrl(r.url)};
  }).catch(function(){return {url:url,status:0,error:true};});
}
function livePing(){
  var now=Date.now();
  var gap=window._esicLiveLastTick?(now-window._esicLiveLastTick)/60000:0;
  var slept=gap>LIVE_MINUTES*2.5;
  window._esicLiveLastTick=now;
  var chain=Promise.resolve([]);
  LIVE_URLS.forEach(function(u){chain=chain.then(function(acc){return pingOne(u).then(function(r){acc.push(r);return acc;});});});
  chain.then(function(results){
    if(results.some(function(r){return r.login;})){
      liveStop();
      alert('Be Live stopped: the ERP sent the login page.\n\nStarted: '+liveTime(window._esicLiveStarted)+
        '\nLast good ping: '+liveTime(window._esicLiveLastOk)+
        '\nNow: '+liveTime(now)+
        (slept?'\n\nThe computer was probably asleep for about '+Math.round(gap)+' minutes before this check.':'\n\nThe computer was awake, so the ERP likely has a fixed maximum session time.')+
        '\n\nPlease log in again.');
      return;
    }
    var ok=results.filter(function(r){return !r.error&&r.status>=200&&r.status<300;}).length;
    if(ok===0)liveFail('no page responded');
    else{window._esicLiveFails=0;window._esicLiveLastOk=now;}
  });
}
function liveFail(why){
  window._esicLiveFails=(window._esicLiveFails||0)+1;
  if(window._esicLiveFails>=3){
    liveStop();
    alert('Be Live stopped after 3 failed checks in a row ('+why+').\nLast good ping: '+liveTime(window._esicLiveLastOk)+'\nCheck internet or ERP site, then click Be Live again.');
  }
}
function liveStart(){
  if(window._esicLiveTimer)return;
  window._esicLiveStarted=Date.now();window._esicLiveLastOk=null;window._esicLiveFails=0;window._esicLiveLastTick=null;
  window._esicLiveTimer=setInterval(livePing,LIVE_MINUTES*60000);
  livePing();liveColor();
}
function liveStop(){
  if(window._esicLiveTimer){clearInterval(window._esicLiveTimer);window._esicLiveTimer=null;}
  liveColor();
}

/* ---------- Panel ---------- */
var btn='color:white;border:none;padding:8px 4px;border-radius:4px;cursor:pointer;font-size:12px;font-weight:bold;';
var panel=document.createElement('div');
panel.id='_esic_launcher';
panel.style.cssText='position:fixed;top:10px;right:10px;z-index:99999;background:#1a3c6e;border:2px solid #f0a500;border-radius:8px;padding:12px;font-family:Arial,sans-serif;font-size:13px;color:white;box-shadow:0 4px 12px rgba(0,0,0,0.4);width:230px;';
panel.innerHTML='<div style="font-weight:bold;margin-bottom:8px;color:#f0a500;font-size:14px;">&#9889; ESIC Quick Launch</div>'+
'<input id="_esic_empcode" type="text" inputmode="numeric" maxlength="17" placeholder="17-digit Employer Code" style="width:100%;padding:7px;border-radius:4px;border:1px solid #ccc;font-size:13px;color:#000;box-sizing:border-box;margin-bottom:8px;">'+
'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">'+
'<button id="_esic_btnC6" style="background:#1976D2;'+btn+'">C6</button>'+
'<button id="_esic_btnLive" style="background:#37474F;'+btn+'">Be Live</button>'+
'</div>'+
'<div id="_esic_c6form" style="display:none;margin-top:8px;border-top:1px solid #444;padding-top:8px;">'+
'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">'+
'<button id="_esic_c6pdf" style="background:#D32F2F;'+btn+'">PDF</button>'+
'<button id="_esic_c6xls" style="background:#388E3C;'+btn+'">Excel</button>'+
'</div></div>'+
'<div style="margin-top:6px;font-size:10px;color:#aaa;text-align:center;">Click &#9889; again to close</div>';
document.body.appendChild(panel);

document.getElementById('_esic_empcode').addEventListener('input',function(e){e.target.value=e.target.value.replace(/\D/g,'').slice(0,17);});
document.getElementById('_esic_btnC6').addEventListener('click',function(){
  var f=document.getElementById('_esic_c6form');
  f.style.display=f.style.display==='none'?'block':'none';
});
document.getElementById('_esic_c6pdf').addEventListener('click',function(){runC6('pdf');});
document.getElementById('_esic_c6xls').addEventListener('click',function(){runC6('excel');});
document.getElementById('_esic_btnLive').addEventListener('click',function(){
  if(window._esicLiveTimer)liveStop();else liveStart();
});
liveColor();
})();
