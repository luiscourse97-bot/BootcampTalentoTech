CREATE TABLE departamento(
    cod_departamento INT PRIMARY KEY,
    nombre_departamento VARCHAR(100)
);

CREATE TABLE municipio(
    cod_municipio INT PRIMARY KEY,
    nombre_municipio VARCHAR(100),
    cod_departamento INT,
    FOREIGN KEY (cod_departamento) REFERENCES departamento(cod_departamento)
);

CREATE TABLE ips(
    id_ips INT PRIMARY KEY,
    nombre_ips VARCHAR(200),
    cod_municipio INT,
    FOREIGN KEY (cod_municipio) REFERENCES municipio(cod_municipio)
);

CREATE TABLE indicador(
    id_indicador INT PRIMARY KEY AUTOINCREMENT,
    nombre_indicador VARCHAR(300),
    categoria VARCHAR(200),
    servicio VARCHAR(200),
    especificacion VARCHAR(200)
);

CREATE TABLE medicion(
    id_medicion INT PRIMARY KEY AUTOINCREMENT,
    id_ips INT,
    id_indicador INT,
    numerador FLOAT,
    denominador FLOAT,
    resultado FLOAT,
    unidad VARCHAR(50),
    fuente VARCHAR(200),
    enlace VARCHAR(500),
    periodo INT,
    FOREIGN KEY (id_ips) REFERENCES ips(id_ips),
    FOREIGN KEY (id_indicador) REFERENCES indicador(id_indicador)
);