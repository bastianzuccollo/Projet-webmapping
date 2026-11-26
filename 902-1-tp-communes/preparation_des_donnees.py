# Préparation des données

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path


# Chargement des données
communes = gpd.read_file("902-1-tp-communes/donnees/communes_64_65.gpkg", layer="communes")

communes_precis = gpd.read_file("902-1-tp-communes/donnees/communes_64_65.gpkg", layer="communes_precis")

pnp_coeur = gpd.read_file("902-1-tp-communes/donnees/pnp_coeur.geojson")

pnp_aire = gpd.read_file("902-1-tp-communes/donnees/pnp_aire_adhesion.geojson")

#Reprojection
pnp_coeur = pnp_coeur.to_crs(communes_precis.crs)
pnp_aire = pnp_aire.to_crs(communes_precis.crs)

coeur_union = pnp_coeur.geometry.union_all()
aire_union = pnp_aire.geometry.union_all()

#Calcul intersections
intersections_coeur = communes_precis.geometry.intersection(coeur_union)
communes_precis["surface_coeur_km2"] = (intersections_coeur.area / 1_000_000)
communes_precis["dans_coeur"] = (~intersections_coeur.is_empty)
intersections_aire = communes_precis.geometry.intersection(aire_union)
communes_precis["surface_aire_km2"] = (intersections_aire.area / 1_000_000)
communes_precis["dans_aire_adhesion"] = (~intersections_aire.is_empty)

communes_precis["surface_totale_km2"] = (communes_precis.geometry.area / 1_000_000)
communes_precis["part_coeur_pct"] = (communes_precis["surface_coeur_km2"]/ communes_precis["surface_totale_km2"]* 100)

#Jointure
indicateurs = communes_precis[
    [
        "code_insee",
        "dans_coeur",
        "dans_aire_adhesion",
        "surface_coeur_km2",
        "surface_aire_km2",
        "surface_totale_km2",
        "part_coeur_pct"
    ]].copy()

communes_finales = communes.merge(indicateurs, on="code_insee", how="left", validate="one_to_one")
# On créer un indicateur dans le parc pour filtrer
communes_finales["dans_parc"] = (communes_finales["dans_coeur"] | communes_finales["dans_aire_adhesion"])

communes_finales = communes_finales[communes_finales["dans_parc"]].copy()

# Export
communes_finales.to_file("902-1-tp-communes/donnees/communes_pnp.gpkg", layer="communes", driver="GPKG")

#On calcul un point représentatif pour chaque communes
couche_points = communes_finales.copy()
couche_points.geometry = couche_points.geometry.representative_point()

couche_coeur = pnp_coeur.to_crs(communes_finales.crs)
couche_aire = pnp_aire.to_crs(communes_finales.crs)

#On créer un gpkg avec toutes les couches 
GPKG_COMPLET = Path("902-1-tp-communes/donnees/Couches_TP.gpkg")

GPKG_COMPLET.unlink(missing_ok=True)

communes_finales.to_file( GPKG_COMPLET, layer="communes", driver="GPKG", mode="w")
couche_points.to_file(GPKG_COMPLET, layer="communes_points", driver="GPKG", mode="a")
couche_coeur.to_file(GPKG_COMPLET, layer="coeur", driver="GPKG", mode="a")
couche_aire.to_file(GPKG_COMPLET, layer="aire", driver="GPKG", mode="a")

# Conversion du GeoPackage en PMTiles

from pathlib import Path
import subprocess

GPKG = Path("902-1-tp-communes/donnees/Couches_TP.gpkg")
PMTILES = Path("902-1-tp-communes/donnees/Couches_TP.pmtiles")

# Supprimer l'ancien PMTiles
PMTILES.unlink(missing_ok=True)

subprocess.run([
    "ogr2ogr",
    "-f", "PMTiles",
    str(PMTILES),
    str(GPKG),
    "-dsco", "MINZOOM=6",
    "-dsco", "MAXZOOM=14",
    "-preserve_fid"
], check=True)