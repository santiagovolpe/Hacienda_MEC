--cambia el titulo para cada año y la tabla final 
CREATE TABLE hacienda_2019 (
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
INTO TABLE hacienda_2019
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

-- una vez que se importen los 12 meses del año quita las columnas innecesarias
-- hace lo mismo con una tabla extra donde iran todos los años juntos despues
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

-- revisa las entidades y elegi, yo elegi el MEC
select distinct(descripcionEntidad) from hacienda_2019;
-- se borra el resto
delete from hacienda_2019 where descripcionEntidad not like '007-MINISTERIO DE EDUCACIÓN Y CIENCIAS';

--chequea duplicados, especificamente cuantos duplicados hay ademas del original (cuantas filas habria que borrar)
SELECT SUM(dup_count - 1) AS redundant_duplicates
FROM (
    SELECT COUNT(*) AS dup_count
    FROM hacienda_2020
    GROUP BY anio, mes, descripcionNivel, descripcionEntidad, descripcionUnidadResponsable, descripcionTipoPresupuesto_ClasePrograma, descripcionPrograma, descripcionSubprograma, descripcionProyecto_Actividad, finalidad, funcion, subfuncion, grupoEconomico, subgrupoEconomico, categoriaEconomica, descripcionFuenteFinanciamiento, grupoObjetoGasto, objetoGasto, descripcionOrganismoFinanciador, departamento, descripcionUAF, nombreNivelFinanciero, descripcionClasificacion, presupuestoInicialAprobado, montoVigente, montoPlanFinancieroVigente, montoEjecutado, montoTransferido, montoPagado, fechaCorte
    HAVING COUNT(*) > 1
) AS duplicates;

-- en caso de que hayan duplicados
CREATE TABLE hacienda_2019_unique AS
SELECT DISTINCT *
FROM hacienda_2019;

-- una vez que tengas las tablas para todos los años, uni en una sola
INSERT INTO mec_hacienda
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
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.4/Uploads/hacienda_MEC.csv' 
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
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\usdavg2019.csv'
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




