// ============================================================
//  ESIC C6 Register Auto-Downloader
//  Run this from: https://gateway.esic.gov.in/ after login
//  Navigates automatically to C6 Register and downloads PDFs
// ============================================================

(function () {

  // ── CONFIGURATION ──────────────────────────────────────────
  const FROM_DATE        = '01/01/2010';
  const LOCATION_VALUE   = '1151';   // SRO-Tirunelveli
  const ROLE_VALUE       = '2';      // Dealing Assistant (Revenue)
  const C6_PATH          = '/InsuranceGlobalWebV12/RevenueOne/Monthly%20Contribution/C6Register.aspx';
  const PORTAL_BASE      = 'https://gateway.esic.gov.in';
  const INSURANCE_SSO    = "https://sso.esic.gov.in/oauth2/rest/authz?response_type=code&client_id=INSAppClient&domain=INSDomainNew&scope=INSDomainNewRS.all&redirect=https://gateway.esic.gov.in/InsuranceGlobalWebV15/Login/StaffLogin.aspx&scope=openid profile  email&state=102345";

  // ── UTILITIES ──────────────────────────────────────────────
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function todayDate() {
    const d = new Date();
    const dd = String(d.getDate()).padStart(2, '0');
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    return dd + '/' + mm + '/' + d.getFullYear();
  }

  function waitForUrl(win, urlPart, timeoutMs = 25000) {
    return new Promise((resolve, reject) => {
      const start = Date.now();
      const check = () => {
        try {
          if (win.location.href.includes(urlPart)) return resolve();
        } catch(e) {}
        if (Date.now() - start > timeoutMs) return reject(new Error('Timeout waiting for URL: ' + urlPart));
        setTimeout(check, 500);
      };
      check();
    });
  }

  function waitForEl(win, id, timeoutMs = 15000) {
    return new Promise((resolve, reject) => {
      const start = Date.now();
      const check = () => {
        try {
          const el = win.document.getElementById(id);
          if (el) return resolve(el);
        } catch(e) {}
        if (Date.now() - start > timeoutMs) return reject(new Error('Timeout waiting for element: ' + id));
        setTimeout(check, 400);
      };
      check();
    });
  }

  function setSelect(win, id, value) {
    const el = win.document.getElementById(id);
    if (!el) throw new Error('Dropdown not found: ' + id);
    el.value = value;
    el.dispatchEvent(new win.Event('change', { bubbles: true }));
  }

  function setVal(win, id, value) {
    const el = win.document.getElementById(id);
    if (!el) throw new Error('Field not found: ' + id);
    el.dispatchEvent(new win.Event('focus', { bubbles: true }));
    try {
      const nativeSetter = Object.getOwnPropertyDescriptor(win.HTMLInputElement.prototype, 'value').set;
      nativeSetter.call(el, value);
    } catch(e) {}
    el.value = value;
    el.dispatchEvent(new win.Event('input',  { bubbles: true }));
    el.dispatchEvent(new win.Event('change', { bubbles: true }));
    el.dispatchEvent(new win.Event('blur',   { bubbles: true }));
  }

  function clickEl(win, id) {
    const el = win.document.getElementById(id);
    if (!el) throw new Error('Button not found: ' + id);
    el.click();
  }

  // ── STYLES ─────────────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = `
    #c6panel {
      position: fixed; top: 20px; right: 20px; z-index: 999999;
      background: #fff; border: 2px solid #1a5276;
      border-radius: 10px; padding: 20px; width: 350px;
      font-family: Arial, sans-serif; font-size: 13px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.35);
    }
    #c6panel h2 {
      margin: 0 0 12px 0; font-size: 15px; color: #1a5276;
      border-bottom: 1px solid #aed6f1; padding-bottom: 8px;
    }
    #c6panel label { font-weight: bold; display: block; margin-top: 10px; }
    #c6panel input[type=file] { margin-top: 5px; width: 100%; }
    #c6panel button {
      margin-top: 12px; width: 100%; padding: 9px;
      background: #1a5276; color: white; border: none;
      border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold;
    }
    #c6panel button:hover { background: #154360; }
    #c6panel button.sec { background: #888; margin-top: 6px; }
    #c6panel button.sec:hover { background: #666; }
    #c6status {
      margin-top: 12px; padding: 8px; background: #eaf4fb;
      border-radius: 5px; min-height: 40px; color: #1a5276;
      font-size: 12px; line-height: 1.6;
    }
    #c6progress { margin-top: 8px; height: 10px; background: #d5e8f7; border-radius: 5px; overflow: hidden; }
    #c6bar { height: 100%; width: 0%; background: #1a5276; transition: width 0.4s ease; }
    #c6tip { margin-top: 8px; color: #777; font-size: 11px; }
  `;
  document.head.appendChild(style);

  // ── PANEL UI ───────────────────────────────────────────────
  const panel = document.createElement('div');
  panel.id = 'c6panel';
  panel.innerHTML = `
    <h2>📋 C6 Register Downloader</h2>
    <label>Upload Excel File (.xlsx)</label>
    <input type="file" id="c6file" accept=".xlsx" />
    <div id="c6tip">📌 Sheet1 → Column A → Header: "Employer Code"</div>
    <button id="c6start">▶ Start Full Auto Download</button>
    <button class="sec" id="c6close">✖ Close</button>
    <div id="c6status">Upload your Excel and click Start.<br>⚠️ Allow popups for this site if Chrome asks!</div>
    <div id="c6progress"><div id="c6bar"></div></div>
  `;
  document.body.appendChild(panel);
  document.getElementById('c6close').onclick = () => panel.remove();

  const statusEl = document.getElementById('c6status');
  const barEl    = document.getElementById('c6bar');

  function setStatus(msg, color) {
    statusEl.innerHTML = msg;
    statusEl.style.color = color || '#1a5276';
  }

  function setProgress(done, total) {
    barEl.style.width = Math.round((done / total) * 100) + '%';
  }

  // ── EXCEL READING ──────────────────────────────────────────
  function loadXLSX() {
    return new Promise(resolve => {
      if (window.XLSX) return resolve();
      const s = document.createElement('script');
      s.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
      s.onload = resolve;
      document.head.appendChild(s);
    });
  }

  async function readEmployerCodes(file) {
    await loadXLSX();
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = e => {
        try {
          const wb   = XLSX.read(e.target.result, { type: 'array' });
          const ws   = wb.Sheets['Sheet1'];
          if (!ws) return reject(new Error('Sheet "Sheet1" not found in your Excel file.'));
          const data = XLSX.utils.sheet_to_json(ws, { header: 1 });
          let headerIdx = -1;
          for (let i = 0; i < data.length; i++) {
            if (data[i] && String(data[i][0]).trim().toLowerCase() === 'employer code') {
              headerIdx = i; break;
            }
          }
          if (headerIdx === -1) return reject(new Error('Column A header "Employer Code" not found.'));
          const codes = [];
          for (let i = headerIdx + 1; i < data.length; i++) {
            const v = data[i] && data[i][0];
            if (v !== undefined && String(v).trim() !== '') codes.push(String(v).trim());
          }
          if (codes.length === 0) return reject(new Error('No employer codes found below header.'));
          resolve(codes);
        } catch(err) { reject(err); }
      };
      reader.readAsArrayBuffer(file);
    });
  }

  // ── PHASE 1: OPEN INSURANCE POPUP ─────────────────────────
  async function openInsurancePortal() {
    setStatus('🔄 Step 1/5: Opening Insurance portal popup...');
    const insWin = window.open(
      INSURANCE_SSO,
      '_blank',
      'location=yes,height=1200,width=1200,scrollbars=yes,status=yes'
    );
    if (!insWin) {
      throw new Error(
        'Popup was blocked! ➜ Click the popup icon in Chrome address bar → "Always allow" → Try again.'
      );
    }

    setStatus('⏳ Step 2/5: Waiting for login screen to load...<br>(may take up to 30 sec)');
    await waitForUrl(insWin, 'StaffLogin.aspx', 35000);
    await sleep(2500);

    setStatus('⚙️ Step 3/5: Selecting Location & Role...');
    await waitForEl(insWin, 'ddlLocation', 10000);
    setSelect(insWin, 'ddlLocation', LOCATION_VALUE);
    await sleep(1000);

    setSelect(insWin, 'ddlRole', ROLE_VALUE);
    await sleep(600);

    clickEl(insWin, 'btnSubmit');
    setStatus('⏳ Step 4/5: Logging in, waiting for home page...');

    await waitForUrl(insWin, 'Staff_home.aspx', 35000);
    await sleep(3000);

    setStatus('🔍 Closing IP Duplication notice if visible...');
    try {
      const doc  = insWin.document;
      const btns = doc.querySelectorAll('button, input[type=button], input[type=submit], a');
      btns.forEach(btn => {
        const t = (btn.textContent || btn.value || '').trim().toLowerCase();
        if (t === 'close' || t === 'ok') {
          try { btn.click(); } catch(e) {}
        }
      });
    } catch(e) {}

    await sleep(1500);
    return insWin;
  }

  // ── PHASE 2: GO TO C6 PAGE ─────────────────────────────────
  async function goToC6(insWin) {
    setStatus('🔄 Step 5/5: Navigating to C6 Register...');
    insWin.location.href = PORTAL_BASE + C6_PATH;
    await waitForUrl(insWin, 'C6Register.aspx', 20000);
    await waitForEl(insWin, 'ctl00_HomePageContent_txtemployerCode', 12000);
    await sleep(1000);
    setStatus('✅ C6 Register page ready!', '#1a7a1a');
  }

  // ── PHASE 3: FILL & DOWNLOAD ONE CODE ─────────────────────
  //
  // ROOT CAUSE OF THE LOOP BREAK:
  // Clicking the View button triggers an ASP.NET form postback.
  // This navigates insWin (the popup) away from C6Register.aspx
  // to a PDF/report viewer page. On the next iteration, insWin
  // is stuck on the PDF and location.href reassignment is blocked
  // or races with the still-loading PDF renderer.
  //
  // FIX: Before clicking View, we hijack the ASP.NET <form>'s
  // "target" attribute to point to a fresh throwaway window.
  // The PDF postback then loads in THAT window, while insWin
  // stays untouched on C6Register.aspx — ready for the next code.
  //
  async function fillAndDownload(insWin, code, toDate) {

    // Safety net: if something unexpected navigated insWin away, reload C6
    if (!insWin.location.href.includes('C6Register.aspx')) {
      insWin.location.href = PORTAL_BASE + C6_PATH;
      await waitForUrl(insWin, 'C6Register.aspx', 20000);
      await waitForEl(insWin, 'ctl00_HomePageContent_txtemployerCode', 15000);
      await sleep(1500);
    }

    // Reset form
    try {
      clickEl(insWin, 'ctl00_HomePageContent_CtrlBtnReset');
      await sleep(900);
    } catch(e) {}

    // Fill fields
    setVal(insWin, 'ctl00_HomePageContent_txtemployerCode', code);
    await sleep(500);
    setVal(insWin, 'ctl00_HomePageContent_CtrlTxtBxFromDate', FROM_DATE);
    await sleep(500);
    setVal(insWin, 'ctl00_HomePageContent_CtrlTxtBxToDate', toDate);
    await sleep(600);

    // Sanity check
    const doc     = insWin.document;
    const empVal  = doc.getElementById('ctl00_HomePageContent_txtemployerCode')?.value;
    const fromVal = doc.getElementById('ctl00_HomePageContent_CtrlTxtBxFromDate')?.value;
    const toVal   = doc.getElementById('ctl00_HomePageContent_CtrlTxtBxToDate')?.value;
    if (!empVal || !fromVal || !toVal) {
      throw new Error('Fields not filled. emp="' + empVal + '" from="' + fromVal + '" to="' + toVal + '"');
    }

    // ── THE KEY FIX ───────────────────────────────────────────────────
    // Open a named throwaway window for the PDF to load into
    const pdfWinName = 'c6pdf_result';
    const pdfWin = window.open('about:blank', pdfWinName,
      'width=1000,height=750,scrollbars=yes,location=yes');
    if (!pdfWin) {
      throw new Error('Could not open PDF window — check popup permissions.');
    }

    // Redirect the ASP.NET form submit to that throwaway window
    const form = doc.getElementById('aspnetForm') || doc.querySelector('form');
    if (!form) throw new Error('ASP.NET <form> not found on C6 page.');
    const originalTarget = form.target;
    form.target = pdfWinName;

    // Click the View/Print button — postback goes to pdfWin, insWin stays put
    clickEl(insWin, 'ctl00_HomePageContent_CtrlBtnView');

    // Wait for PDF to fully render in the throwaway window
    await sleep(7000);

    // Restore form target for cleanliness (though we reload C6 anyway)
    try { form.target = originalTarget; } catch(e) {}

    // Close the PDF window — the download has already been triggered by the browser
    try { pdfWin.close(); } catch(e) {}

    // Small buffer before next iteration
    await sleep(500);
  }

  // ── MAIN FLOW ──────────────────────────────────────────────
  document.getElementById('c6start').onclick = async () => {
    const fileInput = document.getElementById('c6file');
    if (!fileInput.files || fileInput.files.length === 0) {
      setStatus('⚠️ Please select your Excel file first.', 'red');
      return;
    }

    // Step 1: Read Excel
    let codes;
    try {
      setStatus('📖 Reading Excel file...');
      codes = await readEmployerCodes(fileInput.files[0]);
      setStatus('✅ Found <b>' + codes.length + '</b> employer codes. Opening portal...', '#1a7a1a');
    } catch(err) {
      setStatus('❌ Excel error: ' + err.message, 'red');
      return;
    }

    // Step 2: Open portal & navigate
    let insWin;
    try {
      insWin = await openInsurancePortal();
      await goToC6(insWin);
    } catch(err) {
      setStatus('❌ Navigation failed: ' + err.message, 'red');
      return;
    }

    // Step 3: Loop all codes
    const toDate = todayDate();
    const failed = [];

    for (let i = 0; i < codes.length; i++) {
      const code = codes[i];
      setStatus(
        '⏳ Processing <b>' + (i + 1) + ' of ' + codes.length + '</b><br>' +
        '🏢 Code: <b>' + code + '</b><br>' +
        '📅 ' + FROM_DATE + ' → ' + toDate
      );
      setProgress(i, codes.length);

      try {
        await fillAndDownload(insWin, code, toDate);
        setStatus('✅ Done <b>' + (i + 1) + '/' + codes.length + '</b>: ' + code, '#1a7a1a');
      } catch(err) {
        failed.push(code);
        setStatus('⚠️ Failed for ' + code + ':<br>' + err.message + '<br>Continuing next...', 'orange');
        await sleep(1500);
      }

      await sleep(800);
    }

    setProgress(codes.length, codes.length);

    if (failed.length === 0) {
      setStatus('🎉 All <b>' + codes.length + '</b> PDFs downloaded successfully!', '#1a7a1a');
    } else {
      setStatus(
        '✅ Completed! <b>' + (codes.length - failed.length) + '</b> succeeded.<br>' +
        '❌ Failed (' + failed.length + '): ' + failed.join(', '),
        'orange'
      );
    }
  };

})();
