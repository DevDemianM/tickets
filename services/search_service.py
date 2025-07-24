"""
Servicio de búsqueda unificado para el sistema de tickets
Permite búsqueda completa sin limitaciones de paginado
Busca por: id, técnico, referencia, prioridad, documento
"""

from sqlalchemy import or_, and_, func
from models.tickets import Tickets
from models import db
import re


class SearchService:
    """
    Servicio de búsqueda unificado para todos los módulos de tickets.
    Permite búsqueda completa sin limitaciones de paginado.
    """
    
    @staticmethod
    def search_tickets(search_term, ticket_type=None, limit=None):
        """
        Busca tickets por múltiples criterios sin limitaciones de paginado.
        
        Args:
            search_term (str): Término de búsqueda
            ticket_type (str, optional): Tipo de ticket ("0"=ST, "1"=RI, "2"=GA)
            limit (int, optional): Límite de resultados (None = sin límite)
            
        Returns:
            list: Lista de tickets que coinciden con la búsqueda
        """
        if not search_term or not search_term.strip():
            return []
            
        # Limpiar y preparar el término de búsqueda
        clean_term = search_term.strip()
        search_pattern = f"%{clean_term}%"
        
        # Query base
        query = Tickets.query
        
        # Filtrar por tipo de ticket si se especifica
        if ticket_type is not None:
            query = query.filter(Tickets.type_of_service == ticket_type)
        
        # Aplicar condiciones de búsqueda en múltiples campos
        search_conditions = or_(
            # Búsqueda por ID del ticket
            func.cast(Tickets.id_ticket, db.String).ilike(search_pattern),
            
            # Búsqueda por técnico (nombre)
            Tickets.technical_name.ilike(search_pattern),
            
            # Búsqueda por referencia del producto
            Tickets.reference.ilike(search_pattern),
            
            # Búsqueda por prioridad
            Tickets.priority.ilike(search_pattern),
            
            # Búsqueda por documento del cliente
            Tickets.document_client.ilike(search_pattern),
            
            # Búsquedas adicionales útiles
            Tickets.IMEI.ilike(search_pattern),
            Tickets.product_code.ilike(search_pattern),
            Tickets.city.ilike(search_pattern),
            Tickets.state.ilike(search_pattern)
        )
        
        # Aplicar condiciones de búsqueda
        query = query.filter(search_conditions)
        
        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(Tickets.get_latest_activity_expression())
        
        # Aplicar límite si se especifica
        if limit:
            query = query.limit(limit)
            
        try:
            results = query.all()
            return results
        except Exception as e:
            print(f"Error en búsqueda de tickets: {e}")
            return []
    
    @staticmethod
    def search_technical_service(search_term, limit=None):
        """
        Búsqueda específica para Servicio Técnico (ST).
        
        Args:
            search_term (str): Término de búsqueda
            limit (int, optional): Límite de resultados
            
        Returns:
            list: Lista de tickets de servicio técnico
        """
        return SearchService.search_tickets(search_term, ticket_type="0", limit=limit)
    
    @staticmethod
    def search_internal_repair(search_term, limit=None):
        """
        Búsqueda específica para Reparación Interna (RI).
        
        Args:
            search_term (str): Término de búsqueda
            limit (int, optional): Límite de resultados
            
        Returns:
            list: Lista de tickets de reparación interna
        """
        return SearchService.search_tickets(search_term, ticket_type="1", limit=limit)
    
    @staticmethod
    def search_warranty(search_term, limit=None):
        """
        Búsqueda específica para Garantía (GA).
        
        Args:
            search_term (str): Término de búsqueda
            limit (int, optional): Límite de resultados
            
        Returns:
            list: Lista de tickets de garantía
        """
        return SearchService.search_tickets(search_term, ticket_type="2", limit=limit)
    
    @staticmethod
    def search_technician_tickets(search_term, technician_document, limit=None):
        """
        Búsqueda específica para Vista del Técnico.
        Solo busca en tickets asignados al técnico especificado.
        
        Args:
            search_term (str): Término de búsqueda
            technician_document (str): Documento del técnico
            limit (int, optional): Límite de resultados
            
        Returns:
            list: Lista de tickets asignados al técnico
        """
        if not search_term or not search_term.strip() or not technician_document:
            return []
            
        # Normalizar documento del técnico
        normalized_doc = ''.join(c for c in technician_document if c.isalnum())
        
        # Buscar todos los tickets (sin filtro de tipo)
        all_tickets = SearchService.search_tickets(search_term, ticket_type=None, limit=None)
        
        # Filtrar solo los tickets asignados al técnico
        technician_tickets = []
        for ticket in all_tickets:
            if ticket.technical_document:
                normalized_ticket_doc = ''.join(c for c in ticket.technical_document if c.isalnum())
                if normalized_ticket_doc == normalized_doc and ticket.state != 'Terminado':
                    technician_tickets.append(ticket)
        
        # Aplicar límite si se especifica
        if limit and len(technician_tickets) > limit:
            technician_tickets = technician_tickets[:limit]
            
        return technician_tickets
    
    @staticmethod
    def get_search_summary(search_term, ticket_type=None):
        """
        Obtiene un resumen de los resultados de búsqueda.
        
        Args:
            search_term (str): Término de búsqueda
            ticket_type (str, optional): Tipo de ticket
            
        Returns:
            dict: Resumen con conteos por estado, prioridad, etc.
        """
        tickets = SearchService.search_tickets(search_term, ticket_type)
        
        if not tickets:
            return {
                'total': 0,
                'by_state': {},
                'by_priority': {},
                'by_city': {}
            }
        
        # Agrupar por estado
        by_state = {}
        by_priority = {}
        by_city = {}
        
        for ticket in tickets:
            # Contar por estado
            state = ticket.state or 'Sin estado'
            by_state[state] = by_state.get(state, 0) + 1
            
            # Contar por prioridad
            priority = ticket.priority or 'Sin prioridad'
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # Contar por ciudad
            city = ticket.city or 'Sin ciudad'
            by_city[city] = by_city.get(city, 0) + 1
        
        return {
            'total': len(tickets),
            'by_state': by_state,
            'by_priority': by_priority,
            'by_city': by_city
        }
    
    @staticmethod
    def validate_search_term(search_term):
        """
        Valida el término de búsqueda.
        
        Args:
            search_term (str): Término a validar
            
        Returns:
            dict: Resultado de validación
        """
        if not search_term:
            return {
                'is_valid': False,
                'message': 'El término de búsqueda es requerido'
            }
        
        clean_term = search_term.strip()
        
        if len(clean_term) < 1:
            return {
                'is_valid': False,
                'message': 'El término de búsqueda debe tener al menos 1 caracter'
            }
        
        if len(clean_term) > 100:
            return {
                'is_valid': False,
                'message': 'El término de búsqueda no puede tener más de 100 caracteres'
            }
        
        # Verificar caracteres no permitidos (opcional)
        if re.search(r'[<>"\';]', clean_term):
            return {
                'is_valid': False,
                'message': 'El término de búsqueda contiene caracteres no permitidos'
            }
        
        return {
            'is_valid': True,
            'message': 'Término de búsqueda válido',
            'clean_term': clean_term
        } 