----Promedio de indicadores por departamento
SELECT 
d.nombre_departamento,
AVG(m.resultado) promedio_indicador
FROM medicion m
JOIN ips i ON m.id_ips = i.id_ips
JOIN municipio mu ON i.cod_municipio = mu.cod_municipio
JOIN departamento d ON mu.cod_departamento = d.cod_departamento
GROUP BY d.nombre_departamento;

----Top IPS con mejores resultados
SELECT 
i.nombre_ips,
AVG(m.resultado) promedio
FROM medicion m
JOIN ips i ON m.id_ips = i.id_ips
GROUP BY i.nombre_ips
ORDER BY promedio DESC;

----Indicadores por servicio
SELECT 
ind.servicio,
COUNT(*) total_registros
FROM medicion m
JOIN indicador ind
ON m.id_indicador = ind.id_indicador
GROUP BY ind.servicio;