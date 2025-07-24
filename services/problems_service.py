"""
Servicio centralizado para manejar problemas del sistema de tickets.
Evita problemas de DetachedInstanceError al asegurar que los objetos estén vinculados a la sesión.
"""
from typing import List, Optional
from models.problems import Problems
from models import db


def get_fresh_problems() -> List[Problems]:
    """
    Obtiene problemas frescos de la base de datos para evitar DetachedInstanceError.
    Esta función asegura que los objetos estén vinculados a la sesión actual.
    
    Returns:
        List[Problems]: Lista de problemas ordenados por nombre
    """
    try:
        # Obtener problemas frescos de la base de datos
        problems = Problems.query.order_by(Problems.name).all()
        
        # Verificar que los objetos estén vinculados a la sesión
        for problem in problems:
            if not db.session.is_active:
                # Si la sesión no está activa, refrescar el objeto
                db.session.refresh(problem)
        
        return problems
    except Exception as e:
        print(f"Error obteniendo problemas frescos: {e}")
        return []


def get_problems_by_ids(problem_ids: List[int]) -> List[Problems]:
    """
    Obtiene problemas específicos por sus IDs, asegurando que estén vinculados a la sesión.
    
    Args:
        problem_ids: Lista de IDs de problemas a obtener
        
    Returns:
        List[Problems]: Lista de problemas encontrados
    """
    try:
        if not problem_ids:
            return []
            
        problems = Problems.query.filter(Problems.id.in_(problem_ids)).all()
        
        # Verificar que los objetos estén vinculados a la sesión
        for problem in problems:
            if not db.session.is_active:
                db.session.refresh(problem)
        
        return problems
    except Exception as e:
        print(f"Error obteniendo problemas por IDs: {e}")
        return []


def get_problem_by_id(problem_id: int) -> Optional[Problems]:
    """
    Obtiene un problema específico por su ID, asegurando que esté vinculado a la sesión.
    
    Args:
        problem_id: ID del problema a obtener
        
    Returns:
        Problems: Problema encontrado o None si no existe
    """
    try:
        problem = Problems.query.get(problem_id)
        
        if problem and not db.session.is_active:
            db.session.refresh(problem)
        
        return problem
    except Exception as e:
        print(f"Error obteniendo problema por ID {problem_id}: {e}")
        return None


def refresh_problems_session(problems: List[Problems]) -> List[Problems]:
    """
    Refresca la sesión de una lista de problemas para evitar DetachedInstanceError.
    
    Args:
        problems: Lista de problemas a refrescar
        
    Returns:
        List[Problems]: Lista de problemas con sesión refrescada
    """
    try:
        refreshed_problems = []
        for problem in problems:
            if problem and not db.session.is_active:
                db.session.refresh(problem)
            refreshed_problems.append(problem)
        return refreshed_problems
    except Exception as e:
        print(f"Error refrescando sesión de problemas: {e}")
        return problems 