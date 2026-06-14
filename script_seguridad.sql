-- ============================================================
-- SCRIPT SEGURIDAD - FARMA SEGURA
-- Ejecutar en: farmasegura_seguridad (Clever Cloud)
-- Nota: No incluye CREATE DATABASE, ni usuarios, ni triggers conflictivos
-- ============================================================

USE farmasegura_seguridad;

-- Tablas de seguridad
CREATE TABLE auditoria_log (
    id_log BIGINT NOT NULL AUTO_INCREMENT,
    fecha_hora DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    usuario_real VARCHAR(100) NOT NULL,
    tabla_afectada VARCHAR(100) NOT NULL,
    operacion ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    valores_anteriores LONGTEXT NULL,
    valores_nuevos LONGTEXT NULL,
    ip_origen VARCHAR(50) NULL,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB;

CREATE TABLE intentos_login (
    id_intento INT NOT NULL AUTO_INCREMENT,
    usuario VARCHAR(50) NOT NULL,
    ip_origen VARCHAR(45) NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    exitoso TINYINT(1) NOT NULL,
    PRIMARY KEY (id_intento)
) ENGINE=InnoDB;

CREATE TABLE sesiones_usuarios (
    id_sesion INT NOT NULL AUTO_INCREMENT,
    id_empleado INT NOT NULL COMMENT 'Referencia a empleados de BD_OPERATIVA',
    token_sesion VARCHAR(255) NOT NULL,
    fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME NULL,
    ip VARCHAR(45) NULL,
    user_agent TEXT NULL,
    activa TINYINT(1) DEFAULT 1,
    PRIMARY KEY (id_sesion)
) ENGINE=InnoDB;

CREATE TABLE historial_contrasenas (
    id_historial INT NOT NULL AUTO_INCREMENT,
    id_empleado INT NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    fecha_cambio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cambiado_por VARCHAR(100) NULL,
    PRIMARY KEY (id_historial)
) ENGINE=InnoDB;

CREATE TABLE eventos_seguridad (
    id_evento INT NOT NULL AUTO_INCREMENT,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_evento VARCHAR(50) NOT NULL,
    gravedad ENUM('BAJA','MEDIA','ALTA','CRITICA') NOT NULL,
    descripcion TEXT NULL,
    id_empleado_afectado INT NULL,
    ip_origen VARCHAR(50) NULL,
    PRIMARY KEY (id_evento)
) ENGINE=InnoDB;

CREATE TABLE alertas_seguridad (
    id_alerta INT NOT NULL AUTO_INCREMENT,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_alerta VARCHAR(50) NOT NULL,
    descripcion TEXT NULL,
    estado ENUM('PENDIENTE','LEIDA','RESUELTA') DEFAULT 'PENDIENTE',
    id_empleado_destino INT NULL,
    PRIMARY KEY (id_alerta)
) ENGINE=InnoDB;

CREATE TABLE password_reset_tokens (
    id_token INT NOT NULL AUTO_INCREMENT,
    id_empleado INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expiracion DATETIME NOT NULL,
    usado TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_token)
) ENGINE=InnoDB;

-- Datos de prueba (opcional, pueden insertarse algunos registros de ejemplo)
-- Nota: Los triggers de auditoría que escriben en esta base se omiten por el mismo motivo.