-- SQL script to list all bands with Glam rock as their main style, ranked by their longevity
SELECT
    band_name,
    IF(splitted.lifespan IS NULL, 0, splitted.lifespan) AS lifespan
FROM
    (
        SELECT
            band_name,
            FLOOR((DATEDIFF(2022, formed) + 1) / 365) AS lifespan
        FROM
            metal_bands
    ) AS splitted
    RIGHT JOIN glam_rock_bands AS glam
    ON splitted.band_name = glam.band_name
ORDER BY
    lifespan DESC, band_name;
