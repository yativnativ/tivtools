/* This Is Vegan Tools — WebMCP tool registration (document.modelContext).
   Gives in-browser AI agents a structured E-Nummern-Check instead of scraping.
   No-op in browsers without WebMCP support. */

(function () {
  var mc = document.modelContext || navigator.modelContext;
  if (!mc || typeof mc.registerTool !== 'function') return;

  var dataPromise = null;
  function loadAdditives() {
    if (!dataPromise) {
      dataPromise = fetch('/enummern.json', { cache: 'no-cache' }).then(function (r) { return r.json(); });
    }
    return dataPromise;
  }

  function out(o) { return { content: [{ type: 'text', text: JSON.stringify(o, null, 1) }] }; }

  var STATUS = {
    yes: 'vegan',
    no: 'nicht vegan (tierischen Ursprungs)',
    maybe: 'unklar, kann tierisch oder pflanzlich hergestellt sein'
  };

  mc.registerTool({
    name: 'check_e_number',
    description: 'Prueft, ob ein Lebensmittel-Zusatzstoff (E-Nummer) vegan ist. Datenbasis: kuratierte Liste von 113 E-Nummern mit Herkunft und Erklaerung von tools.this-is-vegan.com. Suche per E-Nummer (z.B. "E120") oder Name (z.B. "Karmin", "Gelatine").',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'E-Nummer ("E120", "120") oder Name des Zusatzstoffs ("Karmin")' }
      },
      required: ['query']
    },
    execute: async function (args) {
      var data = await loadAdditives();
      var list = data.additives || [];
      var q = String(args.query || '').trim().toUpperCase().replace(/\s+/g, '');
      if (/^\d/.test(q)) q = 'E' + q;
      var hits = list.filter(function (a) { return a.code.toUpperCase() === q; });
      if (!hits.length) {
        var ql = String(args.query || '').trim().toLowerCase();
        hits = list.filter(function (a) { return a.name.toLowerCase().indexOf(ql) !== -1; });
      }
      if (!hits.length) {
        return out({ found: false, hint: 'Keine dieser 113 gelisteten E-Nummern. Volle Liste: https://tools.this-is-vegan.com/e-nummern/' });
      }
      return out({
        found: true,
        results: hits.slice(0, 5).map(function (a) {
          return {
            code: a.code,
            name: a.name,
            klasse: a['class'],
            vegan: STATUS[a.status] || a.status,
            info: a.info,
            details: 'https://tools.this-is-vegan.com/e-nummern/' + a.code.toLowerCase() + '/'
          };
        })
      });
    }
  });
})();
