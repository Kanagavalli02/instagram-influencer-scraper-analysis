# Instagram Influencer Data Collection, Scraping & Analysis

## Goal

Collect and scrape publicly available Instagram influencer data, then analyze the scraped dataset and present insights using visualizations (graphs).

## Project Overview

This project covers the complete pipeline:

* Influencer discovery / data collection
* Scraping target information from Instagram profiles (public data only)
* Cleaning and structuring the scraped output
* Exploratory data analysis using Python
* Visual analysis using charts/graphs

## Data Collection Method

Influencer accounts were identified using:

* ChatGPT Deep Research (to shortlist relevant influencers based on the given criteria)
* Manual verification and curation (to ensure accuracy and relevance)

> Note: Only public information is included. No private data is accessed or stored.

## Scraping Method

**Approach:** Code-based scraping using Python.

### What was scraped (example fields)

* Username / handle
* Display name (if public)
* Followers / following counts
* Post count
* Bio text (if public)
* Category/keywords (derived from bio/content where applicable)
* Engagement-related info (if included in your script)

### Output Format

Scraped data is saved as:

* CSV (recommended) and/or JSON

## Data Analysis

After scraping:

* Data cleaning (handling missing values, formatting numbers, removing duplicates)
* Feature creation (optional: engagement rate estimate, category labels, etc.)
* Summary statistics (top influencers, ranges, averages, distributions)
* Visualizations (bar charts, histograms, scatter plots, etc.)

## Visualizations

Graphs are generated using Python (Matplotlib / Seaborn if used).
Examples:

* Followers distribution
* Top N influencers by followers
* Category distribution (if available)
* Relationship between followers and engagement (if available)

## Tech Stack

* Python 3.x
* Libraries (typical): pandas, numpy, matplotlib (plus any scraping libs used in your code)

## Project Structure (example)

```text
.
├── src/
│   ├── scraper.py
│   ├── analysis.py
│   └── utils.py
├── data/
│   ├── raw/              # optional (may be excluded from git)
│   └── processed/
├── outputs/
│   └── charts/           # saved graphs
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup & Run

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Run scraping

```bash
python src/scraper.py
```

### 3) Run analysis + generate graphs

```bash
python src/analysis.py
```

## Results

* Scraped dataset saved in: `data/processed/` (or your chosen folder)
* Graphs saved in: `outputs/charts/`

## Efficiency & Key Highlights

* Automated scraping pipeline to reduce manual effort
* Structured output (CSV/JSON) for easy reuse
* Reproducible analysis workflow (same script generates the same insights)
* Clean separation between scraping and analysis modules

## Notes & Ethics

* This project is intended for educational and research purposes.
* Only public information is collected.
* Follow Instagram’s Terms of Service and applicable laws.
* Avoid scraping at aggressive rates; use delays and respect request limits.

## Author

Kanagavalli
