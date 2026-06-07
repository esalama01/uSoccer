# uSoccer

A football analytics pipeline that scrapes event data from WhoScored, converts it to the SPADL representation, computes gamestates, and applies machine learning models (VAEP and xG) alongside player chemistry analysis. The project is grounded in published research on valuing actions and quantifying player interactions, and it uses the `socceraction` library for SPADL conversions.

**This is a work-in-progress.** The machine learning component was built under time constraints and lacks proper hyperparameter tuning, regularization, or learning-curve analysis. A formal model evaluation will be added in a later iteration.

---

## Completed Features

| Feature | Description | Location |
|---------|-------------|----------|
| Match data scraping | Downloads match event JSON from WhoScored live pages | `pipeline/pipeline.py` – `MatchScraper` |
| League-wide scraping | Discovers fixtures and match IDs for a full season | `pipeline/pipeline.py` – `LeagueScraper` |
| SPADL conversion | Parses WhoScored JSON and converts events to SPADL actions using `socceraction` | `pipeline/pipeline.py` – `SpadlConverter` |
| Gamestate features | Computes action features (position, bodypart, time, etc.) and assembles gamestate DataFrames | `pipeline/pipeline.py` – `GstatesConverter` |
| VAEP model | Trains XGBoost classifiers for scoring and conceding probabilities, then computes VAEP values per action | `analytics/data_analysis.py` – `VAEP` |
| xG model | Trains an XGBoost classifier for shot conversion probability and merges xG values into SPADL data | `analytics/data_analysis.py` – `xG` |
| Passing network visualisation | Draws a weighted passing network on a scaled pitch using matplotlib | `analytics/data_analysis.py` – `Plots` |
| Player chemistry (JOI / JDI) | Calculates Joint Offensive Impact and Joint Defensive Impact per 90 minutes, based on VAEP values | `analytics/data_analysis.py` – `PlayerChemistry` |

---

## What is Missing / Work in Progress

- **Predictive chemistry model:** The chemistry metrics (JOI90, JDI90) are currently computed from observed data only. A model that predicts chemistry from player profiles and tactical context is planned.
- **Expected Threat (xT):** Adding xT values to the action timeline is a planned extension.
- **Model validation:** No hyperparameter search, cross-validation, or learning-curve analysis has been performed. Models are trained with fixed, untuned parameters. A formal evaluation covering regularization, capacity, and calibration will be added later.
- **Data pipeline robustness:** Network error handling is minimal; rate limiting and retry logic are not implemented.
- **Testing:** No unit or integration tests are included.
- **Configurability:** Many paths and parameters are hardcoded throughout the codebase.

---

## Project Structure

```text
.
├── pipeline
│   └── pipeline.py          # scraping, SPADL conversion, gamestate computation
├── analytics
│   └── data_analysis.py     # VAEP, xG, player chemistry, passing network visualisation
├── data
│   ├── events/              # raw scraped events (partitioned parquet)
│   ├── spadl/               # SPADL data (partitioned parquet)
│   └── game_states/         # gamestate features and labels (partitioned parquet)
├── plot_config.json         # pitch drawing configuration
└── README.md
```

---

## Dependencies

- Python 3.8+
- `curl_cffi` — browser impersonation for scraping
- `beautifulsoup4` — HTML parsing
- `pandas`
- `numpy`
- `matplotlib`
- `scipy`
- `xgboost`
- `socceraction` — SPADL conversion and VAEP feature / label functions
- `json5`
- `pyarrow` — parquet I/O
- `tqdm`

Install all dependencies with:

```bash
pip install curl_cffi beautifulsoup4 pandas numpy matplotlib scipy xgboost socceraction json5 pyarrow tqdm
```

> `socceraction` may impose version constraints on `pandas` and related packages. Consult its documentation if you encounter compatibility errors.

---

## How to Use

### 1. Scrape League Data

To scrape a full season and save raw events:

```python
from pipeline.pipeline import LeagueScraper

lg = LeagueScraper("laliga", "2025/2026")
lg.save(path="../data/events")
```

To scrape a specific list of matches:

```python
from pipeline.pipeline import MatchScraper

urls = [
    "https://www.whoscored.com/matches/1914256/live/spain-laliga-2025-2026-real-madrid-athletic-club",
    "https://www.whoscored.com/matches/1914251/live/spain-laliga-2025-2026-sevilla-real-madrid",
]
scraper = MatchScraper(urls)
data = scraper.crawl()
```

### 2. Convert to SPADL

```python
from pipeline.pipeline import SpadlConverter

converter = SpadlConverter(data_list=data)
spadl_df = converter.parse()
converter.save(path="../data/spadl")
```

### 3. Compute Gamestates

```python
from pipeline.pipeline import GstatesConverter

gstate = GstatesConverter(read_path="../data/spadl")
gstate.save(path="../data/game_states")
```

### 4. Train VAEP and xG Models

```python
from analytics.data_analysis import VAEP, xG

# VAEP
vp = VAEP(read_path="../data/game_states")
vp.train()
predictions = vp.predict(vp.select_features())
vp.process_all_games(
    predictions,
    spadl_file_path="../data/spadl",
    output_dir="../data/spadl_vaep"
)

# xG
xg_model = xG(read_path="../data/game_states")
xg_model.train()
xg_preds = xg_model.predict(xg_model.select_features())
xg_model.process_all_games(
    xg_preds,
    spadl_file_path="../data/spadl",
    output_dir="../data/spadl_xG"
)
```

### 5. Plot a Passing Network

```python
import matplotlib.pyplot as plt
from analytics.data_analysis import Plots

plotter = Plots(
    read_path="../data/spadl_vaep",
    filters=[('game_id', '=', 1821496)]
)
plotter.prepare_data(period=1, num_minutes=45, team_name="Real Madrid")

ax = plotter.draw_pitch()
plotter.draw_pass_map(
    ax=ax,
    player_position=plotter.player_position,
    player_pass_count=plotter.player_pass_count,
    player_pass_value=plotter.player_pass_value,
    pair_pass_count=plotter.pair_pass_count,
    pair_pass_value=plotter.pair_pass_value,
    title="Real Madrid - First Half"
)
plt.savefig("passing_network.png", bbox_inches='tight')
```
<p align="center">
  <img src="https://raw.githubusercontent.com/esalama01/uSoccer/main/analystics/first_pass_map.png" width="700" alt="Passing Network"/>
  <br>
  <em>Passing network — node size and color reflect pass volume and VAEP contribution.</em>
</p>


### 6. Calculate Player Chemistry

> The chemistry calculations require that the SPADL data already contains a `vaep_value` column. Run the VAEP pipeline first.

```python
from analytics.data_analysis import PlayerChemistry

chem = PlayerChemistry(read_path="../data/spadl_vaep")
minutes_df = chem.generate_minutes_df()

# Joint Offensive Impact per 90
joi90 = chem.calculate_joi90(minutes_df, "Player A", "Player B")

# Joint Defensive Impact per 90
game_ids = [...]  # list of game IDs where both players appeared
player_positions = chem.get_player_coordinates(game_ids[0])
jdi90 = chem.calculate_jdi90(minutes_df, "Player A", "Player B", game_ids, player_positions)
```

---

## References

- Decroos, T., Bransen, L., Van Haaren, J., & Davis, J. (2019). *Actions Speak Louder than Goals: Valuing Player Actions in Soccer.* KDD 2019. [Link](https://www.janvanhaaren.be/assets/papers/kdd-2019-vaep.pdf)
- Van Haaren, J. (2020). *Quantifying Player Chemistry in Soccer.* MIT SSA Conference. [Link](https://www.janvanhaaren.be/assets/papers/mitssac-2020-chemistry.pdf)
- `socceraction` library: [GitHub](https://github.com/ML-KULeuven/socceraction) — used for SPADL conversion and VAEP feature / label generation.
- `soccerdata` library: [GitHub](https://github.com/probberechts/soccerdata) — referenced for data loading patterns.
- Player chemistry implementation inspired by: [vinisilvag/player-chemistry](https://github.com/vinisilvag/player-chemistry/blob/main/metrics.py)
- passing-networks-in-python  : [GitHub](https://github.com/Friends-of-Tracking-Data-FoTD/passing-networks-in-python)

---

## Limitations

- **Scraping legality:** WhoScored data scraping may violate the website's terms of service. Use responsibly and for research purposes only.
- **Data quality:** The pipeline does not validate scraped event data. Some matches may contain incomplete or inconsistent JSON.
- **Model simplicity:** XGBoost models are trained with fixed, shallow-tree configurations and no cross-validation. No performance metrics are reported.
- **Hardcoded parameters:** Paths, pitch dimensions (105 x 68 m), and feature / label groups are hardcoded throughout. The code assumes a specific parquet partitioning scheme.
- **No incremental updates:** Each run reprocesses everything from scratch; there is no caching or incremental scraping.
- **Single data source:** Only WhoScored match event data is supported. Other providers (Opta, StatsBomb, WyScout) are not integrated.

---

## Future Work

- **Predictive chemistry model:** Train a model to forecast JOI / JDI from player profiles and tactical context rather than computing it retrospectively.
- **Expected Threat (xT):** Integrate xT values into the action timeline alongside VAEP and xG.
- **Formal model evaluation:** Add cross-validation, learning curves, SHAP analysis, and hyperparameter optimization for all models.
- **Pipeline robustness:** Add request caching, parallel downloading, and proper error recovery.
- **Additional data sources:** Support other data formats via the `socceraction` loader interface.

---

## License

This project is for educational and research purposes. No license is applied.
