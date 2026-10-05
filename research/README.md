# ÁguaTwin IA — reproducible exploratory study, 2026-10-04

Two separate tasks use real SGB/SIAGAS public historical well records in Paraíba.

1. **Production evidence versus dry status**: 3,022 tubular-well records in 204 municipalities. Class 1 requires positive specific yield and status other than `Seco`; class 0 requires status `Seco` without positive specific yield. Of 3,046 eligible records, 24 contradictory records were excluded. Missing production is never assumed to mean dry. This is cadastral status, not a dated successful/unsuccessful drilling outcome.
2. **Salinity**: 8,234 records in 223 municipalities with positive depth and electrical conductivity. Class 1 means EC > 3,000 µS/cm. This threshold is an irrigation salinity screening reference, not a potability classifier.

Features are latitude, longitude and well depth. The depth selected for an unobserved site is a scenario, not a causal estimate of what drilling deeper would accomplish. Geology, fractures, terrain, rainfall and pumping dates are absent from these predictors.

Run `fetch_paraiba.py`, `prepare_state_dataset.py`, `fetch_potential.py`, then `compare_five_models.py` with Python 3, NumPy 2.3.5 and scikit-learn 1.8.0. Source URLs, hashes, rejected identifiers and class definitions are in the validation JSON.

KNN, Random Forest, Gaussian Naive Bayes, K-means and a NumPy CNN 1D are compared with the same five spatial GroupKFold splits, based on a 0.04-degree latitude/longitude grid. Scaling and K-means cluster-to-label assignment use training observations only. No hyperparameter selection uses the test folds. CNN analytic gradients pass central finite-difference checks. CNN convolves ordered tabular features, not satellite imagery. K-means is a clustering comparator with train-only majority labels. Pooled out-of-fold metrics include confusion matrices and minority-class recall.

There is no spatial buffer, temporal or prospective independent validation. The selected well catalog is not a random sample of the state. Metrics cannot be interpreted as the probability of groundwater at a proposed drill site. Model scores are not calibrated probabilities. Domain screening (feature ranges and nearest observation within 5 km) is a practical heuristic, not a certified area-of-applicability estimate.

NASA POWER daily API provides precipitation, air temperature and solar irradiation for the water/solar scenario. It is not used as an ML covariate in this version. Browser queries request UTC, validate units and complete daily observations, and preserve the last valid climate series on failure. Rainfall is climatic context, not proof of recharge or groundwater availability.

Candidate points are an exploratory grid ranked by the final Random Forest score. They need hydrogeological verification, access and legal checks, and suitable geophysics before any drilling decision. Water availability needs a pumping test; drinking-water safety needs chemical and microbiological laboratory analysis. This prototype is not a calibrated hydrogeological digital twin.

Related research: Souza et al. (2023), doi:10.14393/rbcv75n0a-65381; Vio et al. (2025), doi:10.28998/contegeo.10i.24.18434. Their existence does not establish novelty for this combination; a systematic novelty review and independent field validation remain to be done.

## v2.1 extension

Run `fetch_hydrogeology.py`, then `train_hydrogeology.py` with Shapely 2.1.2 and the pinned NumPy/scikit-learn versions. Raw descriptive SGB layers are preserved in `hydro_layers_source.zip` with provenance and hashes. `dist/hydro_context.json` is the shared simplified geometry used by training and browser. Unzipped raw layers and `hydro_features.json` are regeneratable outputs, ignored by Git. The geological RF comparison uses the same spatial splits with 0/2/5 km buffers, fixed feature sets and train-only category encoding. No observed depth is required by the deployed new-site RF. Geological inputs did not improve the production task. Scores and tree dispersion are exploratory, uncalibrated quantities.

`import_field_reports.py` audits human-reviewed dated evidence; community text creates investigation leads only. No field reports have been collected or used in current training. Future measured outcomes must remain distinct from historical SIAGAS status and reserve independent sites/time periods before model updates.

The decision module conserves water and salts under common energy/cost constraints. Initial alternatives are hypothetical. The conditional-volume criterion considers only a user-selected salt limit and cannot certify drinking water or irrigation suitability. See `docs/AGUA_RURAL_NORDESTE.md` for the prospective rural protocol and `docs/RESULTADOS_V2_1.md` for all 18 evaluation configurations. `npm test` runs DOM/model/physics and report-audit verification; it is not field validation.
