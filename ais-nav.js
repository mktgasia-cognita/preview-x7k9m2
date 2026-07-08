(function() {
  var reports = [{"filename": "ais-meta-ads-mar2-mar15.html", "dates": "Mar 2 - 15, 2026"}, {"filename": "ais-meta-ads-mar16-mar29.html", "dates": "Mar 16 - 29, 2026"}, {"filename": "ais-meta-ads-mar30-apr12.html", "dates": "Mar 30 - Apr 12, 2026"}, {"filename": "ais-meta-ads-apr13-apr26.html", "dates": "Apr 13 - 26, 2026"}, {"filename": "ais-meta-ads-apr27-may10.html", "dates": "Apr 27 - May 10, 2026"}, {"filename": "ais-meta-ads-may11-may24.html", "dates": "May 11 - 24, 2026"}, {"filename": "ais-meta-ads-may25-jun7.html", "dates": "May 25 - Jun 7, 2026"}, {"filename": "ais-meta-ads-jun8-jun21.html", "dates": "Jun 8 - 21, 2026"}, {"filename": "ais-meta-ads-jun22-jul5.html", "dates": "Jun 22 - Jul 5, 2026"}];
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
    if (reports.length > 1 && !el.classList.contains('report-nav-compact')) {
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
