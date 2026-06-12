/**
 * Asset manifest loader for CarbonSim Online.
 *
 * Fetches /assets/manifest.json, preloads all image assets, and exposes
 * a simple API for the isometric renderer (Sprint 3) to consume.
 */
(function (root) {
  'use strict';

  const MANIFEST_URL = '/assets/manifest.json';

  /** @type {Record<string, HTMLImageElement>} */
  const images = {};
  /** @type {Record<string, any>} */
  let manifest = null;
  let loadPromise = null;

  /**
   * Load the manifest and preload all image assets.
   * @returns {Promise<Record<string, any>>}
   */
  function loadAssets() {
    if (loadPromise) {
      return loadPromise;
    }

    loadPromise = fetch(MANIFEST_URL)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load asset manifest: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        manifest = data;
        const imageEntries = Object.entries(manifest.assets || {}).filter(
          ([_, entry]) => entry.type === 'image'
        );

        return Promise.all(
          imageEntries.map(([name, entry]) => {
            return new Promise((resolve, reject) => {
              const img = new Image();
              img.onload = () => {
                images[name] = img;
                resolve({ name, img });
              };
              img.onerror = () => {
                reject(new Error(`Failed to load image: ${entry.path}`));
              };
              img.src = entry.path;
            });
          })
        ).then(() => manifest);
      });

    return loadPromise;
  }

  /**
   * Get a preloaded image by logical name.
   * @param {string} name
   * @returns {HTMLImageElement | undefined}
   */
  function getImage(name) {
    return images[name];
  }

  /**
   * Get the raw manifest entry for any asset type.
   * @param {string} name
   * @returns {any | undefined}
   */
  function getAsset(name) {
    return manifest && manifest.assets ? manifest.assets[name] : undefined;
  }

  /**
   * Return the full loaded manifest object.
   * @returns {any | null}
   */
  function getManifest() {
    return manifest;
  }

  root.AssetLoader = {
    load: loadAssets,
    getImage: getImage,
    getAsset: getAsset,
    getManifest: getManifest,
  };
})(window);
