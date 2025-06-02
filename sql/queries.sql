 CREATE TABLE hacienda_import (
    anio INT,
    mes INT,
    codigoNivel INT,
    descripcionNivel VARCHAR(100),
    codigoEntidad INT,
    descripcionEntidad VARCHAR(150),
    codigoUnidadResponsable INT,
    descripcionUnidadResponsable VARCHAR(200),
    codigoTipoPresupuesto_ClasePrograma INT,
    descripcionTipoPresupuesto_ClasePrograma VARCHAR(200),
    codigoPrograma INT,
    descripcionPrograma VARCHAR(150),
    codigoSubprograma INT,
    descripcionSubprograma VARCHAR(150),
    codigoProyecto_Actividad INT,
    descripcionProyecto_Actividad VARCHAR(200),
    codigoFinalidad INT,
    finalidad VARCHAR(100),
    codigoFuncion INT,
    funcion VARCHAR(100),
    codigoSubfuncion INT,
    subfuncion VARCHAR(100),
    grupoEconomico VARCHAR(100),
    subgrupoEconomico VARCHAR(100),
    categoriaEconomica VARCHAR(100),
    codigoFuenteFinanciamiento INT,
    descripcionFuenteFinanciamiento VARCHAR(200),
    codigoGrupoObjetoGasto INT,
    grupoObjetoGasto VARCHAR(100),
    codigoSubgrupoObjetoGasto INT,
    subgrupoObjetoGasto VARCHAR(100),
    codigoObjetoGasto INT,
    objetoGasto VARCHAR(100),
    codigoOrganismoFinanciador INT,
    descripcionOrganismoFinanciador VARCHAR(150),
    codigoDepartamento INT,
    departamento VARCHAR(100),
    codigoUAF INT,
    descripcionUAF VARCHAR(150),
    codigoNivelFinanciero INT,
    nombreNivelFinanciero VARCHAR(100),
    codigoClasificacion VARCHAR(50),
    descripcionClasificacion VARCHAR(150),
    presupuestoInicialAprobado BIGINT,
    montoVigente BIGINT,
    montoPlanFinancieroVigente BIGINT,
    montoEjecutado BIGINT,
    montoTransferido BIGINT,
    montoPagado BIGINT,
    mesCorte INT,
    anioCorte INT,
    fechaCorte DATE
);

-- el path tiene que ser donde vayan las descargas del scraper
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\pgn-gasto_2019-01.csv'
INTO TABLE hacienda_import
CHARACTER SET latin1
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    anio,
    mes,
    codigoNivel,
    descripcionNivel,
    codigoEntidad,
    descripcionEntidad,
    codigoUnidadResponsable,
    descripcionUnidadResponsable,
    codigoTipoPresupuesto_ClasePrograma,
    descripcionTipoPresupuesto_ClasePrograma,
    codigoPrograma,
    descripcionPrograma,
    codigoSubprograma,
    descripcionSubprograma,
    codigoProyecto_Actividad,
    descripcionProyecto_Actividad,
    codigoFinalidad,
    finalidad,
    codigoFuncion,
    funcion,
    codigoSubfuncion,
    subfuncion,
    grupoEconomico,
    subgrupoEconomico,
    categoriaEconomica,
    codigoFuenteFinanciamiento,
    descripcionFuenteFinanciamiento,
    codigoGrupoObjetoGasto,
    grupoObjetoGasto,
    codigoSubgrupoObjetoGasto,
    subgrupoObjetoGasto,
    codigoObjetoGasto,
    objetoGasto,
    codigoOrganismoFinanciador,
    descripcionOrganismoFinanciador,
    codigoDepartamento,
    departamento,
    codigoUAF,
    descripcionUAF,
    codigoNivelFinanciero,
    nombreNivelFinanciero,
    codigoClasificacion,
    descripcionClasificacion,
    presupuestoInicialAprobado,
    montoVigente,
    montoPlanFinancieroVigente,
    montoEjecutado,
    montoTransferido,
    montoPagado,
    mesCorte,
    anioCorte,
    fechaCorte
);
 -- crear tabla para cada año en base a la importación con solo datos del MEC
CREATE TABLE hacienda_2019 AS
SELECT *
FROM hacienda_import
WHERE descripcionEntidad = '007-MINISTERIO DE EDUCACIÓN Y CIENCIAS';

-- borrar los datos de la tabla de importación
TRUNCATE hacienda_import;

-- una vez que se tenga la tabla del MEC año x, eliminar las columnas que no nos sirvan
-- haz lo mismo con una tabla extra donde iran todos los años juntos despues
alter table hacienda_2019
drop column anioCorte, 
drop column mesCorte, 
drop column codigoClasificacion,  
drop column codigoNivelFinanciero,
drop column codigoUAF,
drop column codigoDepartamento,
drop column codigoOrganismoFinanciador,
drop column codigoObjetoGasto,
drop column codigoSubgrupoObjetoGasto,
drop column codigoGrupoObjetoGasto,
drop column codigoFuenteFinanciamiento,
drop column codigoSubfuncion,
drop column codigoFuncion,
drop column codigoFinalidad,
drop column codigoProyecto_Actividad,
drop column codigoSubprograma,
drop column codigoPrograma,
drop column codigoTipoPresupuesto_ClasePrograma,
drop column codigoUnidadResponsable,
drop column codigoEntidad,
drop column codigoNivel;

-- borrar todos los datos que no sean los más recientes según la fecha de corte
DELETE t
FROM hacienda_2019 t
LEFT JOIN (
  SELECT mes, MAX(fechaCorte) AS max_fechaCorte
  FROM hacienda_2023
  GROUP BY mes
) sub
  ON t.mes = sub.mes AND t.fechaCorte = sub.max_fechaCorte
WHERE sub.mes IS NULL;

-- en caso de error 1175 ejecuta esto y volve a ejecutar delete
SET SQL_SAFE_UPDATES = 0;

--chequea duplicados, especificamente cuantos duplicados hay ademas del original (cuantas filas habria que borrar)
SELECT SUM(dup_count - 1) AS redundant_duplicates
FROM (
    SELECT COUNT(*) AS dup_count
    FROM hacienda_2019
    GROUP BY anio, mes, descripcionNivel, descripcionEntidad, descripcionUnidadResponsable, descripcionTipoPresupuesto_ClasePrograma, descripcionPrograma, descripcionSubprograma, descripcionProyecto_Actividad, finalidad, funcion, subfuncion, grupoEconomico, subgrupoEconomico, categoriaEconomica, descripcionFuenteFinanciamiento, grupoObjetoGasto, objetoGasto, descripcionOrganismoFinanciador, departamento, descripcionUAF, nombreNivelFinanciero, descripcionClasificacion, presupuestoInicialAprobado, montoVigente, montoPlanFinancieroVigente, montoEjecutado, montoTransferido, montoPagado, fechaCorte
    HAVING COUNT(*) > 1
) AS duplicates;

-- en caso de que hayan duplicados
CREATE TABLE hacienda_2019_unique AS
SELECT DISTINCT *
FROM hacienda_2019;

-- una vez que tengas las tablas para todos los años, uni en una sola
INSERT INTO mec_hacienda
SELECT * FROM hacienda_2019
UNION ALL
SELECT * FROM hacienda_2020
UNION ALL
SELECT * FROM hacienda_2021
UNION ALL
SELECT * FROM hacienda_2022
UNION ALL
SELECT * FROM hacienda_2023
UNION ALL
SELECT * FROM hacienda_2024;

-- exporta en un csv si deseas
select * from mec_hacienda
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.4/Uploads/hacienda_mec.csv' 
FIELDS ENCLOSED BY '"' 
TERMINATED BY ';' 
ESCAPED BY '"' 
LINES TERMINATED BY '\r\n';


-- crea tabla para cambio a usd
create table bcp (
anio INT,
mes INT,
compra REAL);

-- cambia el archivo para insertar valores de cada año
LOAD DATA INFILE 'C:\\ruta\\csv'
INTO TABLE bcp
CHARACTER SET latin1
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    anio,
    mes,
    compra);

-- añadi columnas donde iran los montos en dolares
ALTER TABLE mec_hacienda
ADD COLUMN presupuesto_usd FLOAT,
ADD COLUMN montoVigente_usd FLOAT,
ADD COLUMN montoPlanFinanciero_usd FLOAT,
ADD COLUMN montoEjecutado_usd FLOAT,
ADD COLUMN montoTransferido_usd FLOAT,
ADD COLUMN montoPagado_usd FLOAT;

-- convertir los guranies a dolares en las nuevas columnas
UPDATE mec_hacienda a
JOIN bcp b ON a.anio = b.anio AND a.mes = b.mes
SET
  a.presupuesto_usd  = a.presupuestoInicialAprobado / NULLIF(b.compra, 0),
  a.montoVigente_usd = a.montoVigente / NULLIF(b.compra, 0),
  a.montoPlanFinanciero_usd = a.montoPlanFinancieroVigente / NULLIF(b.compra, 0),
  a.montoEjecutado_usd = a.montoEjecutado / NULLIF(b.compra, 0),
  a.montoTransferido_usd = a.montoTransferido / NULLIF(b.compra, 0),
  a.montoPagado_usd = a.montoPagado / NULLIF(b.compra, 0);




