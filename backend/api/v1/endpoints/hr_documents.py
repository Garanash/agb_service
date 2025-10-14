"""
API endpoints для HR отдела
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from database import get_db
from models import User
from api.v1.schemas import (
    HRDocumentCreate, HRDocumentResponse
)
from api.v1.dependencies import get_current_user
from services.hr_document_service import get_hr_document_service, HRDocumentService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/verified-contractors", response_model=List[Dict[str, Any]])
async def get_verified_contractors_for_hr(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение проверенных исполнителей для HR отдела"""
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники HR отдела могут просматривать проверенных исполнителей"
        )
    
    hr_service = get_hr_document_service(db)
    verified_contractors = hr_service.get_verified_contractors_for_hr()
    
    result = []
    for contractor in verified_contractors:
        documents = hr_service.get_contractor_documents(contractor.id)
        result.append({
            "contractor_id": contractor.id,
            "name": f"{contractor.first_name} {contractor.last_name}",
            "phone": contractor.phone,
            "email": contractor.email,
            "specializations": contractor.specializations or [],
            "equipment_brands_experience": contractor.equipment_brands_experience or [],
            "work_regions": contractor.work_regions or [],
            "hourly_rate": contractor.hourly_rate,
            "availability_status": contractor.availability_status,
            "documents_count": len(documents),
            "pending_documents": len([d for d in documents if d.document_status == "pending"]),
            "completed_documents": len([d for d in documents if d.document_status == "completed"])
        })
    
    return result

@router.get("/contractor/{contractor_id}/documents", response_model=List[HRDocumentResponse])
async def get_contractor_documents(
    contractor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение документов конкретного исполнителя"""
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники HR отдела могут просматривать документы"
        )
    
    hr_service = get_hr_document_service(db)
    documents = hr_service.get_contractor_documents(contractor_id)
    
    return [HRDocumentResponse.from_orm(doc) for doc in documents]

@router.post("/contractor/{contractor_id}/create-document", response_model=HRDocumentResponse)
async def create_document_request(
    contractor_id: int,
    document_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание заявки на документ"""
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники HR отдела могут создавать документы"
        )
    
    document_type = document_data.get("document_type")
    if not document_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тип документа обязателен"
        )
    
    hr_service = get_hr_document_service(db)
    
    try:
        document = hr_service.create_document_request(
            contractor_id=contractor_id,
            document_type=document_type,
            hr_officer_id=current_user.id
        )
        
        return HRDocumentResponse.from_orm(document)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/document/{document_id}/generate")
async def generate_document(
    document_id: int,
    generation_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Генерация документа"""
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники HR отдела могут генерировать документы"
        )
    
    hr_service = get_hr_document_service(db)
    
    try:
        document = hr_service.generate_document(
            document_id=document_id,
            hr_officer_id=current_user.id,
            document_content=generation_data.get("document_content")
        )
        
        return {
            "message": f"Документ {document_id} сгенерирован",
            "document": HRDocumentResponse.from_orm(document)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/document/{document_id}/complete")
async def complete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Завершение работы с документом"""
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники HR отдела могут завершать документы"
        )
    
    hr_service = get_hr_document_service(db)
    
    try:
        document = hr_service.complete_document(
            document_id=document_id,
            hr_officer_id=current_user.id
        )
        
        return {
            "message": f"Документ {document_id} завершен",
            "document": HRDocumentResponse.from_orm(document)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/document/{document_id}/content")
async def get_document_content(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение содержимого документа"""
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники HR отдела могут просматривать содержимое документов"
        )
    
    hr_service = get_hr_document_service(db)
    
    try:
        content = hr_service.get_document_content(document_id)
        return {"content": content}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/document/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Скачивание документа"""
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники HR отдела могут скачивать документы"
        )
    
    hr_service = get_hr_document_service(db)
    
    try:
        content = hr_service.get_document_content(document_id)
        
        # Получаем информацию о документе для имени файла
        from models import HRDocument
        document = db.query(HRDocument).filter(HRDocument.id == document_id).first()
        
        filename = f"{document.document_type}_{document.contractor_id}.txt"
        
        return Response(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/statistics")
async def get_hr_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики для HR отдела"""
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники HR отдела могут просматривать статистику"
        )
    
    hr_service = get_hr_document_service(db)
    stats = hr_service.get_hr_statistics()
    
    return stats

@router.get("/contractor/{contractor_id}/details")
async def get_contractor_details_for_hr(
    contractor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение детальной информации об исполнителе для HR"""
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники HR отдела могут просматривать детальную информацию"
        )
    
    hr_service = get_hr_document_service(db)
    
    try:
        details = hr_service.get_contractor_detailed_info_for_hr(contractor_id)
        return details
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/document-types")
async def get_available_document_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение доступных типов документов"""
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники HR отдела могут просматривать типы документов"
        )
    
    document_types = [
        {
            "type": "employment_contract",
            "name": "Трудовой договор",
            "description": "Основной трудовой договор для постоянных сотрудников"
        },
        {
            "type": "service_agreement",
            "name": "Договор возмездного оказания услуг",
            "description": "Договор для внештатных исполнителей"
        },
        {
            "type": "nda_agreement",
            "name": "Соглашение о неразглашении",
            "description": "Соглашение о конфиденциальности информации"
        },
        {
            "type": "safety_instruction",
            "name": "Инструкция по технике безопасности",
            "description": "Инструкция по безопасному выполнению работ"
        },
        {
            "type": "equipment_certificate",
            "name": "Сертификат на работу с оборудованием",
            "description": "Сертификат о допуске к работе с техникой"
        }
    ]
    
    return document_types
