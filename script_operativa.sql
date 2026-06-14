-- ============================================================
-- FARMA SEGURA - BASE OPERATIVA (tablas de negocio)
-- ============================================================

-- Tablas
CREATE TABLE sucursales (
    id_sucursal   INT          NOT NULL AUTO_INCREMENT,
    nombre        VARCHAR(100) NOT NULL,
    ciudad        VARCHAR(100) NOT NULL,
    direccion     VARCHAR(200) NOT NULL,
    PRIMARY KEY (id_sucursal)
);

CREATE TABLE empleados (
    id_empleado   INT          NOT NULL AUTO_INCREMENT,
    nombre        VARCHAR(150) NOT NULL,
    usuario       VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol           ENUM('FARMACEUTICO','GERENTE','AUDITOR','ADMINISTRADOR') NOT NULL,
    id_sucursal   INT          NULL,
    activo        TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id_empleado),
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal)
);

CREATE TABLE clientes (
    id_cliente           INT          NOT NULL AUTO_INCREMENT,
    nombre               VARCHAR(150) NOT NULL,
    cedula               VARCHAR(20)  NOT NULL UNIQUE,
    telefono             VARCHAR(20)  NULL,
    direccion            VARCHAR(200) NULL,
    sucursal_registro_id INT          NOT NULL,
    PRIMARY KEY (id_cliente),
    FOREIGN KEY (sucursal_registro_id) REFERENCES sucursales(id_sucursal)
);

CREATE TABLE medicamentos (
    id_medicamento INT            NOT NULL AUTO_INCREMENT,
    nombre         VARCHAR(150)   NOT NULL,
    precio         DECIMAL(10,2)  NOT NULL,
    stock          INT            NOT NULL DEFAULT 0,
    id_sucursal    INT            NOT NULL,
    PRIMARY KEY (id_medicamento),
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal)
);

CREATE TABLE ventas (
    id_venta    INT            NOT NULL AUTO_INCREMENT,
    fecha       DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_cliente  INT            NOT NULL,
    id_empleado INT            NOT NULL,
    id_sucursal INT            NOT NULL,
    total       DECIMAL(10,2)  NOT NULL,
    PRIMARY KEY (id_venta),
    FOREIGN KEY (id_cliente)  REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal)
);

CREATE TABLE detalle_ventas (
    id_detalle      INT           NOT NULL AUTO_INCREMENT,
    id_venta        INT           NOT NULL,
    id_medicamento  INT           NOT NULL,
    cantidad        INT           NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_detalle),
    FOREIGN KEY (id_venta)       REFERENCES ventas(id_venta) ON DELETE CASCADE,
    FOREIGN KEY (id_medicamento) REFERENCES medicamentos(id_medicamento)
);

-- Vistas públicas
CREATE OR REPLACE VIEW vw_empleados_public AS
SELECT id_empleado, nombre, usuario, rol, id_sucursal, activo FROM empleados;

CREATE OR REPLACE VIEW vw_clientes_public AS
SELECT id_cliente, nombre, cedula, CONCAT(LEFT(telefono, 4), '****') AS telefono, direccion, sucursal_registro_id FROM clientes;

CREATE OR REPLACE VIEW vw_medicamentos_public AS
SELECT id_medicamento, nombre, precio, stock, id_sucursal FROM medicamentos;

CREATE OR REPLACE VIEW vw_ventas_public AS
SELECT v.id_venta, v.fecha, v.total, v.id_sucursal, c.nombre AS cliente_nombre, e.nombre AS empleado_nombre
FROM ventas v
JOIN clientes c ON v.id_cliente = c.id_cliente
JOIN empleados e ON v.id_empleado = e.id_empleado;

CREATE OR REPLACE VIEW vw_detalle_ventas_public AS
SELECT dv.id_detalle, dv.id_venta, dv.cantidad, dv.precio_unitario, m.nombre AS medicamento_nombre
FROM detalle_ventas dv
JOIN medicamentos m ON dv.id_medicamento = m.id_medicamento;

-- Procedimiento almacenado para insertar ventas (no usa triggers)
DELIMITER $$
CREATE PROCEDURE sp_insertar_venta(
    IN p_id_cliente INT,
    IN p_id_empleado INT,
    IN p_id_sucursal INT,
    IN p_items JSON
)
BEGIN
    DECLARE v_total DECIMAL(10,2) DEFAULT 0;
    DECLARE v_precio DECIMAL(10,2);
    DECLARE v_stock INT;
    DECLARE v_id_med INT;
    DECLARE v_cant INT;
    DECLARE v_id_venta INT;
    DECLARE v_idx INT DEFAULT 0;
    DECLARE v_len INT;

    SET v_len = JSON_LENGTH(p_items);
    IF v_len = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La venta debe tener al menos un producto';
    END IF;

    START TRANSACTION;

    INSERT INTO ventas (fecha, id_cliente, id_empleado, id_sucursal, total)
    VALUES (NOW(), p_id_cliente, p_id_empleado, p_id_sucursal, 0);

    SET v_id_venta = LAST_INSERT_ID();

    WHILE v_idx < v_len DO
        SET v_id_med = JSON_UNQUOTE(JSON_EXTRACT(p_items, CONCAT('$[', v_idx, '].id_medicamento')));
        SET v_cant   = JSON_UNQUOTE(JSON_EXTRACT(p_items, CONCAT('$[', v_idx, '].cantidad')));

        SELECT precio, stock INTO v_precio, v_stock
        FROM medicamentos
        WHERE id_medicamento = v_id_med AND id_sucursal = p_id_sucursal
        FOR UPDATE;

        IF v_precio IS NULL THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Medicamento no encontrado en esta sucursal';
        END IF;

        IF v_stock < v_cant THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente';
        END IF;

        INSERT INTO detalle_ventas (id_venta, id_medicamento, cantidad, precio_unitario)
        VALUES (v_id_venta, v_id_med, v_cant, v_precio);

        UPDATE medicamentos SET stock = stock - v_cant WHERE id_medicamento = v_id_med;


        SET v_total = v_total + (v_precio * v_cant);
        SET v_idx = v_idx + 1;
    END WHILE;

    UPDATE ventas SET total = v_total WHERE id_venta = v_id_venta;

    COMMIT;

    SELECT v_id_venta AS id_venta, v_total AS total;
END$$
DELIMITER ;

-- Datos de prueba
INSERT INTO sucursales (nombre, ciudad, direccion) VALUES
('Centro', 'La Paz', 'Av. Mariscal Santa Cruz 123'),
('Norte', 'La Paz', 'Av. Saavedra 456'),
('Sur', 'Cochabamba', 'Av. America 789');

INSERT INTO empleados (nombre, usuario, password_hash, rol, id_sucursal, activo) VALUES
('Juan Perez', 'juan_perez', '$2b$12$iRQPrqOJn.Qqsl6NJJCta.YAKhidSkkpa.33625zXbNOe3Pnr/2Hq', 'FARMACEUTICO', 1, 1),
('Maria Garcia', 'maria_garcia', '$2b$12$XCu2I/DNcvETmw9yfVxmYOuzH0nXZcutzUpHASiKrUjfTtAYoRZue', 'GERENTE', 1, 1),
('Carlos Lopez', 'carlos_lopez', '$2b$12$L9VzXYQn9wtkHNyXR5yw6.LoWb/O00YbS3cuIjLUX5HvfdCa5PjAK', 'FARMACEUTICO', 2, 1),
('Ana Rodriguez', 'ana_rodriguez', '$2b$12$QIQC6ve12bC7jFiLYY/b2eQnuwiOQv66h466fDNOsQUcHYe4zqY/e', 'GERENTE', 2, 1),
('Luis Mamani', 'luis_mamani', '$2b$12$xg3V0QY5qFOC/K12zvrDo.SMnOa0mLfmkCZag04nrcPdP3cL6NIga', 'FARMACEUTICO', 3, 1),
('Rosa Quispe', 'rosa_quispe', '$2b$12$ERLDNRerYF/Uf7zWC.JcWuvdV89J.ozZFgM3feFw1bIKCItBbesS6', 'GERENTE', 3, 1),
('Diego Vargas', 'diego_vargas', '$2b$12$04zVksp5JtsfHjVzJvLEw.eGNGDSA.8rJ4SP4sUPHV.ZiG/MFRXfe', 'AUDITOR', NULL, 1),
('Super Admin', 'admin', '$2b$12$e9C2M3kEiRovM2Iu4d5lPuRbz7LUBk81vwmDUu5tOrgQJ4HCLe86e', 'ADMINISTRADOR', NULL, 1);

INSERT INTO clientes (nombre, cedula, telefono, direccion, sucursal_registro_id) VALUES
('Pedro Morales', '1234567', '70011111', 'Calle 1 #100', 1),
('Lucia Fernandez', '2345678', '70022222', 'Calle 2 #200', 1),
('Omar Salinas', '3456789', '70033333', 'Calle 3 #300', 2),
('Elena Castro', '4567890', '70044444', 'Calle 4 #400', 2),
('Felipe Torres', '5678901', '70055555', 'Calle 5 #500', 3),
('Carmen Vega', '6789012', '70066666', 'Calle 6 #600', 3);

INSERT INTO medicamentos (nombre, precio, stock, id_sucursal) VALUES
('Paracetamol 500mg', 5.50, 100, 1),
('Ibuprofeno 400mg', 7.00, 80, 1),
('Amoxicilina 500mg', 12.00, 50, 1),
('Losartan 50mg', 15.00, 60, 1),
('Paracetamol 500mg', 5.50, 90, 2),
('Metformina 850mg', 10.00, 70, 2),
('Atorvastatina 20mg', 18.00, 40, 2),
('Omeprazol 20mg', 11.00, 55, 3),
('Amoxicilina 500mg', 12.00, 45, 3),
('Vitamina C 500mg', 4.50, 120, 3);

INSERT INTO ventas (fecha, id_cliente, id_empleado, id_sucursal, total) VALUES
('2025-01-15 10:30:00', 1, 1, 1, 18.00),
('2025-01-16 11:00:00', 2, 1, 1, 12.00),
('2025-01-17 09:00:00', 3, 3, 2, 20.00),
('2025-01-18 14:00:00', 5, 5, 3, 26.50);

INSERT INTO detalle_ventas (id_venta, id_medicamento, cantidad, precio_unitario) VALUES
(1, 1, 2, 5.50), (1, 2, 1, 7.00),
(2, 3, 1, 12.00),
(3, 6, 2, 10.00),
(4, 8, 1, 11.00), (4, 10, 3, 4.50);

-- Fin script operativa