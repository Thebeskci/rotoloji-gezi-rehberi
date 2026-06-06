from __future__ import annotations

import html

import streamlit as st

from rota_yz.config import Settings
from rota_yz.frontend_api import load_frontend_bundle


st.set_page_config(page_title="Rotoloji Gezi Rehberi", layout="wide")

LOCALE_META = {
    "tr": {
        "title": "Rotalari bir dergi sayfasi gibi kesfet.",
        "subtitle": "Cok dilli sehir ve mekan koleksiyonunu veri paneli gibi degil, editoryal bir gezi dosyasi gibi gez.",
        "all_cities": "Tum sehirler",
        "language": "Dil",
        "city": "Sehir",
        "category": "Kategori",
        "rating": "Minimum puan",
        "results": "Mekan",
        "city_count": "Sehir kapsami",
        "avg_rating": "Ortalama puan",
        "filters": "Aktif filtreler",
        "featured": "Kapak hikayesi",
        "curated": "Secilmis duraklar",
        "more_places": "Diger oneriler",
        "curated_copy": "En guclu mekanlar once buyuk editoryal kartlarla gelir, geri kalani daha sik bir gezi izgara duzeniyle devam eder.",
        "more_copy": "Rota setinin kalan parcasi daha kompakt bir saha rehberi gibi akar.",
        "empty": "Secilen filtreler icin mekan bulunamadi.",
        "source": "Kaynak",
        "prompt": "Gorsel promptu",
        "refresh": "Yenile / Refresh",
        "sidebar_title": "Rotoloji Atlas",
        "sidebar_copy": "Dil, sehir, kategori ve puan kirilimi ile rotayi daralt. Ana sayfa secime gore yeniden kurgulanir.",
        "hero_kicker": "YZ destekli gezi rehberi",
        "spotlight": "One cikan durak",
        "cta_label": "Kaynagi ac",
        "all_label": "Tum rotalar",
        "data_status": "Veri katmani",
        "data_source_api": "Canli API",
        "data_source_snapshot": "Gomulu snapshot",
        "data_source_api_copy": "Arayuz, yayin sirasinda HTTP API uzerinden icerik cekiyor.",
        "data_source_snapshot_copy": "Arayuz, repo icine gomulu veri anlik goruntusu ile calisiyor.",
        "load_error": "Icerik yuklenirken hata olustu.",
    },
    "en": {
        "title": "Explore routes like a magazine spread.",
        "subtitle": "Browse the multilingual city and place collection as an editorial travel issue rather than a plain data table.",
        "all_cities": "All cities",
        "language": "Language",
        "city": "City",
        "category": "Category",
        "rating": "Minimum rating",
        "results": "Places",
        "city_count": "City coverage",
        "avg_rating": "Average score",
        "filters": "Active filters",
        "featured": "Cover story",
        "curated": "Curated stops",
        "more_places": "More recommendations",
        "curated_copy": "The strongest stops surface first as large editorial cards, then the rest continue as a tighter field-guide grid.",
        "more_copy": "The remainder of the route set flows like a compact field guide.",
        "empty": "No places matched the selected filters.",
        "source": "Source",
        "prompt": "Image prompt",
        "refresh": "Refresh",
        "sidebar_title": "Rotoloji Atlas",
        "sidebar_copy": "Narrow the route by language, city, category, and score. The front page is recomposed from your selection.",
        "hero_kicker": "AI-assisted travel guide",
        "spotlight": "Featured stop",
        "cta_label": "Open source",
        "all_label": "All routes",
        "data_status": "Data layer",
        "data_source_api": "Live API",
        "data_source_snapshot": "Bundled snapshot",
        "data_source_api_copy": "The interface is currently reading content from the HTTP API.",
        "data_source_snapshot_copy": "The interface is currently running from the bundled repository snapshot.",
        "load_error": "The content feed could not be loaded.",
    },
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;500;600;700;800&family=Cormorant+Garamond:wght@500;600;700&display=swap');

        :root {
          --bg: #f4eadc;
          --bg-soft: rgba(255, 250, 243, 0.84);
          --panel: #fff8f0;
          --ink: #1c2f2d;
          --muted: #6f7f78;
          --line: rgba(28, 47, 45, 0.12);
          --accent: #c7683b;
          --accent-deep: #9f4f2f;
          --teal: #204946;
          --sand: #ddc5a5;
          --shadow: 0 22px 60px rgba(56, 34, 17, 0.12);
          --radius-xl: 32px;
          --radius-lg: 24px;
          --radius-md: 18px;
        }

        html, body, [class*="css"] {
          font-family: 'Bricolage Grotesque', sans-serif;
        }

        .stApp {
          color: var(--ink);
          background:
            radial-gradient(circle at 0% 0%, rgba(199, 104, 59, 0.16), transparent 28%),
            radial-gradient(circle at 100% 0%, rgba(32, 73, 70, 0.18), transparent 30%),
            linear-gradient(180deg, #f8f1e8 0%, #f2e8da 40%, #f7f0e7 100%);
        }

        [data-testid="stAppViewContainer"] {
          background: transparent;
        }

        [data-testid="stHeader"] {
          background: transparent;
        }

        [data-testid="stSidebar"] {
          background:
            linear-gradient(180deg, rgba(25, 56, 53, 0.97) 0%, rgba(21, 43, 41, 0.98) 100%);
          border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] * {
          color: #f8f3eb;
        }

        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label,
        [data-testid="stSidebar"] .stSlider label {
          color: rgba(248, 243, 235, 0.92) !important;
          font-size: 0.9rem;
          letter-spacing: 0.02em;
        }

        [data-testid="stSidebar"] .stSelectbox > div > div,
        [data-testid="stSidebar"] .stMultiSelect > div > div {
          background: rgba(255, 255, 255, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.12);
          border-radius: 16px;
        }

        [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {
          padding-top: 0.3rem;
        }

        [data-testid="stSidebar"] .stButton button {
          border-radius: 999px;
          border: 1px solid rgba(255, 255, 255, 0.14);
          background: linear-gradient(135deg, #f3c291 0%, #c7683b 100%);
          color: #1a2624;
          font-weight: 700;
          box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22);
        }

        .sidebar-brand {
          border: 1px solid rgba(255, 255, 255, 0.1);
          background: rgba(255, 255, 255, 0.05);
          border-radius: 26px;
          padding: 1.2rem 1.1rem 1rem 1.1rem;
          margin-bottom: 1.2rem;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
        }

        .sidebar-brand .eyebrow {
          display: inline-block;
          padding: 0.3rem 0.65rem;
          border-radius: 999px;
          background: rgba(243, 194, 145, 0.18);
          color: #f3c291;
          font-size: 0.74rem;
          text-transform: uppercase;
          letter-spacing: 0.12em;
        }

        .sidebar-brand h2 {
          margin: 0.9rem 0 0.45rem 0;
          font-family: 'Cormorant Garamond', serif;
          font-size: 2rem;
          line-height: 0.95;
          letter-spacing: -0.03em;
          color: #fff8ef;
        }

        .sidebar-brand p {
          margin: 0;
          color: rgba(248, 243, 235, 0.72);
          line-height: 1.65;
          font-size: 0.92rem;
        }

        .source-status {
          margin: 1rem 0 1.3rem 0;
          padding: 0.95rem 1rem;
          border-radius: 20px;
          border: 1px solid rgba(255, 255, 255, 0.1);
          background: rgba(255, 255, 255, 0.05);
        }

        .source-status .label {
          font-size: 0.72rem;
          text-transform: uppercase;
          letter-spacing: 0.12em;
          color: rgba(248, 243, 235, 0.6);
        }

        .source-status .value {
          margin-top: 0.4rem;
          font-size: 1.02rem;
          font-weight: 700;
          color: #fff7ef;
        }

        .source-status p {
          margin: 0.5rem 0 0 0;
          font-size: 0.88rem;
          line-height: 1.55;
          color: rgba(248, 243, 235, 0.7);
        }

        .hero-shell {
          border: 1px solid var(--line);
          border-radius: var(--radius-xl);
          background:
            linear-gradient(130deg, rgba(255, 255, 255, 0.76) 0%, rgba(255, 247, 238, 0.88) 44%, rgba(255, 249, 240, 0.94) 100%);
          box-shadow: var(--shadow);
          padding: 2rem;
        }

        .hero-kicker,
        .section-kicker {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.32rem 0.7rem;
          border-radius: 999px;
          background: rgba(32, 73, 70, 0.08);
          color: var(--teal);
          text-transform: uppercase;
          letter-spacing: 0.12em;
          font-size: 0.72rem;
          font-weight: 700;
        }

        .hero-title,
        .section-title {
          font-family: 'Cormorant Garamond', serif;
          letter-spacing: -0.035em;
          color: #162625;
        }

        .hero-title {
          margin: 1rem 0 1rem 0;
          font-size: clamp(3rem, 5vw, 5.6rem);
          line-height: 0.92;
        }

        .hero-copy {
          color: #5f6c66;
          font-size: 1.05rem;
          line-height: 1.75;
          max-width: 46rem;
          margin-bottom: 1.35rem;
        }

        .tag-row,
        .filter-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.6rem;
        }

        .chip {
          display: inline-flex;
          align-items: center;
          padding: 0.42rem 0.75rem;
          border-radius: 999px;
          background: rgba(32, 73, 70, 0.08);
          border: 1px solid rgba(32, 73, 70, 0.1);
          color: #244845;
          font-size: 0.82rem;
          font-weight: 600;
        }

        .chip.alt {
          background: rgba(199, 104, 59, 0.12);
          border-color: rgba(199, 104, 59, 0.16);
          color: var(--accent-deep);
        }

        .feature-card {
          position: relative;
          min-height: 540px;
          border-radius: 28px;
          overflow: hidden;
          border: 1px solid rgba(255, 255, 255, 0.16);
          box-shadow: 0 28px 70px rgba(28, 47, 45, 0.18);
          background:
            linear-gradient(180deg, rgba(9, 16, 18, 0.06) 0%, rgba(9, 16, 18, 0.58) 100%),
            linear-gradient(135deg, #365c58 0%, #b56943 100%);
          background-size: cover;
          background-position: center;
        }

        .feature-overlay {
          position: absolute;
          inset: auto 0 0 0;
          padding: 1.45rem;
          background: linear-gradient(180deg, rgba(14, 20, 21, 0) 0%, rgba(14, 20, 21, 0.82) 100%);
          color: #fffaf4;
        }

        .feature-label {
          display: inline-block;
          padding: 0.28rem 0.65rem;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.16);
          font-size: 0.72rem;
          text-transform: uppercase;
          letter-spacing: 0.12em;
          font-weight: 700;
          margin-bottom: 0.75rem;
        }

        .feature-title {
          font-family: 'Cormorant Garamond', serif;
          font-size: 2.6rem;
          line-height: 0.92;
          margin: 0 0 0.4rem 0;
        }

        .feature-copy {
          font-size: 0.98rem;
          line-height: 1.65;
          color: rgba(255, 250, 244, 0.84);
        }

        .metric-block {
          border-radius: 22px;
          border: 1px solid var(--line);
          background: rgba(255, 251, 245, 0.85);
          box-shadow: 0 16px 38px rgba(67, 44, 24, 0.08);
          padding: 1.1rem 1.2rem;
          min-height: 122px;
        }

        .metric-label {
          color: #76837c;
          font-size: 0.82rem;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }

        .metric-value {
          margin-top: 0.55rem;
          font-size: 2rem;
          font-weight: 800;
          color: #162625;
        }

        .metric-note {
          color: #6f7f78;
          margin-top: 0.25rem;
          font-size: 0.92rem;
        }

        .section-shell {
          margin-top: 1.2rem;
        }

        .section-title {
          margin: 0.85rem 0 0.35rem 0;
          font-size: clamp(2.2rem, 4vw, 3.4rem);
          line-height: 0.95;
        }

        .section-copy {
          margin: 0 0 1rem 0;
          color: #66756f;
          line-height: 1.7;
        }

        .lead-card,
        .place-card {
          border-radius: 28px;
          overflow: hidden;
          border: 1px solid rgba(28, 47, 45, 0.1);
          background: rgba(255, 251, 246, 0.92);
          box-shadow: 0 18px 48px rgba(69, 44, 21, 0.1);
        }

        .lead-card {
          min-height: 520px;
        }

        .place-card {
          min-height: 100%;
        }

        .image-panel {
          position: relative;
          overflow: hidden;
          min-height: 260px;
          background:
            linear-gradient(180deg, rgba(12, 15, 16, 0.04) 0%, rgba(12, 15, 16, 0.48) 100%),
            linear-gradient(135deg, #345956 0%, #c87950 100%);
          background-size: cover;
          background-position: center;
        }

        .lead-card .image-panel {
          min-height: 340px;
        }

        .image-badge {
          position: absolute;
          left: 1rem;
          top: 1rem;
          padding: 0.38rem 0.72rem;
          border-radius: 999px;
          background: rgba(255, 248, 240, 0.82);
          color: #173330;
          font-size: 0.76rem;
          font-weight: 700;
          letter-spacing: 0.03em;
        }

        .card-copy {
          padding: 1.15rem 1.15rem 1.2rem 1.15rem;
        }

        .card-topline {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.8rem;
          margin-bottom: 0.7rem;
        }

        .city-mark {
          font-size: 0.82rem;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: #697973;
          font-weight: 700;
        }

        .rating-mark {
          color: var(--accent-deep);
          font-size: 0.92rem;
          font-weight: 800;
        }

        .card-title {
          font-family: 'Cormorant Garamond', serif;
          font-size: 2rem;
          line-height: 0.96;
          color: #162625;
          margin: 0 0 0.7rem 0;
        }

        .card-description {
          color: #60706a;
          line-height: 1.72;
          font-size: 0.96rem;
          margin-bottom: 1rem;
        }

        .card-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.75rem;
          flex-wrap: wrap;
        }

        .source-link {
          text-decoration: none;
          color: #1c413d !important;
          font-weight: 700;
        }

        .prompt-note {
          font-size: 0.84rem;
          color: #75837d;
        }

        .empty-state {
          border: 1px dashed rgba(28, 47, 45, 0.18);
          border-radius: 24px;
          padding: 1.2rem 1.3rem;
          background: rgba(255, 249, 241, 0.78);
          color: #5f6c66;
        }

        .stExpander {
          border-radius: 18px !important;
          border: 1px solid rgba(28, 47, 45, 0.1) !important;
          background: rgba(255, 252, 248, 0.9) !important;
        }

        .stExpander details summary p {
          font-size: 0.9rem;
          font-weight: 700;
          color: #1d3432;
        }

        @media (max-width: 980px) {
          .hero-shell {
            padding: 1.4rem;
          }

          .feature-card {
            min-height: 360px;
            margin-top: 1rem;
          }

          .lead-card {
            min-height: auto;
          }

          .lead-card .image-panel {
            min-height: 260px;
          }

          .hero-title {
            font-size: 3.2rem;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=300)
def load_content(base_url: str, locale: str, data_mode: str, snapshot_path: str) -> dict:
    return load_frontend_bundle(
        base_url=base_url,
        locale=locale,
        data_mode=data_mode,
        snapshot_path=snapshot_path,
    )


def escape(value: str | None) -> str:
    return html.escape(value or "")


def shorten(text: str, limit: int = 220) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rsplit(" ", 1)[0] + "..."


def image_background(image_url: str | None, overlay: str) -> str:
    if image_url:
        return f"{overlay}, url('{escape(image_url)}')"
    return f"{overlay}, linear-gradient(135deg, #345956 0%, #c87950 100%)"


def build_filter_chips(meta: dict, selected_city: dict | None, selected_categories: list[str], minimum_rating: float) -> str:
    chips = [
        f"<span class='chip alt'>{escape(selected_city['name']) if selected_city else meta['all_label']}</span>",
        f"<span class='chip'>score >= {minimum_rating:.1f}</span>",
    ]
    if selected_categories:
        chips.extend(f"<span class='chip'>{escape(category)}</span>" for category in selected_categories)
    return "".join(chips)


def render_sidebar(meta: dict) -> None:
    st.markdown(
        f"""
        <div class="sidebar-brand">
          <span class="eyebrow">Travel issue</span>
          <h2>{escape(meta["sidebar_title"])}</h2>
          <p>{escape(meta["sidebar_copy"])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_data_source(meta: dict, source: str) -> None:
    if source == "api":
        value = meta["data_source_api"]
        copy = meta["data_source_api_copy"]
    else:
        value = meta["data_source_snapshot"]
        copy = meta["data_source_snapshot_copy"]

    st.markdown(
        f"""
        <div class="source-status">
          <div class="label">{escape(meta["data_status"])}</div>
          <div class="value">{escape(value)}</div>
          <p>{escape(copy)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-block">
          <div class="metric-label">{escape(label)}</div>
          <div class="metric-value">{escape(value)}</div>
          <div class="metric-note">{escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(meta: dict, selected_city: dict | None, featured_place: dict | None, selected_categories: list[str], minimum_rating: float) -> None:
    city_copy = selected_city["short_description"] if selected_city else meta["subtitle"]
    city_label = selected_city["name"] if selected_city else meta["all_label"]
    filter_chips = build_filter_chips(meta, selected_city, selected_categories, minimum_rating)

    hero_col, feature_col = st.columns([1.35, 0.85], gap="large")
    with hero_col:
        st.markdown(
            f"""
            <div class="hero-shell">
              <span class="hero-kicker">{escape(meta["hero_kicker"])}</span>
              <div class="hero-title">{escape(meta["title"])}</div>
              <p class="hero-copy">{escape(city_copy)}</p>
              <div class="tag-row">
                <span class="chip alt">{escape(city_label)}</span>
                <span class="chip">{escape(meta["filters"])}</span>
              </div>
              <div class="filter-row" style="margin-top:0.9rem;">
                {filter_chips}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feature_col:
        if not featured_place:
            return
        background = image_background(
            featured_place.get("image_url"),
            "linear-gradient(180deg, rgba(9, 16, 18, 0.06) 0%, rgba(9, 16, 18, 0.58) 100%)",
        )
        st.markdown(
            f"""
            <div class="feature-card" style="background-image:{background};">
              <div class="feature-overlay">
                <div class="feature-label">{escape(meta["spotlight"])}</div>
                <div class="feature-title">{escape(featured_place["name"])}</div>
                <div class="feature-copy">{escape(shorten(featured_place["description"], 180))}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_section_header(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="section-shell">
          <span class="section-kicker">{escape(kicker)}</span>
          <div class="section-title">{escape(title)}</div>
          <p class="section-copy">{escape(copy)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card(place: dict, meta: dict, *, large: bool = False) -> None:
    image = image_background(
        place.get("image_url"),
        "linear-gradient(180deg, rgba(10, 14, 16, 0.04) 0%, rgba(10, 14, 16, 0.42) 100%)",
    )
    wrapper_class = "lead-card" if large else "place-card"
    st.markdown(
        f"""
        <div class="{wrapper_class}">
          <div class="image-panel" style="background-image:{image};">
            <span class="image-badge">{escape(place["category"])}</span>
          </div>
          <div class="card-copy">
            <div class="card-topline">
              <span class="city-mark">{escape(place["city_name"])}</span>
              <span class="rating-mark">{place["rating"]:.1f}</span>
            </div>
            <div class="card-title">{escape(place["name"])}</div>
            <div class="card-description">{escape(shorten(place["description"], 230 if large else 165))}</div>
            <div class="card-footer">
              <a class="source-link" href="{escape(place['source_url'])}">{escape(meta["source"])}</a>
              <span class="prompt-note">{escape(meta["prompt"])}</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander(f"{meta['prompt']} · {place['name']}"):
        st.write(place.get("generated_prompt", ""))


def render_curated_layout(filtered_places: list[dict], meta: dict) -> None:
    if not filtered_places:
        st.markdown(f"<div class='empty-state'>{escape(meta['empty'])}</div>", unsafe_allow_html=True)
        return

    lead_places = filtered_places[:3]
    remaining_places = filtered_places[3:]

    if lead_places:
        left_col, right_col = st.columns([1.15, 0.85], gap="large")
        with left_col:
            render_card(lead_places[0], meta, large=True)
        with right_col:
            for place in lead_places[1:]:
                render_card(place, meta, large=False)

    if remaining_places:
        render_section_header(
            meta["featured"],
            meta["more_places"],
            meta["more_copy"],
        )
        grid_columns = st.columns(3, gap="large")
        for index, place in enumerate(remaining_places):
            with grid_columns[index % 3]:
                render_card(place, meta, large=False)


def main() -> None:
    inject_styles()
    settings = Settings.from_env()

    with st.sidebar:
        locale = st.selectbox(
            LOCALE_META["tr"]["language"],
            options=["tr", "en"],
            format_func=lambda code: "TR" if code == "tr" else "EN",
        )
        meta = LOCALE_META[locale]
        render_sidebar(meta)
        if st.button(meta["refresh"], width="stretch"):
            st.cache_data.clear()
            st.rerun()

    try:
        content = load_content(
            settings.strapi_url,
            locale,
            settings.streamlit_data_mode,
            settings.snapshot_path,
        )
    except Exception as exc:
        st.error(f"{meta['load_error']} {exc}")
        st.stop()

    with st.sidebar:
        render_data_source(meta, content["source"])

    cities = content["cities"]
    places = content["places"]

    city_options = [meta["all_cities"]] + [city["name"] for city in cities]
    selected_city_name = st.sidebar.selectbox(meta["city"], city_options)
    selected_city = next((city for city in cities if city["name"] == selected_city_name), None)

    categories = sorted({place["category"] for place in places})
    selected_categories = st.sidebar.multiselect(meta["category"], categories)
    minimum_rating = st.sidebar.slider(meta["rating"], 0.0, 5.0, 4.5, 0.1)

    filtered_places = [
        place
        for place in places
        if place["rating"] >= minimum_rating
        and (not selected_city or place["city_slug"] == selected_city["slug"])
        and (not selected_categories or place["category"] in selected_categories)
    ]

    featured_place = filtered_places[0] if filtered_places else (places[0] if places else None)
    active_cities = {place["city_slug"] for place in filtered_places}
    average_rating = (
        sum(place["rating"] for place in filtered_places) / len(filtered_places)
        if filtered_places
        else 0.0
    )

    render_hero(meta, selected_city, featured_place, selected_categories, minimum_rating)

    metric_cols = st.columns(4, gap="large")
    with metric_cols[0]:
        render_metric(meta["results"], str(len(filtered_places)), meta["curated"])
    with metric_cols[1]:
        city_note = selected_city["name"] if selected_city else str(len(active_cities or cities))
        render_metric(meta["city_count"], str(len(active_cities or cities)), city_note)
    with metric_cols[2]:
        render_metric(meta["category"], str(len(selected_categories) or len(categories)), meta["filters"])
    with metric_cols[3]:
        render_metric(meta["avg_rating"], f"{average_rating:.1f}" if average_rating else "-", meta["featured"])

    render_section_header(
        meta["featured"],
        meta["curated"],
        meta["curated_copy"],
    )
    render_curated_layout(filtered_places, meta)


if __name__ == "__main__":
    main()
