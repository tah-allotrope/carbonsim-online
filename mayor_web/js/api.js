const API = {
  async _fetch(method, path, body) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const resp = await fetch(path, opts);
    if (!resp.ok) {
      let msg = `HTTP ${resp.status}`;
      try { const e = await resp.json(); msg = e.detail || msg; } catch {}
      throw new Error(msg);
    }
    return resp.json();
  },

  createGame(data) { return this._fetch('POST', '/api/games', data); },
  listGames() { return this._fetch('GET', '/api/games'); },
  getGame(id) { return this._fetch('GET', `/api/games/${id}`); },
  advanceYear(id) { return this._fetch('POST', `/api/games/${id}/advance-year`); },
  resolveCard(id, data) { return this._fetch('POST', `/api/games/${id}/resolve-card`, data); },
  decision(id, data) { return this._fetch('POST', `/api/games/${id}/decision`, data); },
  endYear(id) { return this._fetch('POST', `/api/games/${id}/end-year`); },
  saveGame(id, data) { return this._fetch('POST', `/api/games/${id}/save`, data); },
  listSaves(id) { return this._fetch('GET', `/api/games/${id}/saves`); },
  loadSave(id, saveId) { return this._fetch('POST', `/api/games/${id}/load/${saveId}`); },
  getSummary(id) { return this._fetch('GET', `/api/games/${id}/summary`); },
  deleteGame(id) { return this._fetch('DELETE', `/api/games/${id}`); },
};
