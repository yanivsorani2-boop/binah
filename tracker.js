/* Binah Site Tracker — localStorage-based visit tracking */
(function(){
  var key = 'binah_visits';
  try {
    var visits = JSON.parse(localStorage.getItem(key) || '[]');
    visits.push({
      ts: Date.now(),
      page: location.pathname + location.search,
      title: document.title,
      ref: document.referrer || ''
    });
    // Keep last 10,000 entries
    if (visits.length > 10000) visits = visits.slice(-10000);
    localStorage.setItem(key, JSON.stringify(visits));
  } catch(e) {}
})();
