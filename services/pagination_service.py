"""
Servicio de paginación optimizada para tablas grandes
Mantiene la misma apariencia visual pero carga datos eficientemente
"""
from sqlalchemy import func, text
from flask import request
import math


class PaginationService:
    def __init__(self, query, page_size=50, max_page_size=200):
        """
        Inicializa el servicio de paginación
        
        Args:
            query: Query de SQLAlchemy
            page_size: Tamaño de página por defecto
            max_page_size: Tamaño máximo de página permitido
        """
        self.base_query = query
        self.page_size = min(page_size, max_page_size)
        self.max_page_size = max_page_size
    
    def get_paginated_data(self, page=1, filters=None):
        """
        Obtiene datos paginados con filtros opcionales
        
        Args:
            page: Número de página (1-indexed)
            filters: Diccionario con filtros a aplicar
            
        Returns:
            Dict con datos paginados y metadatos
        """
        try:
            # Aplicar filtros si existen
            query = self.base_query
            if filters:
                query = self._apply_filters(query, filters)
            
            # Contar total de registros (optimizado)
            total_count = query.count()
            
            # Calcular paginación
            total_pages = math.ceil(total_count / self.page_size)
            page = max(1, min(page, total_pages))  # Asegurar página válida
            offset = (page - 1) * self.page_size
            
            # Obtener datos de la página actual
            items = query.offset(offset).limit(self.page_size).all()
            
            return {
                'items': items,
                'pagination': {
                    'page': page,
                    'pages': total_pages,
                    'per_page': self.page_size,
                    'total': total_count,
                    'has_prev': page > 1,
                    'has_next': page < total_pages,
                    'prev_num': page - 1 if page > 1 else None,
                    'next_num': page + 1 if page < total_pages else None
                }
            }
            
        except Exception as e:
            print(f"Error en paginación: {e}")
            return {
                'items': [],
                'pagination': {
                    'page': 1,
                    'pages': 0,
                    'per_page': self.page_size,
                    'total': 0,
                    'has_prev': False,
                    'has_next': False,
                    'prev_num': None,
                    'next_num': None
                }
            }
    
    def _apply_filters(self, query, filters):
        """
        Aplica filtros al query de manera optimizada
        
        🎯 FILTROS SOPORTADOS:
        - search: Búsqueda en IMEI, código producto, técnico, documento cliente
        - state: Estado específico del ticket  
        - state_not: Excluir un estado específico
        - city: Ciudad específica
        - date_from/date_to: Rango de fechas
        """
        for field, value in filters.items():
            if value and str(value).strip():  # Solo aplicar si hay valor
                
                if field == 'search':
                    # 🔍 BÚSQUEDA OPTIMIZADA en múltiples campos
                    search_term = f"%{value.strip()}%"
                    query = query.filter(
                        text("""(
                            IMEI LIKE :search OR 
                            product_code LIKE :search OR 
                            technical_name LIKE :search OR
                            document_client LIKE :search OR
                            CAST(id_ticket AS VARCHAR) LIKE :search
                        )""")
                    ).params(search=search_term)
                
                elif field == 'state':
                    # 🎯 FILTRO POR ESTADO ESPECÍFICO
                    query = query.filter(text("state = :state")).params(state=value)
                
                elif field == 'state_not':
                    # ❌ EXCLUIR ESTADO ESPECÍFICO (para filtro "Activos")
                    query = query.filter(text("state != :state_not")).params(state_not=value)
                
                elif field == 'city':
                    # 🏙️ FILTRO POR CIUDAD (manejo especial para tildes)
                    city_value = value.lower()
                    if city_value in ['medellin', 'medellín']:
                        query = query.filter(text("LOWER(city) LIKE '%medell%'"))
                    elif city_value in ['bogota', 'bogotá']:
                        query = query.filter(text("LOWER(city) LIKE '%bogot%'"))
                    else:
                        query = query.filter(text("LOWER(city) LIKE LOWER(:city)")).params(city=f"%{value}%")
                
                elif field == 'date_from':
                    # 📅 FILTRO FECHA DESDE
                    query = query.filter(text("creation_date >= :date_from")).params(date_from=value)
                
                elif field == 'date_to':
                    # 📅 FILTRO FECHA HASTA
                    query = query.filter(text("creation_date <= :date_to")).params(date_to=value)
                
                elif field == 'priority':
                    # ⚡ FILTRO POR PRIORIDAD
                    query = query.filter(text("priority = :priority")).params(priority=value)
        
        return query


def get_paginated_tickets(ticket_type="1", page=1, filters=None):
    """
    Función de conveniencia para obtener tickets paginados
    
    Args:
        ticket_type: Tipo de ticket ("1" para reparación interna, "2" para garantía, etc.)
        page: Número de página
        filters: Filtros a aplicar
        
    Returns:
        Datos paginados
    """
    # USAR EL MODELO DE TICKETS NORMAL
    from models.tickets import Tickets
    
    # 🎯 QUERY BASE FILTRADO POR type_of_service - ORDENADO POR ACTIVIDAD MÁS RECIENTE
    base_query = Tickets.query.filter(Tickets.type_of_service == ticket_type).order_by(Tickets.get_latest_activity_expression())
    
    # 🔧 APLICAR FILTROS
    if filters:
        for field, value in filters.items():
            if value and str(value).strip():
                if field == 'search':
                    # 🔍 BÚSQUEDA en campos del modelo de tickets normal
                    search_term = f"%{value.strip()}%"
                    base_query = base_query.filter(
                        (Tickets.IMEI.ilike(search_term)) |
                        (Tickets.technical_name.ilike(search_term)) |
                        (Tickets.reference.ilike(search_term)) |
                        (Tickets.document_client.ilike(search_term))
                    )
                elif field == 'state':
                    base_query = base_query.filter(Tickets.state == value)
                elif field == 'state_not':
                    base_query = base_query.filter(Tickets.state != value)
                elif field == 'city':
                    city_value = value.lower()
                    if city_value in ['medellin', 'medellín']:
                        base_query = base_query.filter(Tickets.city.ilike('%medell%'))
                    elif city_value in ['bogota', 'bogotá']:
                        base_query = base_query.filter(Tickets.city.ilike('%bogot%'))
                    else:
                        base_query = base_query.filter(Tickets.city == value)
    
    pagination_service = PaginationService(base_query, page_size=20)
    return pagination_service.get_paginated_data(page, {})


def get_paginated_technical_service(page=1, filters=None):
    """
    Función específica para servicio técnico con filtros optimizados
    
    Args:
        page: Número de página
        filters: Dict con filtros {'search': str, 'state': str, 'city': str, 'state_not': str}
    """
    from models.tickets import Tickets as TechnicalTickets
    
    # 🎯 QUERY BASE OPTIMIZADO: Solo tickets de servicio técnico (type_of_service="0")
    base_query = TechnicalTickets.query.filter_by(type_of_service="0").order_by(
        TechnicalTickets.get_latest_activity_expression()  # Ordenado por actividad más reciente
    )
    
    # 🔧 SERVICIO DE PAGINACIÓN CON TAMAÑO OPTIMIZADO
    pagination_service = PaginationService(base_query, page_size=20)  # 20 tickets por página
    return pagination_service.get_paginated_data(page, filters)


def get_paginated_warranties(page=1, filters=None):
    """
    Función específica para garantías con filtros optimizados
    
    Args:
        page: Número de página
        filters: Dict con filtros {'search': str, 'state': str, 'city': str, 'state_not': str}
    """
    from models.tickets import Tickets as WarrantyTickets
    
    # 🎯 QUERY BASE OPTIMIZADO: Solo tickets de garantía (type_of_service="2")
    base_query = WarrantyTickets.query.filter_by(type_of_service="2").order_by(
        WarrantyTickets.get_latest_activity_expression()  # Ordenado por actividad más reciente
    )
    
    # 🔧 SERVICIO DE PAGINACIÓN CON TAMAÑO OPTIMIZADO
    pagination_service = PaginationService(base_query, page_size=20)  # 20 tickets por página
    return pagination_service.get_paginated_data(page, filters)


class LazyLoader:
    """
    Carga perezosa para datos que no se necesitan inmediatamente
    Ideal para detalles de tickets que se muestran en modales
    """
    
    @staticmethod
    def load_ticket_details(ticket_id, ticket_type="internal"):
        """Carga detalles completos de un ticket solo cuando se necesitan"""
        try:
            if ticket_type == "internal":
                from models.tickets import Tickets
                ticket = Tickets.query.get(ticket_id)
            else:
                from models.tickets import Tickets as TechnicalTickets
                ticket = TechnicalTickets.query.get(ticket_id)
            
            if not ticket:
                return None
            
            # Cargar relaciones necesarias de manera eficiente
            # Esto se ejecuta solo cuando se abre el modal de detalles
            return {
                'ticket': ticket,
                'problems': ticket.problems,
                'spare_parts': ticket.spare_parts if hasattr(ticket, 'spare_parts') else []
            }
            
        except Exception as e:
            print(f"Error cargando detalles del ticket {ticket_id}: {e}")
            return None
    
    @staticmethod
    def load_ticket_history(ticket_id):
        """Carga historial de cambios de un ticket (solo cuando se necesita)"""
        # Implementar cuando sea necesario 
