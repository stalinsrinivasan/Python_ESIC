(function(){
if(document.getElementById('_esic_launcher')){document.getElementById('_esic_launcher').remove();return;}

function fill(w,id,val){var f=w.document.getElementById(id);if(f){f.value=val;f.dispatchEvent(new Event('change',{bubbles:true}));f.dispatchEvent(new Event('input',{bubbles:true}));}}
function clickId(w,id){var b=w.document.getElementById(id);if(b)b.click();}
function today(){var d=new Date(),dd=String(d.getDate()).padStart(2,'0'),mm=String(d.getMonth()+1).padStart(2,'0');return dd+'/'+mm+'/'+d.getFullYear();}
function waitForEl(w,id,cb,timeoutMs){var waited=0;var iv=setInterval(function(){var el;try{el=w.document.getElementById(id);}catch(e){el=null;}if(el){clearInterval(iv);cb();}else{waited+=300;if(waited>=(timeoutMs||15000)){clearInterval(iv);alert('Timed out waiting for field: '+id);}}},300);}
function waitForText(w,id,cb,timeoutMs){var waited=0;var iv=setInterval(function(){var el;try{el=w.document.getElementById(id);}catch(e){el=null;}var val=el?(('value' in el)?el.value:el.textContent):'';if(val && val.trim().length>0){clearInterval(iv);cb();}else{waited+=300;if(waited>=(timeoutMs||10000)){clearInterval(iv);alert('Timed out waiting for IP Name to load. Please check the Insurance Number and try again.');}}},300);}
function isValidDate(s){return /^\d{2}\/\d{2}\/\d{4}$/.test(s);}
function addDays(dateStr,num){var p=dateStr.split('/');var d=new Date(parseInt(p[2],10),parseInt(p[1],10)-1,parseInt(p[0],10));d.setDate(d.getDate()+num);var dd=String(d.getDate()).padStart(2,'0');var mm=String(d.getMonth()+1).padStart(2,'0');return dd+'/'+mm+'/'+d.getFullYear();}

var pages=[
  {label:'Counter Foil',url:'https://gateway.esic.gov.in/InsuranceGlobalWeb/Employee/ViewCounterFoil.aspx',after:function(w,ip){fill(w,'ctl00_HomePageContent_ctrlTextEmpeIPNo',ip);setTimeout(function(){clickId(w,'ctl00_HomePageContent_ctrlBtnShow');},500);}},
  {label:'Ledger',url:'https://gateway.esic.gov.in/InsuranceGlobalWeb/Benefits/REPORTS/editIpNumber_Leadger.aspx',after:function(w,ip){fill(w,'ctl00_HomePageContent_txtIPNo',ip);setTimeout(function(){var els=w.document.querySelectorAll('input[type=submit],input[type=button],button');for(var i=0;i<els.length;i++){if((els[i].value||els[i].textContent||'').trim()==='Submit'){els[i].click();return;}}},500);}},
  {label:'IP Contribution',url:'https://gateway.esic.gov.in/InsuranceGlobalWeb/Benefits/SuperSpeciality/IPContribution.aspx',after:function(w,ip){fill(w,'ctl00_HomePageContent_txt_ipno',ip);}},
  {label:'Certificates',url:'https://gateway.esic.gov.in/InsuranceGlobalWeb/Benefits/Certificates/View_All_Certificates.aspx',after:function(w,ip){
    fill(w,'ctl00_HomePageContent_txtIPNumber',ip);
    waitForText(w,'ctl00_HomePageContent_txtBoxIpName',function(){
      fill(w,'ctl00_HomePageContent_txtfrmDate','01/01/2010');
      fill(w,'ctl00_HomePageContent_txttoDate',today());
      setTimeout(function(){
        clickId(w,'ctl00_HomePageContent_btnSearch');
      },300);
    },10000);
  }}
];

function altCertFlow(ip,fromDate,toDate,diagnosis){
  var boDate=addDays(toDate,1);
  var w=window.open('https://gateway.esic.gov.in/InsuranceGlobalWeb/Benefits/Certificates/input_ipno_accdnt.aspx?getPage=iVtF46vN4hJ0jfDKKzOXkTmbcvGoriV0','_blank');
  waitForEl(w,'ctl00_HomePageContent_txtIpNo',function(){
    fill(w,'ctl00_HomePageContent_txtIpNo',ip);
    waitForText(w,'ctl00_HomePageContent_lblIpName',function(){
      clickId(w,'ctl00_HomePageContent_Submit');
      waitForEl(w,'ctl00_HomePageContent_txtHospName',function(){
        fill(w,'ctl00_HomePageContent_txtHospName','GH');
        var sel=w.document.getElementById('ctl00_HomePageContent_certFrom');
        if(sel){sel.value='0';sel.dispatchEvent(new Event('change',{bubbles:true}));}
        fill(w,'ctl00_HomePageContent_txtDocName','MR');
        fill(w,'ctl00_HomePageContent_txtExaminatnDate',fromDate);
        fill(w,'ctl00_HomePageContent_txtDiagnosis',diagnosis);
        fill(w,'ctl00_HomePageContent_txtIssueDate',toDate);
        fill(w,'ctl00_HomePageContent_txtBOSubmitDate',boDate);
        fill(w,'ctl00_HomePageContent_addmissionDate',fromDate);
        fill(w,'ctl00_HomePageContent_dischargeDate',toDate);
      });
    },10000);
  });
}

function imoCertFlow(ip,examDate,diagnosis){
  var nextVisit=addDays(examDate,2);
  var boDate=addDays(examDate,1);
  var w=window.open('https://gateway.esic.gov.in/InsuranceGlobalWeb/Benefits/Certificates/certificate_main.aspx','_blank');
  waitForEl(w,'ctl00_HomePageContent_txtipnumber',function(){
    fill(w,'ctl00_HomePageContent_txtipnumber',ip);
    clickId(w,'ctl00_HomePageContent_rbtncertificateissued_0');
    clickId(w,'ctl00_HomePageContent_rbtncertificatefor_0');
    setTimeout(function(){
      clickId(w,'ctl00_HomePageContent_btnSubmit');
      waitForEl(w,'ctl00_HomePageContent_txtExmDate',function(){
        fill(w,'ctl00_HomePageContent_txtExmDate',examDate);
        fill(w,'ctl00_HomePageContent_txtNxtVisitDate',nextVisit);
        fill(w,'ctl00_HomePageContent_txtBODate',boDate);
        fill(w,'ctl00_HomePageContent_txtDiagnosis',diagnosis);
        fill(w,'ctl00_HomePageContent_txtMedOfficerName','MR');
        fill(w,'ctl00_HomePageContent_txtdispLocation','Thoothukudi');
      });
    },600);
  });
}

var panel=document.createElement('div');
panel.id='_esic_launcher';
panel.style.cssText='position:fixed;top:10px;right:10px;z-index:99999;background:#1a3c6e;border:2px solid #f0a500;border-radius:8px;padding:12px;font-family:Arial,sans-serif;font-size:13px;color:white;box-shadow:0 4px 12px rgba(0,0,0,0.4);width:260px;';
panel.innerHTML='<div style="font-weight:bold;margin-bottom:8px;color:#f0a500;font-size:14px;">&#9889; ESIC Quick Launch</div>'+
'<input id="_esic_ipno" type="text" placeholder="Enter Insurance Number" style="width:100%;padding:7px;border-radius:4px;border:1px solid #ccc;font-size:13px;color:#000;box-sizing:border-box;margin-bottom:8px;">'+
'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">'+
'<button id="_esic_btn0" style="background:#2196F3;color:white;border:none;padding:7px 4px;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;">Counter Foil</button>'+
'<button id="_esic_btn1" style="background:#4CAF50;color:white;border:none;padding:7px 4px;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;">Ledger</button>'+
'<button id="_esic_btn2" style="background:#FF9800;color:white;border:none;padding:7px 4px;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;">IP Contribution</button>'+
'<button id="_esic_btn3" style="background:#9C27B0;color:white;border:none;padding:7px 4px;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;">Certificates</button>'+
'<button id="_esic_btnAlt" style="background:#795548;color:white;border:none;padding:7px 4px;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;">AE</button>'+
'<button id="_esic_btnImo" style="background:#607D8B;color:white;border:none;padding:7px 4px;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;">IMO</button>'+
'</div>'+
'<div id="_esic_altform" style="display:none;margin-top:8px;border-top:1px solid #444;padding-top:8px;">'+
'<input id="_esic_fromdate" type="text" placeholder="From Date (dd/mm/yyyy)" style="width:100%;padding:6px;border-radius:4px;border:1px solid #ccc;font-size:12px;color:#000;box-sizing:border-box;margin-bottom:6px;">'+
'<input id="_esic_todate" type="text" placeholder="To Date (dd/mm/yyyy)" style="width:100%;padding:6px;border-radius:4px;border:1px solid #ccc;font-size:12px;color:#000;box-sizing:border-box;margin-bottom:6px;">'+
'<input id="_esic_diagnosis" type="text" placeholder="Diagnosis" style="width:100%;padding:6px;border-radius:4px;border:1px solid #ccc;font-size:12px;color:#000;box-sizing:border-box;margin-bottom:6px;">'+
'<button id="_esic_btnAltGo" style="width:100%;background:#795548;color:white;border:none;padding:7px 4px;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;">Go</button>'+
'</div>'+
'<div id="_esic_imoform" style="display:none;margin-top:8px;border-top:1px solid #444;padding-top:8px;">'+
'<input id="_esic_examdate" type="text" placeholder="Date of Examination (dd/mm/yyyy)" style="width:100%;padding:6px;border-radius:4px;border:1px solid #ccc;font-size:12px;color:#000;box-sizing:border-box;margin-bottom:6px;">'+
'<input id="_esic_imodiagnosis" type="text" placeholder="Diagnosis" style="width:100%;padding:6px;border-radius:4px;border:1px solid #ccc;font-size:12px;color:#000;box-sizing:border-box;margin-bottom:6px;">'+
'<button id="_esic_btnImoGo" style="width:100%;background:#607D8B;color:white;border:none;padding:7px 4px;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;">Go</button>'+
'</div>'+
'<div style="margin-top:6px;font-size:10px;color:#aaa;text-align:center;">Click &#9889; again to close</div>';
document.body.appendChild(panel);

function go(idx){var ip=document.getElementById('_esic_ipno').value.trim();if(!ip){alert('Enter Insurance Number first');return;}var p=pages[idx];var w=window.open(p.url,'_blank');w.onload=function(){p.after(w,ip);};}

document.getElementById('_esic_btn0').addEventListener('click',function(){go(0);});
document.getElementById('_esic_btn1').addEventListener('click',function(){go(1);});
document.getElementById('_esic_btn2').addEventListener('click',function(){go(2);});
document.getElementById('_esic_btn3').addEventListener('click',function(){go(3);});

document.getElementById('_esic_btnAlt').addEventListener('click',function(){
  document.getElementById('_esic_imoform').style.display='none';
  var f=document.getElementById('_esic_altform');f.style.display=(f.style.display==='none')?'block':'none';
});
document.getElementById('_esic_btnAltGo').addEventListener('click',function(){
  var ip=document.getElementById('_esic_ipno').value.trim();
  if(!ip){alert('Enter Insurance Number first');return;}
  var fromDate=document.getElementById('_esic_fromdate').value.trim();
  var toDate=document.getElementById('_esic_todate').value.trim();
  var diagnosis=document.getElementById('_esic_diagnosis').value.trim();
  if(!isValidDate(fromDate)){alert('Enter valid From Date (dd/mm/yyyy)');return;}
  if(!isValidDate(toDate)){alert('Enter valid To Date (dd/mm/yyyy)');return;}
  if(!diagnosis){alert('Enter Diagnosis');return;}
  altCertFlow(ip,fromDate,toDate,diagnosis);
});

document.getElementById('_esic_btnImo').addEventListener('click',function(){
  document.getElementById('_esic_altform').style.display='none';
  var f=document.getElementById('_esic_imoform');f.style.display=(f.style.display==='none')?'block':'none';
});
document.getElementById('_esic_btnImoGo').addEventListener('click',function(){
  var ip=document.getElementById('_esic_ipno').value.trim();
  if(!ip){alert('Enter Insurance Number first');return;}
  var examDate=document.getElementById('_esic_examdate').value.trim();
  var diagnosis=document.getElementById('_esic_imodiagnosis').value.trim();
  if(!isValidDate(examDate)){alert('Enter valid Date of Examination (dd/mm/yyyy)');return;}
  if(!diagnosis){alert('Enter Diagnosis');return;}
  imoCertFlow(ip,examDate,diagnosis);
});
})();
