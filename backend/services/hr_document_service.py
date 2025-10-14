"""
Сервис для управления HR документами
Управляет процессом создания и обработки документов для исполнителей
"""

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from models import (
    HRDocument, ContractorProfile, User, SecurityVerification
)

logger = logging.getLogger(__name__)

class HRDocumentService:
    """Сервис для управления HR документами"""
    
    def __init__(self, db: Session):
        self.db = db
        self.documents_dir = "uploads/hr_documents"
        os.makedirs(self.documents_dir, exist_ok=True)
    
    def get_verified_contractors_for_hr(self) -> List[ContractorProfile]:
        """Получение проверенных исполнителей для HR"""
        verified_contractors = self.db.query(ContractorProfile).join(SecurityVerification).filter(
            SecurityVerification.verification_status == "approved"
        ).all()
        
        return verified_contractors
    
    def get_contractor_documents(self, contractor_id: int) -> List[HRDocument]:
        """Получение документов конкретного исполнителя"""
        return self.db.query(HRDocument).filter(
            HRDocument.contractor_id == contractor_id
        ).order_by(HRDocument.created_at.desc()).all()
    
    def create_document_request(
        self, 
        contractor_id: int, 
        document_type: str, 
        hr_officer_id: int
    ) -> HRDocument:
        """Создание заявки на документ"""
        
        # Проверяем, что исполнитель существует и проверен
        contractor = self.db.query(ContractorProfile).filter(
            ContractorProfile.id == contractor_id
        ).first()
        
        if not contractor:
            raise ValueError(f"Исполнитель с ID {contractor_id} не найден")
        
        # Проверяем, что исполнитель проверен службой безопасности
        verification = self.db.query(SecurityVerification).filter(
            SecurityVerification.contractor_id == contractor_id,
            SecurityVerification.verification_status == "approved"
        ).first()
        
        if not verification:
            raise ValueError(f"Исполнитель {contractor_id} не прошел проверку службы безопасности")
        
        # Создаем документ
        document = HRDocument(
            contractor_id=contractor_id,
            document_type=document_type,
            document_status="pending",
            generated_by=hr_officer_id
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        logger.info(f"✅ Создана заявка на документ {document_type} для исполнителя {contractor_id}")
        return document
    
    def generate_document(
        self, 
        document_id: int, 
        hr_officer_id: int,
        document_content: Optional[str] = None
    ) -> HRDocument:
        """Генерация документа"""
        
        document = self.db.query(HRDocument).filter(
            HRDocument.id == document_id
        ).first()
        
        if not document:
            raise ValueError(f"Документ с ID {document_id} не найден")
        
        if document.document_status != "pending":
            raise ValueError(f"Документ {document_id} уже обработан")
        
        # Получаем информацию об исполнителе
        contractor = self.db.query(ContractorProfile).filter(
            ContractorProfile.id == document.contractor_id
        ).first()
        
        if not contractor:
            raise ValueError(f"Исполнитель для документа {document_id} не найден")
        
        # Генерируем содержимое документа
        if not document_content:
            document_content = self._generate_document_content(document.document_type, contractor)
        
        # Сохраняем документ в файл
        filename = f"{document.document_type}_{contractor.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.documents_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(document_content)
            
            # Обновляем статус документа
            document.document_status = "generated"
            document.generated_by = hr_officer_id
            document.generated_at = datetime.now(timezone.utc)
            document.document_path = filepath
            
            self.db.commit()
            self.db.refresh(document)
            
            logger.info(f"✅ Документ {document_id} сгенерирован и сохранен: {filepath}")
            return document
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения документа {document_id}: {e}")
            raise ValueError(f"Ошибка сохранения документа: {e}")
    
    def complete_document(self, document_id: int, hr_officer_id: int) -> HRDocument:
        """Завершение работы с документом"""
        
        document = self.db.query(HRDocument).filter(
            HRDocument.id == document_id
        ).first()
        
        if not document:
            raise ValueError(f"Документ с ID {document_id} не найден")
        
        if document.document_status != "generated":
            raise ValueError(f"Документ {document_id} не может быть завершен: статус {document.document_status}")
        
        document.document_status = "completed"
        self.db.commit()
        self.db.refresh(document)
        
        logger.info(f"✅ Документ {document_id} завершен")
        return document
    
    def get_document_content(self, document_id: int) -> str:
        """Получение содержимого документа"""
        
        document = self.db.query(HRDocument).filter(
            HRDocument.id == document_id
        ).first()
        
        if not document:
            raise ValueError(f"Документ с ID {document_id} не найден")
        
        if not document.document_path or not os.path.exists(document.document_path):
            raise ValueError(f"Файл документа {document_id} не найден")
        
        try:
            with open(document.document_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"❌ Ошибка чтения документа {document_id}: {e}")
            raise ValueError(f"Ошибка чтения документа: {e}")
    
    def get_hr_statistics(self) -> Dict[str, Any]:
        """Получение статистики для HR отдела"""
        
        # Общее количество документов
        total_documents = self.db.query(HRDocument).count()
        
        # Документы по статусам
        pending_count = self.db.query(HRDocument).filter(
            HRDocument.document_status == "pending"
        ).count()
        
        generated_count = self.db.query(HRDocument).filter(
            HRDocument.document_status == "generated"
        ).count()
        
        completed_count = self.db.query(HRDocument).filter(
            HRDocument.document_status == "completed"
        ).count()
        
        # Документы за последние 30 дней
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_documents = self.db.query(HRDocument).filter(
            HRDocument.created_at >= thirty_days_ago
        ).count()
        
        # Среднее время обработки документа
        processed_documents = self.db.query(HRDocument).filter(
            and_(
                HRDocument.generated_at.isnot(None),
                HRDocument.created_at.isnot(None)
            )
        ).all()
        
        avg_processing_time = 0
        if processed_documents:
            total_time = sum([
                (doc.generated_at - doc.created_at).total_seconds() / 3600  # в часах
                for doc in processed_documents
                if doc.generated_at and doc.created_at
            ])
            avg_processing_time = total_time / len(processed_documents)
        
        # Статистика по типам документов
        document_types = self.db.query(
            HRDocument.document_type,
            func.count(HRDocument.id).label('count')
        ).group_by(HRDocument.document_type).all()
        
        return {
            "total_documents": total_documents,
            "pending_count": pending_count,
            "generated_count": generated_count,
            "completed_count": completed_count,
            "recent_documents": recent_documents,
            "avg_processing_time_hours": round(avg_processing_time, 1),
            "completion_rate": round(
                (completed_count / total_documents * 100) if total_documents > 0 else 0, 1
            ),
            "document_types": {doc_type: count for doc_type, count in document_types}
        }
    
    def get_contractor_detailed_info_for_hr(self, contractor_id: int) -> Dict[str, Any]:
        """Получение детальной информации об исполнителе для HR"""
        
        contractor = self.db.query(ContractorProfile).filter(
            ContractorProfile.id == contractor_id
        ).first()
        
        if not contractor:
            raise ValueError(f"Исполнитель с ID {contractor_id} не найден")
        
        user = self.db.query(User).filter(User.id == contractor.user_id).first()
        
        # Получаем информацию о проверке безопасности
        verification = self.db.query(SecurityVerification).filter(
            SecurityVerification.contractor_id == contractor_id
        ).first()
        
        # Получаем документы исполнителя
        documents = self.get_contractor_documents(contractor_id)
        
        return {
            "contractor_id": contractor.id,
            "user_id": contractor.user_id,
            "personal_info": {
                "first_name": contractor.first_name,
                "last_name": contractor.last_name,
                "patronymic": contractor.patronymic,
                "phone": contractor.phone,
                "email": contractor.email,
                "telegram_username": contractor.telegram_username
            },
            "professional_info": {
                "specializations": contractor.specializations or [],
                "equipment_brands_experience": contractor.equipment_brands_experience or [],
                "certifications": contractor.certifications or [],
                "work_regions": contractor.work_regions or [],
                "hourly_rate": contractor.hourly_rate,
                "availability_status": contractor.availability_status
            },
            "security_verification": {
                "status": verification.verification_status if verification else "not_verified",
                "verified_at": verification.checked_at.isoformat() if verification and verification.checked_at else None,
                "verified_by": verification.checked_by if verification else None
            },
            "hr_documents": [
                {
                    "id": doc.id,
                    "document_type": doc.document_type,
                    "document_status": doc.document_status,
                    "created_at": doc.created_at.isoformat(),
                    "generated_at": doc.generated_at.isoformat() if doc.generated_at else None,
                    "generated_by": doc.generated_by
                }
                for doc in documents
            ],
            "activity_info": {
                "registration_date": user.created_at.isoformat() if user else None,
                "is_active": user.is_active if user else False
            }
        }
    
    def _generate_document_content(self, document_type: str, contractor: ContractorProfile) -> str:
        """Генерация содержимого документа"""
        
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        if document_type == "employment_contract":
            return f"""
ТРУДОВОЙ ДОГОВОР № {contractor.id}

г. Москва                                    {current_date}

ООО "Алмазгеобур", именуемое в дальнейшем "Работодатель", в лице генерального директора, действующего на основании Устава, с одной стороны, и гражданин(ка) {contractor.first_name} {contractor.last_name} {contractor.patronymic or ''}, именуемый(ая) в дальнейшем "Работник", с другой стороны, заключили настоящий трудовой договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА
1.1. Работник принимается на работу в качестве сервисного инженера по обслуживанию горнодобывающей техники.
1.2. Место работы: {', '.join(contractor.work_regions or ['г. Москва'])}.
1.3. Дата начала работы: {current_date}.

2. ОБЯЗАННОСТИ РАБОТНИКА
2.1. Работник обязуется выполнять следующие виды работ:
- Техническое обслуживание и ремонт горнодобывающей техники;
- Диагностика неисправностей оборудования;
- Выполнение работ по специализациям: {', '.join(contractor.specializations or ['общее обслуживание'])}.

3. ОПЛАТА ТРУДА
3.1. Размер почасовой оплаты составляет {contractor.hourly_rate or 1000} рублей за час работы.
3.2. Оплата производится ежемесячно до 10 числа следующего месяца.

4. РЕЖИМ РАБОТЫ
4.1. Работник работает по гибкому графику в соответствии с производственной необходимостью.
4.2. Работник может быть привлечен к работе в выходные и праздничные дни с согласованием.

5. КОНТАКТНАЯ ИНФОРМАЦИЯ
5.1. Телефон: {contractor.phone}
5.2. Email: {contractor.email}
5.3. Telegram: {contractor.telegram_username or 'не указан'}

Настоящий договор составлен в двух экземплярах, имеющих одинаковую юридическую силу.

Работодатель: _________________     Работник: _________________
                (подпись)                        (подпись)
"""
        
        elif document_type == "service_agreement":
            return f"""
ДОГОВОР ВОЗМЕЗДНОГО ОКАЗАНИЯ УСЛУГ № {contractor.id}

г. Москва                                    {current_date}

ООО "Алмазгеобур", именуемое в дальнейшем "Заказчик", в лице генерального директора, действующего на основании Устава, с одной стороны, и гражданин(ка) {contractor.first_name} {contractor.last_name} {contractor.patronymic or ''}, именуемый(ая) в дальнейшем "Исполнитель", с другой стороны, заключили настоящий договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА
1.1. Исполнитель обязуется оказать услуги по техническому обслуживанию и ремонту горнодобывающей техники, а Заказчик обязуется принять и оплатить эти услуги.
1.2. Виды оказываемых услуг:
- Техническое обслуживание оборудования;
- Ремонт и диагностика неисправностей;
- Консультационные услуги по эксплуатации техники.

2. СПЕЦИАЛИЗАЦИИ ИСПОЛНИТЕЛЯ
2.1. Исполнитель имеет опыт работы со следующими брендами: {', '.join(contractor.equipment_brands_experience or ['различные бренды'])}.
2.2. Специализации: {', '.join(contractor.specializations or ['общее обслуживание'])}.

3. СТОИМОСТЬ УСЛУГ И ПОРЯДОК РАСЧЕТОВ
3.1. Стоимость услуг составляет {contractor.hourly_rate or 1000} рублей за час работы.
3.2. Оплата производится по факту выполнения работ в течение 5 банковских дней.

4. ОТВЕТСТВЕННОСТЬ СТОРОН
4.1. Исполнитель несет ответственность за качество оказываемых услуг.
4.2. Заказчик обязуется обеспечить безопасные условия труда.

5. КОНТАКТНЫЕ ДАННЫЕ
5.1. Исполнитель: {contractor.phone}, {contractor.email}
5.2. Заказчик: ООО "Алмазгеобур"

Договор вступает в силу с момента подписания и действует до полного выполнения обязательств.

Заказчик: _________________     Исполнитель: _________________
            (подпись)                        (подпись)
"""
        
        elif document_type == "nda_agreement":
            return f"""
СОГЛАШЕНИЕ О НЕРАЗГЛАШЕНИИ КОНФИДЕНЦИАЛЬНОЙ ИНФОРМАЦИИ

г. Москва                                    {current_date}

ООО "Алмазгеобур", именуемое в дальнейшем "Раскрывающая сторона", и гражданин(ка) {contractor.first_name} {contractor.last_name} {contractor.patronymic or ''}, именуемый(ая) в дальнейшем "Получающая сторона", заключили настоящее соглашение о нижеследующем:

1. ОПРЕДЕЛЕНИЕ КОНФИДЕНЦИАЛЬНОЙ ИНФОРМАЦИИ
1.1. Под конфиденциальной информацией понимается любая техническая, коммерческая, финансовая информация, включая:
- Технические характеристики оборудования;
- Методы и технологии обслуживания;
- Коммерческие условия сотрудничества;
- Данные о заказчиках и их оборудовании.

2. ОБЯЗАТЕЛЬСТВА ПОЛУЧАЮЩЕЙ СТОРОНЫ
2.1. Получающая сторона обязуется:
- Не разглашать конфиденциальную информацию третьим лицам;
- Использовать информацию только в целях выполнения работ;
- Принимать меры по защите информации.

3. СРОК ДЕЙСТВИЯ
3.1. Настоящее соглашение действует в течение 5 лет с момента подписания.

4. ОТВЕТСТВЕННОСТЬ
4.1. За нарушение обязательств по неразглашению Получающая сторона несет ответственность в соответствии с действующим законодательством.

Раскрывающая сторона: _________________     Получающая сторона: _________________
                        (подпись)                            (подпись)
"""
        
        else:
            return f"""
ДОКУМЕНТ: {document_type.upper()}

Исполнитель: {contractor.first_name} {contractor.last_name} {contractor.patronymic or ''}
Дата создания: {current_date}
Телефон: {contractor.phone}
Email: {contractor.email}

Специализации: {', '.join(contractor.specializations or ['не указаны'])}
Опыт с брендами: {', '.join(contractor.equipment_brands_experience or ['не указан'])}
Регионы работы: {', '.join(contractor.work_regions or ['не указаны'])}

Почасовая ставка: {contractor.hourly_rate or 'не указана'} руб/час

Документ создан автоматически системой HR отдела ООО "Алмазгеобур".
"""

def get_hr_document_service(db: Session) -> HRDocumentService:
    """Получение экземпляра сервиса HR документов"""
    return HRDocumentService(db)
