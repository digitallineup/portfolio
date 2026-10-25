/**
 * Digital Lineup lead guard (server side).
 *
 * HOW TO INSTALL (2 minutes):
 * 1. Open the "Digital Lineup Website Leads" sheet > Extensions > Apps Script.
 * 2. In the existing code, rename the line   function doPost(e) {   to   function doPostReal(e) {
 * 3. Paste this whole file BELOW the existing code. Save.
 * 4. Deploy > Manage deployments > pencil (edit) on the current web app > Version: "New version" > Deploy.
 *    The web app URL stays the same, so the website needs no change.
 *
 * WHAT IT DOES
 * - Every real form on digitallineup.com now sends a page token (_k) and timing (_ms).
 *   Bots that post straight to this URL (how the 23 Oct "JamesBic / Nokia" and
 *   25 Oct "realegkl / AliExpress" leads came in) do not have it.
 * - Spam goes to a "Spam" tab with the reason. No email alert, no row in Leads,
 *   so it never reaches the team or any ad pixel / offline conversion upload.
 * - Real leads pass straight through to your existing doPostReal(e), unchanged.
 */
var DL_TOKEN = 'dl7k2026';

function doPost(e) {
  var d = {};
  try { d = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { d = {}; }
  var why = dlSpamReason_(d);
  if (why) {
    dlLogSpam_(d, why);
    return ContentService.createTextOutput('ok');
  }
  return doPostReal(e);
}

function dlSpamReason_(d) {
  if (d._honey) return 'honeypot';
  if (d._k !== DL_TOKEN) return 'no page token (posted directly, not from the website)';
  if (Number(d._ms || 0) < 3000) return 'submitted too fast';
  if (d._spam === 'likely') return 'pattern: ' + (d._flags || '');
  var digits = String(d.phone || '').replace(/\D/g, '').length;
  if (d.phone && (digits < 10 || digits > 15)) return 'invalid phone';
  // Same email more than 3 times in an hour = flood
  var key = 'dl_' + String(d.email || '').toLowerCase();
  var c = CacheService.getScriptCache(), n = Number(c.get(key) || 0) + 1;
  c.put(key, String(n), 3600);
  if (n > 3) return 'flood';
  return '';
}

function dlLogSpam_(d, why) {
  var ss = SpreadsheetApp.getActive() || SpreadsheetApp.openById('1LVpvLL6hXSzlfrYPeBB-c3m-hWDoBUkDojoMo7UDAts');
  var sh = ss.getSheetByName('Spam') || ss.insertSheet('Spam');
  if (sh.getLastRow() === 0) sh.appendRow(['Received (PKT)', 'Reason', 'Name', 'Email', 'Phone', 'Business', 'Page', 'Raw']);
  sh.appendRow([Utilities.formatDate(new Date(), 'Asia/Karachi', 'yyyy-MM-dd HH:mm:ss'), why,
    d.name || '', d.email || '', d.phone || '', d.business || '', d.page || '', JSON.stringify(d).slice(0, 1500)]);
}
