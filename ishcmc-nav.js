(function() {
  var reports = [{"filename": "ishcmc-meta-ads-jun29-jul5.html", "dates": "Jun 29 - Jul 5, 2026"}, {"filename": "ishcmc-meta-ads-jul6-jul12.html", "dates": "Jul 6 - 12, 2026"}, {"filename": "ishcmc-meta-ads-jul13-jul19.html", "dates": "Jul 13 - 19, 2026"}];
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
