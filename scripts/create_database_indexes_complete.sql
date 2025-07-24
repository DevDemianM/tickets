-- ========================================
-- 🚀 OPTIMIZACIÓN DE BASE DE DATOS - PASO 2 - COMPLETO
-- Creación de índices para máximo rendimiento
-- Estimación: 60-80% mejora adicional en consultas
-- ========================================

-- 1. 🎯 ÍNDICES PRINCIPALES PARA TICKETS

-- Índice para tipo de servicio
CREATE INDEX IF NOT EXISTS idx_tickets_type_service 
ON tickets(type_of_service);

-- Índice para fecha de creación (ordenamiento principal)
CREATE INDEX IF NOT EXISTS idx_tickets_creation_date 
ON tickets(creation_date DESC);

-- Índice compuesto PRINCIPAL para paginación optimizada
CREATE INDEX IF NOT EXISTS idx_tickets_pagination 
ON tickets(type_of_service, creation_date DESC);

-- Índice para estado (filtros frecuentes)
CREATE INDEX IF NOT EXISTS idx_tickets_state 
ON tickets(state);

-- Índice para ciudad (filtros geográficos)
CREATE INDEX IF NOT EXISTS idx_tickets_city 
ON tickets(city);

-- Índice compuesto para filtros múltiples
CREATE INDEX IF NOT EXISTS idx_tickets_filters 
ON tickets(type_of_service, state, city);

-- 2. 🔍 ÍNDICES PARA BÚSQUEDAS

-- Índice para documento de cliente (búsquedas frecuentes)
CREATE INDEX IF NOT EXISTS idx_tickets_document_client 
ON tickets(document_client);

-- Índice para IMEI (búsquedas de productos)
CREATE INDEX IF NOT EXISTS idx_tickets_imei 
ON tickets(IMEI);

-- Índice para nombre del técnico
CREATE INDEX IF NOT EXISTS idx_tickets_technical_name 
ON tickets(technical_name);

-- 3. 🛠️ ÍNDICES PARA RELACIONES

-- Índice para problemas de tickets
CREATE INDEX IF NOT EXISTS idx_problems_tickets_ticket_id 
ON problems_tickets(id_ticket);

-- Índice para repuestos de tickets
CREATE INDEX IF NOT EXISTS idx_spares_tickets_ticket_id 
ON spares_tickets(id_ticket);

-- 4. 📅 ÍNDICES ESPECIALIZADOS POR MÓDULO

-- Para servicio técnico (type_of_service = '0')
CREATE INDEX IF NOT EXISTS idx_technical_service_active 
ON tickets(type_of_service, state, creation_date DESC) 
WHERE type_of_service = '0';

-- Para garantías (type_of_service = '2')
CREATE INDEX IF NOT EXISTS idx_warranties_active 
ON tickets(type_of_service, state, creation_date DESC) 
WHERE type_of_service = '2';

-- Para reparación interna (type_of_service = '1')
CREATE INDEX IF NOT EXISTS idx_internal_repair_active 
ON tickets(type_of_service, state, creation_date DESC) 
WHERE type_of_service = '1';

-- 5. 👥 ÍNDICES PARA EMPLEADOS

CREATE INDEX IF NOT EXISTS idx_employees_cargo 
ON empleados(cargo);

CREATE INDEX IF NOT EXISTS idx_employees_document 
ON empleados(document);

-- 6. 📊 ANALIZAR TABLAS PARA ESTADÍSTICAS

ANALYZE tickets;
ANALYZE problems_tickets;
ANALYZE spares_tickets;
ANALYZE empleados; 