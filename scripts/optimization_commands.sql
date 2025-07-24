-- 🚀 COMANDOS DE OPTIMIZACIÓN PARA COPIAR Y PEGAR
-- Ejecutar estos comandos uno por uno en tu cliente de base de datos
-- ========================================

-- [ 1] Comando 1
CREATE INDEX IF NOT EXISTS idx_tickets_type_service;

-- [ 2] Comando 2
CREATE INDEX IF NOT EXISTS idx_tickets_creation_date;

-- [ 3] Comando 3
CREATE INDEX IF NOT EXISTS idx_tickets_pagination;

-- [ 4] Comando 4
CREATE INDEX IF NOT EXISTS idx_tickets_state;

-- [ 5] Comando 5
CREATE INDEX IF NOT EXISTS idx_tickets_city;

-- [ 6] Comando 6
CREATE INDEX IF NOT EXISTS idx_tickets_filters;

-- [ 7] Comando 7
CREATE INDEX IF NOT EXISTS idx_tickets_document_client;

-- [ 8] Comando 8
CREATE INDEX IF NOT EXISTS idx_tickets_reference;

-- [ 9] Comando 9
CREATE INDEX IF NOT EXISTS idx_tickets_imei;

-- [10] Comando 10
CREATE INDEX IF NOT EXISTS idx_tickets_technical_name;

-- [11] Comando 11
CREATE INDEX IF NOT EXISTS idx_problems_tickets_ticket_id;

-- [12] Comando 12
CREATE INDEX IF NOT EXISTS idx_problems_tickets_problem_id;

-- [13] Comando 13
CREATE INDEX IF NOT EXISTS idx_spares_tickets_ticket_id;

-- [14] Comando 14
CREATE INDEX IF NOT EXISTS idx_tickets_service_value;

-- [15] Comando 15
CREATE INDEX IF NOT EXISTS idx_tickets_total;

-- [16] Comando 16
CREATE INDEX IF NOT EXISTS idx_tickets_assigned_date;

-- [17] Comando 17
CREATE INDEX IF NOT EXISTS idx_tickets_finished_date;

-- [18] Comando 18
CREATE INDEX IF NOT EXISTS idx_tickets_tracking;

-- [19] Comando 19
CREATE INDEX IF NOT EXISTS idx_technical_service_active;

-- [20] Comando 20
CREATE INDEX IF NOT EXISTS idx_warranties_active;

-- [21] Comando 21
CREATE INDEX IF NOT EXISTS idx_internal_repair_active;

-- [22] Comando 22
CREATE INDEX IF NOT EXISTS idx_employees_cargo;

-- [23] Comando 23
CREATE INDEX IF NOT EXISTS idx_employees_document;

-- [24] Comando 24
ANALYZE tickets;

-- [25] Comando 25
ANALYZE problems_tickets;

-- [26] Comando 26
ANALYZE spares_tickets;

-- [27] Comando 27
ANALYZE empleados;

-- ========================================
-- ✅ Para verificar que se crearon correctamente:
-- SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;
