from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import RepairRequest, CustomerProfile, User, ContractorResponse
from ..schemas import (
    RepairRequestCreate, 
    RepairRequestUpdate, 
    RepairRequestResponse,
    ContractorResponseCreate,
    ContractorResponseResponse,
    RequestStatus
)
from ..dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=RepairRequestResponse)
def create_repair_request(
    request_data: RepairRequestCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание новой заявки на ремонт"""
    # Проверяем, что пользователь имеет профиль заказчика
    customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Профиль заказчика не найден. Создайте профиль заказчика."
        )
    
    # Создаем заявку
    db_request = RepairRequest(
        customer_id=customer_profile.id,
        title=request_data.title,
        description=request_data.description,
        urgency=request_data.urgency,
        preferred_date=request_data.preferred_date,
        address=request_data.address,
        city=request_data.city,
        region=request_data.region,
        status=RequestStatus.NEW
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Здесь можно добавить отправку уведомлений в фоне
    # background_tasks.add_task(send_notifications, db_request.id)
    
    return RepairRequestResponse.model_validate(db_request)

@router.get("/", response_model=List[RepairRequestResponse])
def get_repair_requests(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Получение списка заявок на ремонт"""
    try:
        # Базовый запрос
        query = """
            SELECT r.id, r.customer_id, r.title, r.description, r.urgency, r.preferred_date,
                   r.address, r.city, r.region, r.equipment_type, r.equipment_brand,
                   r.equipment_model, r.problem_description, r.estimated_cost,
                   r.manager_comment, r.final_price, r.sent_to_bot_at, r.status,
                   r.service_engineer_id, r.assigned_contractor_id, r.created_at,
                   r.updated_at, r.processed_at, r.assigned_at
            FROM repair_requests r
        """
        params = []
        
        # Фильтрация по роли пользователя
        if current_user.role == "customer":
            # Заказчик видит только свои заявки
            customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
            if customer_profile:
                query += " WHERE r.customer_id = %s"
                params.append(customer_profile.id)
        elif current_user.role == "contractor":
            # Исполнитель видит заявки, на которые он откликнулся или которые ему назначены
            query += " WHERE (r.assigned_contractor_id = %s OR r.id IN (SELECT request_id FROM contractor_responses WHERE contractor_id = (SELECT id FROM contractor_profiles WHERE user_id = %s)))"
            params.extend([current_user.id, current_user.id])
        elif current_user.role == "service_engineer":
            # Сервисный инженер видит все заявки
            pass
        elif current_user.role == "admin":
            # Администратор видит все заявки
            pass
        
        # Фильтрация по статусу
        if status_filter:
            if params:
                query += " AND r.status = %s"
            else:
                query += " WHERE r.status = %s"
            params.append(status_filter)
        
        # Сортировка и пагинация
        query += " ORDER BY r.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, skip])
        
        result = db.execute(text(query), params).fetchall()
        
        requests_list = []
        for row in result:
            request_dict = {
                "id": row[0],
                "customer_id": row[1],
                "title": row[2],
                "description": row[3],
                "urgency": row[4],
                "preferred_date": row[5].isoformat() if row[5] else None,
                "address": row[6],
                "city": row[7],
                "region": row[8],
                "equipment_type": row[9],
                "equipment_brand": row[10],
                "equipment_model": row[11],
                "problem_description": row[12],
                "estimated_cost": row[13],
                "manager_comment": row[14],
                "final_price": row[15],
                "sent_to_bot_at": row[16].isoformat() if row[16] else None,
                "status": row[17],
                "service_engineer_id": row[18],
                "assigned_contractor_id": row[19],
                "created_at": row[20].isoformat() if row[20] else None,
                "updated_at": row[21].isoformat() if row[21] else None,
                "processed_at": row[22].isoformat() if row[22] else None,
                "assigned_at": row[23].isoformat() if row[23] else None
            }
            requests_list.append(request_dict)
        
        return requests_list
    except Exception as e:
        print(f"Ошибка в get_repair_requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении заявок: {str(e)}"
        )

@router.get("/{request_id}", response_model=RepairRequestResponse)
def get_repair_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение конкретной заявки на ремонт"""
    try:
        # Получаем заявку
        query = """
            SELECT r.id, r.customer_id, r.title, r.description, r.urgency, r.preferred_date,
                   r.address, r.city, r.region, r.equipment_type, r.equipment_brand,
                   r.equipment_model, r.problem_description, r.estimated_cost,
                   r.manager_comment, r.final_price, r.sent_to_bot_at, r.status,
                   r.service_engineer_id, r.assigned_contractor_id, r.created_at,
                   r.updated_at, r.processed_at, r.assigned_at
            FROM repair_requests r
            WHERE r.id = %s
        """
        
        result = db.execute(text(query), [request_id]).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заявка не найдена"
            )
        
        # Проверяем права доступа
        if current_user.role == "customer":
            customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
            if not customer_profile or result[1] != customer_profile.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет доступа к этой заявке"
                )
        
        request_dict = {
            "id": result[0],
            "customer_id": result[1],
            "title": result[2],
            "description": result[3],
            "urgency": result[4],
            "preferred_date": result[5].isoformat() if result[5] else None,
            "address": result[6],
            "city": result[7],
            "region": result[8],
            "equipment_type": result[9],
            "equipment_brand": result[10],
            "equipment_model": result[11],
            "problem_description": result[12],
            "estimated_cost": result[13],
            "manager_comment": result[14],
            "final_price": result[15],
            "sent_to_bot_at": result[16].isoformat() if result[16] else None,
            "status": result[17],
            "service_engineer_id": result[18],
            "assigned_contractor_id": result[19],
            "created_at": result[20].isoformat() if result[20] else None,
            "updated_at": result[21].isoformat() if result[21] else None,
            "processed_at": result[22].isoformat() if result[22] else None,
            "assigned_at": result[23].isoformat() if result[23] else None
        }
        
        return request_dict
    except Exception as e:
        print(f"Ошибка в get_repair_request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении заявки: {str(e)}"
        )

@router.put("/{request_id}", response_model=RepairRequestResponse)
def update_repair_request(
    request_id: int,
    request_data: RepairRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление заявки на ремонт"""
    try:
        # Проверяем права доступа
        if current_user.role not in ["service_engineer", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для обновления заявки"
            )
        
        # Получаем заявку
        query = "SELECT id FROM repair_requests WHERE id = %s"
        result = db.execute(text(query), [request_id]).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заявка не найдена"
            )
        
        # Строим запрос обновления
        update_fields = []
        params = []
        
        if request_data.title is not None:
            update_fields.append("title = %s")
            params.append(request_data.title)
        
        if request_data.description is not None:
            update_fields.append("description = %s")
            params.append(request_data.description)
        
        if request_data.urgency is not None:
            update_fields.append("urgency = %s")
            params.append(request_data.urgency)
        
        if request_data.preferred_date is not None:
            update_fields.append("preferred_date = %s")
            params.append(request_data.preferred_date)
        
        if request_data.address is not None:
            update_fields.append("address = %s")
            params.append(request_data.address)
        
        if request_data.city is not None:
            update_fields.append("city = %s")
            params.append(request_data.city)
        
        if request_data.region is not None:
            update_fields.append("region = %s")
            params.append(request_data.region)
        
        if request_data.equipment_type is not None:
            update_fields.append("equipment_type = %s")
            params.append(request_data.equipment_type)
        
        if request_data.equipment_brand is not None:
            update_fields.append("equipment_brand = %s")
            params.append(request_data.equipment_brand)
        
        if request_data.equipment_model is not None:
            update_fields.append("equipment_model = %s")
            params.append(request_data.equipment_model)
        
        if request_data.problem_description is not None:
            update_fields.append("problem_description = %s")
            params.append(request_data.problem_description)
        
        if request_data.estimated_cost is not None:
            update_fields.append("estimated_cost = %s")
            params.append(request_data.estimated_cost)
        
        if request_data.manager_comment is not None:
            update_fields.append("manager_comment = %s")
            params.append(request_data.manager_comment)
        
        if request_data.final_price is not None:
            update_fields.append("final_price = %s")
            params.append(request_data.final_price)
        
        if request_data.status is not None:
            update_fields.append("status = %s")
            params.append(request_data.status.value)
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет данных для обновления"
            )
        
        update_query = f"""
            UPDATE repair_requests 
            SET {', '.join(update_fields)}, updated_at = %s
            WHERE id = %s
        """
        
        params.extend([datetime.now(), request_id])
        db.execute(text(update_query), params)
        db.commit()
        
        # Возвращаем обновленную заявку
        return get_repair_request(request_id, current_user, db)
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка в update_repair_request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении заявки: {str(e)}"
        )

@router.post("/{request_id}/responses", response_model=ContractorResponseResponse)
def create_contractor_response(
    request_id: int,
    response_data: ContractorResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание отклика исполнителя на заявку"""
    try:
        # Проверяем, что пользователь имеет профиль исполнителя
        contractor_profile = db.query(ContractorProfile).filter(ContractorProfile.user_id == current_user.id).first()
        
        if not contractor_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Профиль исполнителя не найден"
            )
        
        # Проверяем, что заявка существует
        request_query = "SELECT id FROM repair_requests WHERE id = %s"
        request_result = db.execute(text(request_query), [request_id]).fetchone()
        
        if not request_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заявка не найдена"
            )
        
        # Проверяем, что исполнитель еще не откликался на эту заявку
        existing_response_query = """
            SELECT id FROM contractor_responses 
            WHERE request_id = %s AND contractor_id = %s
        """
        existing_response = db.execute(text(existing_response_query), [request_id, contractor_profile.id]).fetchone()
        
        if existing_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы уже откликались на эту заявку"
            )
        
        # Создаем отклик
        db_response = ContractorResponse(
            request_id=request_id,
            contractor_id=contractor_profile.id,
            proposed_price=response_data.proposed_price,
            estimated_time=response_data.estimated_time,
            comment=response_data.comment,
            is_accepted=False
        )
        
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        
        return ContractorResponseResponse.model_validate(db_response)
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка в create_contractor_response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании отклика: {str(e)}"
        )
