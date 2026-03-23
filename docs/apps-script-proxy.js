/**
 * GW Pipeline Dashboard — Google Apps Script Proxy
 *
 * Deploy as a Web App:
 *   1. Open the POSTS_MASTER spreadsheet → Extensions → Apps Script
 *   2. Paste this code, save as "pipeline-proxy"
 *   3. Click Deploy → New deployment → Web app
 *      - Execute as: Me (rajesh@genwise.in)
 *      - Who has access: Anyone
 *   4. Copy the deployment URL
 *   5. In docs/index.html, replace DATA_URL with that URL + "?action=posts"
 */

const SHEET_NAME = "POSTS_MASTER";

function doGet(e) {
  const action = (e && e.parameter && e.parameter.action) || "posts";

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ws = ss.getSheetByName(SHEET_NAME);
  const [headers, ...rows] = ws.getDataRange().getValues();

  const posts = rows
    .map(row => {
      const obj = {};
      headers.forEach((h, i) => { obj[h] = row[i] != null ? String(row[i]) : ""; });
      return obj;
    })
    .filter(r => r.post_id);

  const output = ContentService.createTextOutput(JSON.stringify({
    updated: new Date().toISOString(),
    count: posts.length,
    posts,
  }));
  output.setMimeType(ContentService.MimeType.JSON);

  // Allow cross-origin requests from GitHub Pages
  return output;
}
