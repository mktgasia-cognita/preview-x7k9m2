(function() {
  var reports = [{"filename": "sais-meta-ads-mar18-apr12.html", "dates": "Mar 18 - Apr 12, 2026"}, {"filename": "sais-meta-ads-apr5-apr11.html", "dates": "Apr 5 - 11, 2026"}, {"filename": "sais-meta-ads-apr12-apr18.html", "dates": "Apr 12 - 18, 2026"}, {"filename": "sais-meta-ads-apr19-apr25.html", "dates": "Apr 19 - 25, 2026"}, {"filename": "sais-meta-ads-apr26-may2.html", "dates": "Apr 26 - May 2, 2026"}, {"filename": "sais-meta-ads-may3-may9.html", "dates": "May 3 - 9, 2026"}, {"filename": "sais-meta-ads-may10-may16.html", "dates": "May 10 - 16, 2026"}, {"filename": "sais-meta-ads-may24-may30.html", "dates": "May 24 - 30, 2026"}, {"filename": "sais-meta-ads-may31-jun6.html", "dates": "May 31 - Jun 6, 2026"}, {"filename": "sais-meta-ads-jun7-jun13.html", "dates": "Jun 7 - 13, 2026"}, {"filename": "sais-meta-ads-jun14-jun20.html", "dates": "Jun 14 - 20, 2026"}, {"filename": "sais-meta-ads-jun21-jun27.html", "dates": "Jun 21 - 27, 2026"}, {"filename": "sais-meta-ads-jun28-jul4.html", "dates": "Jun 28 - Jul 4, 2026"}];
  document.querySelectorAll('.report-nav').forEach(function(el) {
    var current = el.dataset.current;
    if (!reports.length) return;
    var idx = -1;
    for (var i = 0; i < reports.length; i++) {
      if (reports[i].filename === current) { idx = i; break; }
    }
    var parts = [];
    if (reports.length > 1 && idx >= 0) {
      var prevLink = idx > 0
        ? '<a href="' + reports[idx - 1].filename + '" class="nav-arrow">&larr; Previous Period</a>'
        : '<span></span>';
      var nextLink = idx < reports.length - 1
        ? '<a href="' + reports[idx + 1].filename + '" class="nav-arrow">Next Period &rarr;</a>'
        : '<span></span>';
      parts.push('<div class="nav-arrows">' + prevLink + nextLink + '</div>');
    }
    if (reports.length > 1) {
      var items = '<span class="nav-index-label">All Reports:</span>';
      for (var i = 0; i < reports.length; i++) {
        var r = reports[i];
        if (r.filename === current) {
          items += '<span class="nav-index-item nav-index-current">' + r.dates + '</span>';
        } else {
          items += '<a href="' + r.filename + '" class="nav-index-item">' + r.dates + '</a>';
        }
      }
      parts.push('<div class="nav-index">' + items + '</div>');
    }
    el.innerHTML = parts.join('');
  });
})();
