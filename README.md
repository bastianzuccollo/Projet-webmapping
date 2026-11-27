On commence par préparer les données.
On fait les calculs sur communes_precis puis on transfert les résultats par communes avec une jointure grace aux ID.
On peut ainsi afficher la couche communes qui est plus légère avec des valeurs précises.
On remarque que les communes sont en EPSG:2154 et les aires en EPSG:4326
On reprojette les couches en EPSG:2154
On a beaucoup de communes à la frontière de l'aire. On décide de les conserver
Sur téléphone on ne voit pas les bordures des communes
