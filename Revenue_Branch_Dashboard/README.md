**ESIC Revenue Branch Dashboard**
**Revenue Branch Dashboard V1.0 — ESIC Sub Regional Office, Tirunelveli**
          A single-file, browser-based dashboard for managing and analysing ESIC claims, employer data, and contribution records. No server or installation required — just open the HTML file in any modern browser.

Features

**1. Claims Module**

Loads claim data from 7 Excel sheets: C18 Adhoc, C18 Actuals, 45A Order, 85B Order, C18 Interest, D18 Damages
Sidebar filters for quick data slicing
Paginated table view
Pivot / Summary modal with drill-down
Export filtered data to Excel

**2. Employer Master Module**

Reads the Employer Master sheet (7th sheet) from the same Excel file
Search employer by code and name
Displays Fact Name, Branch Office, Mobile, Email, Address, Registration Status
Collapsible panel layout

**3. Adhoc & Actual Contribution Processor**

Upload a separate employer contribution Excel file
Two modes:

Adhoc — identifies missing contribution periods
Actual — generates monthly analysis, detailed breakdown, and summary statistics

Exports results as a formatted Excel file

**Tech Stack**
TechnologyUsageHTML5 + Vanilla JavaScriptCore applicationSheetJS (xlsx.full.min.js)Excel file reading and exportIBM Plex Sans / IBM Plex MonoUI fonts (Google Fonts)CSS VariablesTheming and styling

No frameworks. No backend. No installation. Runs entirely in the browser.

**How to Use**
Browser (Direct)
Download ESIC_Dashboard_V1.0.html
Open it in any modern browser (Chrome, Edge, Firefox)
Upload your Excel data file when prompted

**Desktop App (Windows EXE)**
The dashboard is also packaged as a Windows desktop application using NW.js.

Download and extract the release zip
Double-click ESIC_Dashboard.exe
Upload your Excel data file when prompted

Excel File Structure
The main Excel file must contain these sheets in order:
Sheet No.Sheet NameModule 1 C18 Adhoc Claims 2 C18 Actuals Claims 3 45A Order Claims 4 85B Order Claims 5 C18 Interest Claims 6 D18 Damages Claims 7 Employer Master

Project Structure
ESIC_Dashboard/
├── ESIC_Dashboard_V1.0.html   # Main application (single file)
├── package.json               # NW.js app config
├── rebuild.ps1                # Script to rebuild EXE after updates
└── README.md

Rebuilding the EXE (After Updates)
When you update the HTML source file, run rebuild.ps1 to regenerate the .exe:

Right-click rebuild.ps1 → Run with PowerShell
Enter the path to your updated HTML file: C:\ESIC_Dashboard\package.nw\ESIC_DASHBOARD_V1.0.html
Enter the path to your NW.js folder: C:\ESIC_Dashboard\
The updated ESIC_Dashboard.exe will be generated automatically

## Prerequisites — Install Node.js (Only for Rebuilding EXE)
> **Regular users who just want to run the dashboard can skip this section.**
> Node.js is only needed if you want to rebuild the EXE after editing the source.
### Step 1: Check if Node.js is Already Installed
Open **Command Prompt** and run:
```cmd
node -v
npm -v
```
If you see version numbers like `v20.x.x` — Node.js is already installed. Skip to the next section.
If you get `'node' is not recognized` — follow the steps below.
---

### Step 2: Download Node.js
1. Go to **https://nodejs.org**
2. Click the **"LTS"** version (recommended for most users)
3. Download the `.msi` installer for Windows
---

### Step 3: Install Node.js
1. Double-click the downloaded `.msi` file
2. Click **Next** through all steps
3. Accept the license agreement
4. Leave the default installation path as is
5. Click **Install**
6. Click **Finish**
---

### Step 4: Verify Installation
Close and reopen **Command Prompt**, then run:
```cmd
node -v
npm -v
```

You should see version numbers — Node.js is ready!
Author
Stalin Srinivasan S
ESIC Sub Regional Office, Tirunelveli, Tamil Nadu

Disclaimer
This tool is developed for internal use by ESIC Sub Regional Office, Tirunelveli. All data processing happens locally in the browser. No data is sent to any external server.
