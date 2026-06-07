const LOCALE_META = {
  tr: {
    title: "Rotalari bir dergi sayfasi gibi kesfet.",
    subtitle:
      "Cok dilli sehir ve mekan koleksiyonunu veri paneli gibi degil, editoryal bir gezi dosyasi gibi gez.",
    allCities: "Tum sehirler",
    language: "Dil",
    city: "Sehir",
    category: "Kategori",
    rating: "Minimum puan",
    results: "Mekan",
    cityCount: "Sehir kapsami",
    avgRating: "Ortalama puan",
    filters: "Aktif filtreler",
    featured: "Kapak hikayesi",
    curated: "Secilmis duraklar",
    morePlaces: "Diger oneriler",
    curatedCopy:
      "En guclu mekanlar once buyuk editoryal kartlarla gelir, geri kalani daha sik bir gezi izgara duzeniyle devam eder.",
    moreCopy: "Rota setinin kalan parcasi daha kompakt bir saha rehberi gibi akar.",
    empty: "Secilen filtreler icin mekan bulunamadi.",
    source: "Kaynak",
    prompt: "Gorsel promptu",
    refresh: "Icerigi yeniden yukle",
    sidebarTitle: "Rotoloji Atlas",
    sidebarCopy:
      "Dil, sehir, kategori ve puan kirilimi ile rotayi daralt. Bu GitHub Pages edisyonu yalnizca repo icindeki snapshot verisinden beslenir.",
    heroKicker: "GitHub Pages gezi rehberi",
    spotlight: "One cikan durak",
    ctaLabel: "Kaynagi ac",
    allLabel: "Tum rotalar",
    dataStatus: "Veri katmani",
    dataSource: "Gomulu snapshot",
    dataSourceCopy:
      "Arayuz, GitHub Pages uzerinden yayinlanan repo icindeki statik veri arsivini kullaniyor.",
    loadError: "Icerik yuklenirken hata olustu.",
    buildStamp: "Yayin anlik goruntusu",
    brandEyebrow: "GitHub Pages edition",
  },
  en: {
    title: "Explore routes like a magazine spread.",
    subtitle:
      "Browse the multilingual city and place collection as an editorial travel issue rather than a plain data table.",
    allCities: "All cities",
    language: "Language",
    city: "City",
    category: "Category",
    rating: "Minimum rating",
    results: "Places",
    cityCount: "City coverage",
    avgRating: "Average score",
    filters: "Active filters",
    featured: "Cover story",
    curated: "Curated stops",
    morePlaces: "More recommendations",
    curatedCopy:
      "The strongest stops surface first as large editorial cards, then the rest continue as a tighter field-guide grid.",
    moreCopy: "The remainder of the route set flows like a compact field guide.",
    empty: "No places matched the selected filters.",
    source: "Source",
    prompt: "Image prompt",
    refresh: "Reload content",
    sidebarTitle: "Rotoloji Atlas",
    sidebarCopy:
      "Narrow the route by language, city, category, and score. This GitHub Pages edition runs entirely from the repository snapshot.",
    heroKicker: "GitHub Pages travel guide",
    spotlight: "Featured stop",
    ctaLabel: "Open source",
    allLabel: "All routes",
    dataStatus: "Data layer",
    dataSource: "Bundled snapshot",
    dataSourceCopy:
      "The interface is reading the static repository archive published through GitHub Pages.",
    loadError: "The content feed could not be loaded.",
    buildStamp: "Published snapshot",
    brandEyebrow: "GitHub Pages edition",
  },
};

const state = {
  locale: "tr",
  citySlug: "",
  categories: [],
  minRating: 4.5,
  bundleCache: new Map(),
  manifest: null,
};

const nodes = {
  brandEyebrow: document.querySelector("#brand-eyebrow"),
  brandCopy: document.querySelector("#brand-copy"),
  dataStatusLabel: document.querySelector("#data-status-label"),
  dataStatusValue: document.querySelector("#data-status-value"),
  dataStatusCopy: document.querySelector("#data-status-copy"),
  generatedAt: document.querySelector("#generated-at"),
  languageLabel: document.querySelector("#language-label"),
  cityLabel: document.querySelector("#city-label"),
  categoryLabel: document.querySelector("#category-label"),
  ratingLabel: document.querySelector("#rating-label"),
  ratingValue: document.querySelector("#rating-value"),
  localeSwitch: document.querySelector("#locale-switch"),
  citySelect: document.querySelector("#city-select"),
  categoryList: document.querySelector("#category-list"),
  ratingRange: document.querySelector("#rating-range"),
  refreshButton: document.querySelector("#refresh-button"),
  heroGrid: document.querySelector("#hero-grid"),
  metricsGrid: document.querySelector("#metrics-grid"),
  curatedShell: document.querySelector("#curated-shell"),
  moreShell: document.querySelector("#more-shell"),
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function shorten(text, limit = 220) {
  const compact = String(text ?? "").replace(/\s+/g, " ").trim();
  if (compact.length <= limit) {
    return compact;
  }
  return `${compact.slice(0, Math.max(0, limit - 1)).trimEnd()}...`;
}

function formatStamp(value, locale) {
  if (!value) {
    return "";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat(locale === "tr" ? "tr-TR" : "en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(parsed);
}

async function loadManifest(force = false) {
  if (state.manifest && !force) {
    return state.manifest;
  }
  const suffix = force ? `?t=${Date.now()}` : "";
  const response = await fetch(`data/manifest.json${suffix}`);
  if (!response.ok) {
    throw new Error(`manifest ${response.status}`);
  }
  state.manifest = await response.json();
  return state.manifest;
}

async function loadBundle(locale, force = false) {
  if (state.bundleCache.has(locale) && !force) {
    return state.bundleCache.get(locale);
  }

  const suffix = force ? `?t=${Date.now()}` : "";
  const response = await fetch(`data/${locale}.json${suffix}`);
  if (!response.ok) {
    throw new Error(`bundle ${response.status}`);
  }

  const bundle = await response.json();
  state.bundleCache.set(locale, bundle);
  return bundle;
}

function buildFilterChips(meta, selectedCity, selectedCategories, minRating) {
  const chips = [
    `<span class="chip alt">${escapeHtml(selectedCity ? selectedCity.name : meta.allLabel)}</span>`,
    `<span class="chip">score >= ${minRating.toFixed(1)}</span>`,
  ];

  for (const category of selectedCategories) {
    chips.push(`<span class="chip">${escapeHtml(category)}</span>`);
  }

  return chips.join("");
}

function renderHero(meta, selectedCity, featuredPlace, selectedCategories, minRating) {
  const cityCopy = selectedCity ? selectedCity.short_description : meta.subtitle;
  const cityLabel = selectedCity ? selectedCity.name : meta.allLabel;
  const filterChips = buildFilterChips(meta, selectedCity, selectedCategories, minRating);
  const featureBackground = featuredPlace?.image_url
    ? `style="background-image: linear-gradient(180deg, rgba(9, 16, 18, 0.06) 0%, rgba(9, 16, 18, 0.58) 100%), url('${encodeURI(featuredPlace.image_url)}');"`
    : "";

  nodes.heroGrid.innerHTML = `
    <article class="hero-shell">
      <span class="hero-kicker">${escapeHtml(meta.heroKicker)}</span>
      <h2 class="hero-title">${escapeHtml(meta.title)}</h2>
      <p class="hero-copy">${escapeHtml(cityCopy)}</p>
      <div class="tag-row">
        <span class="chip alt">${escapeHtml(cityLabel)}</span>
        <span class="chip">${escapeHtml(meta.filters)}</span>
      </div>
      <div class="filter-row" style="margin-top:0.9rem;">
        ${filterChips}
      </div>
    </article>
    ${
      featuredPlace
        ? `
      <article class="feature-card" ${featureBackground}>
        <div class="feature-overlay">
          <div class="feature-label">${escapeHtml(meta.spotlight)}</div>
          <h3 class="feature-title">${escapeHtml(featuredPlace.name)}</h3>
          <p class="feature-copy">${escapeHtml(shorten(featuredPlace.description, 180))}</p>
        </div>
      </article>
    `
        : ""
    }
  `;
}

function renderMetrics(meta, filteredPlaces, categories, selectedCategories, selectedCity) {
  const activeCities = new Set(filteredPlaces.map((place) => place.city_slug));
  const averageRating = filteredPlaces.length
    ? filteredPlaces.reduce((sum, place) => sum + place.rating, 0) / filteredPlaces.length
    : 0;
  const cityCount = selectedCity ? 1 : activeCities.size;

  const cards = [
    {
      label: meta.results,
      value: String(filteredPlaces.length),
      note: meta.curated,
    },
    {
      label: meta.cityCount,
      value: String(cityCount || 0),
      note: selectedCity ? selectedCity.name : String(cityCount || 0),
    },
    {
      label: meta.category,
      value: String(selectedCategories.length || categories.length),
      note: meta.filters,
    },
    {
      label: meta.avgRating,
      value: averageRating ? averageRating.toFixed(1) : "-",
      note: meta.featured,
    },
  ];

  nodes.metricsGrid.innerHTML = cards
    .map(
      (card) => `
        <article class="metric-card">
          <div class="metric-label">${escapeHtml(card.label)}</div>
          <div class="metric-value">${escapeHtml(card.value)}</div>
          <div class="metric-note">${escapeHtml(card.note)}</div>
        </article>
      `,
    )
    .join("");
}

function renderSectionHeader(kicker, title, copy) {
  return `
    <span class="section-kicker">${escapeHtml(kicker)}</span>
    <h2 class="section-title">${escapeHtml(title)}</h2>
    <p class="section-copy">${escapeHtml(copy)}</p>
  `;
}

function renderCard(place, meta, variant) {
  const wrapperClass = variant === "lead" ? "lead-card" : variant === "stack" ? "stack-card" : "grid-card";
  const background = place.image_url
    ? `style="background-image: linear-gradient(180deg, rgba(10, 14, 16, 0.04) 0%, rgba(10, 14, 16, 0.42) 100%), url('${encodeURI(place.image_url)}');"`
    : "";
  const descriptionLimit = variant === "lead" ? 240 : 165;
  const promptBox = place.generated_prompt
    ? `
      <details class="prompt-box">
        <summary>${escapeHtml(meta.prompt)}</summary>
        <p>${escapeHtml(place.generated_prompt)}</p>
      </details>
    `
    : "";

  return `
    <article class="${wrapperClass}">
      <div class="image-panel" ${background}>
        <span class="image-badge">${escapeHtml(place.category)}</span>
      </div>
      <div class="card-copy">
        <div class="card-topline">
          <span class="city-mark">${escapeHtml(place.city_name)}</span>
          <span class="rating-mark">${escapeHtml(place.rating.toFixed(1))}</span>
        </div>
        <h3 class="card-title">${escapeHtml(place.name)}</h3>
        <p class="card-description">${escapeHtml(shorten(place.description, descriptionLimit))}</p>
        <div class="card-footer">
          <a class="source-link" href="${escapeHtml(place.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(meta.ctaLabel)}</a>
        </div>
        ${promptBox}
      </div>
    </article>
  `;
}

function renderCurated(meta, filteredPlaces) {
  if (!filteredPlaces.length) {
    nodes.curatedShell.innerHTML = `
      ${renderSectionHeader(meta.featured, meta.curated, meta.curatedCopy)}
      <div class="empty-state">${escapeHtml(meta.empty)}</div>
    `;
    nodes.moreShell.innerHTML = "";
    return;
  }

  const leadPlaces = filteredPlaces.slice(0, 3);
  const remainingPlaces = filteredPlaces.slice(3);
  const lead = leadPlaces[0] ? renderCard(leadPlaces[0], meta, "lead") : "";
  const stack = leadPlaces
    .slice(1)
    .map((place) => renderCard(place, meta, "stack"))
    .join("");

  nodes.curatedShell.innerHTML = `
    ${renderSectionHeader(meta.featured, meta.curated, meta.curatedCopy)}
    <div class="lead-layout">
      <div>${lead}</div>
      <div class="stack-grid">${stack}</div>
    </div>
  `;

  if (!remainingPlaces.length) {
    nodes.moreShell.innerHTML = "";
    return;
  }

  nodes.moreShell.innerHTML = `
    ${renderSectionHeader(meta.featured, meta.morePlaces, meta.moreCopy)}
    <div class="card-grid">
      ${remainingPlaces.map((place) => renderCard(place, meta, "grid")).join("")}
    </div>
  `;
}

function syncStaticLabels(meta) {
  document.documentElement.lang = state.locale;
  document.title = state.locale === "tr" ? "Rotoloji Gezi Rehberi" : "Rotoloji Travel Guide";
  nodes.brandEyebrow.textContent = meta.brandEyebrow;
  nodes.brandCopy.textContent = meta.sidebarCopy;
  nodes.dataStatusLabel.textContent = meta.dataStatus;
  nodes.dataStatusValue.textContent = meta.dataSource;
  nodes.dataStatusCopy.textContent = meta.dataSourceCopy;
  nodes.languageLabel.textContent = meta.language;
  nodes.cityLabel.textContent = meta.city;
  nodes.categoryLabel.textContent = meta.category;
  nodes.ratingLabel.textContent = meta.rating;
  nodes.refreshButton.textContent = meta.refresh;
  nodes.ratingValue.textContent = Number(state.minRating).toFixed(1);
}

function populateCitySelect(meta, cities) {
  const options = [
    `<option value="">${escapeHtml(meta.allCities)}</option>`,
    ...cities.map((city) => `<option value="${escapeHtml(city.slug)}">${escapeHtml(city.name)}</option>`),
  ];
  nodes.citySelect.innerHTML = options.join("");
  nodes.citySelect.value = state.citySlug;
}

function populateCategories(categories) {
  nodes.categoryList.innerHTML = categories
    .map(
      (category) => `
        <button
          type="button"
          class="category-chip ${state.categories.includes(category) ? "is-active" : ""}"
          data-category="${escapeHtml(category)}"
        >
          ${escapeHtml(category)}
        </button>
      `,
    )
    .join("");
}

function render(bundle) {
  const meta = LOCALE_META[state.locale];
  const cities = bundle.cities;
  const places = bundle.places;
  const categories = [...new Set(places.map((place) => place.category))].sort((left, right) => left.localeCompare(right));
  const selectedCity = cities.find((city) => city.slug === state.citySlug) || null;

  syncStaticLabels(meta);
  populateCitySelect(meta, cities);
  populateCategories(categories);

  const filteredPlaces = places.filter((place) => {
    const cityMatch = !selectedCity || place.city_slug === selectedCity.slug;
    const categoryMatch = !state.categories.length || state.categories.includes(place.category);
    return cityMatch && categoryMatch && place.rating >= state.minRating;
  });

  const featuredPlace = filteredPlaces[0] || places[0] || null;
  renderHero(meta, selectedCity, featuredPlace, state.categories, state.minRating);
  renderMetrics(meta, filteredPlaces, categories, state.categories, selectedCity);
  renderCurated(meta, filteredPlaces);

  nodes.generatedAt.textContent = `${meta.buildStamp}: ${formatStamp(bundle.generated_at, state.locale)}`;
  for (const button of nodes.localeSwitch.querySelectorAll(".locale-pill")) {
    button.classList.toggle("is-active", button.dataset.locale === state.locale);
  }
}

function ensureStateMatchesBundle(bundle) {
  const cityExists = !state.citySlug || bundle.cities.some((city) => city.slug === state.citySlug);
  if (!cityExists) {
    state.citySlug = "";
  }

  const categorySet = new Set(bundle.places.map((place) => place.category));
  state.categories = state.categories.filter((category) => categorySet.has(category));
}

async function refresh(force = false) {
  const meta = LOCALE_META[state.locale];

  try {
    await loadManifest(force);
    const bundle = await loadBundle(state.locale, force);
    ensureStateMatchesBundle(bundle);
    render(bundle);
  } catch (error) {
    document.body.innerHTML = `
      <main class="error-shell">
        <h2>Rotoloji</h2>
        <p>${escapeHtml(meta.loadError)} ${escapeHtml(error instanceof Error ? error.message : String(error))}</p>
      </main>
    `;
  }
}

function bindEvents() {
  nodes.localeSwitch.addEventListener("click", async (event) => {
    const button = event.target.closest(".locale-pill");
    if (!button) {
      return;
    }

    const nextLocale = button.dataset.locale;
    if (!nextLocale || nextLocale === state.locale) {
      return;
    }

    state.locale = nextLocale;
    state.categories = [];
    await refresh(false);
  });

  nodes.citySelect.addEventListener("change", () => {
    state.citySlug = nodes.citySelect.value;
    refresh(false);
  });

  nodes.categoryList.addEventListener("click", (event) => {
    const button = event.target.closest(".category-chip");
    if (!button) {
      return;
    }

    const category = button.dataset.category;
    if (!category) {
      return;
    }

    if (state.categories.includes(category)) {
      state.categories = state.categories.filter((item) => item !== category);
    } else {
      state.categories = [...state.categories, category];
    }

    refresh(false);
  });

  nodes.ratingRange.addEventListener("input", () => {
    state.minRating = Number(nodes.ratingRange.value);
    nodes.ratingValue.textContent = state.minRating.toFixed(1);
  });

  nodes.ratingRange.addEventListener("change", () => {
    state.minRating = Number(nodes.ratingRange.value);
    refresh(false);
  });

  nodes.refreshButton.addEventListener("click", async () => {
    state.bundleCache.clear();
    await refresh(true);
  });
}

async function init() {
  bindEvents();
  await refresh(false);
}

init();
