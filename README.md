Une petite interface pour montrer les votes des députés

## Ingestion des données

```
mkdir data
cd data
wget http://data.assemblee-nationale.fr/static/openData/repository/15/amo/deputes_actifs_csv_opendata/liste_deputes_libre_office.csv
wget http://data.assemblee-nationale.fr/static/openData/repository/15/loi/dossiers_legislatifs/Dossiers_Legislatifs_XV.json.zip
wget http://data.assemblee-nationale.fr/static/openData/repository/15/loi/scrutins/Scrutins_XV.json.zip
dtrx *.zip
anpy-cli scrutins > scrutins.jsonl
cd ..
./manage.py import_deputes data/liste_deputes_libre_office.csv
./manage.py import_dossiers "data/Dossiers_Legislatifs_XV.json/json/dossierParlementaire/*.json"
./manage.py import_votes "data/Scrutins_XV.json/json/*.json" data/scrutins.jsonl
```
