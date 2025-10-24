// Типы для API Agregator Service

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  role: UserRole;
  is_active: boolean;
  is_password_changed: boolean;
  email_verified: boolean;
  avatar_url?: string;
  phone?: string;
  position?: string;
  created_at: string;
  updated_at?: string;
}

export enum UserRole {
  ADMIN = 'admin',
  CUSTOMER = 'customer',
  CONTRACTOR = 'contractor',
  SERVICE_ENGINEER = 'service_engineer',
  MANAGER = 'manager',
  SECURITY = 'security',
  HR = 'hr',
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  phone?: string;
  position?: string;
  role: UserRole;
}

// Расширенные схемы для регистрации
export interface CustomerRegistrationRequest {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  phone?: string;
  position?: string;
  company_name: string;
  region: string;
  inn_or_ogrn: string;
  // Новые поля для горнодобывающей техники
  equipment_brands?: string[];
  equipment_types?: string[];
  mining_operations?: string[];
  service_history?: string;
}

export interface ContractorRegistrationRequest {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  phone?: string;
  position?: string;
  // Новые поля для специализации
  specializations?: string[];
  equipment_brands_experience?: string[];
  certifications?: string[];
  work_regions?: string[];
  hourly_rate?: number;
  telegram_username?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RepairRequest {
  id: number;
  title: string;
  description: string;
  urgency?: string;
  preferred_date?: string;
  address?: string;
  city?: string;
  region?: string;
  equipment_type?: string;
  equipment_brand?: string;
  equipment_model?: string;
  problem_description?: string;
  priority?: string;
  manager_comment?: string;
  clarification_details?: string;
  estimated_cost?: number;
  final_price?: number;
  scheduled_date?: string;
  status: RequestStatus;
  customer_id: number;
  service_engineer_id?: number;
  assigned_contractor_id?: number;
  manager_id?: number;
  created_at: string;
  updated_at?: string;
  processed_at?: string;
  assigned_at?: string;
  sent_to_bot_at?: string;
  customer?: CustomerProfile;
  service_engineer?: User;
  assigned_contractor?: User;
  manager?: User;
  responses?: ContractorResponse[];
}

export enum RequestStatus {
  NEW = 'new',
  MANAGER_REVIEW = 'manager_review',
  CLARIFICATION = 'clarification',
  SENT_TO_CONTRACTORS = 'sent_to_contractors',
  CONTRACTOR_RESPONSES = 'contractor_responses',
  ASSIGNED = 'assigned',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

export interface RepairRequestCreate {
  title: string;
  description: string;
  urgency?: string;
  preferred_date?: string;
  address?: string;
  city?: string;
  region?: string;
}

export interface RepairRequestUpdate {
  title?: string;
  description?: string;
  urgency?: string;
  preferred_date?: string;
  address?: string;
  city?: string;
  region?: string;
  equipment_type?: string;
  equipment_brand?: string;
  equipment_model?: string;
  problem_description?: string;
  estimated_cost?: number;
  manager_comment?: string;
  final_price?: number;
  status?: RequestStatus;
}

export interface CustomerProfile {
  id: number;
  user_id: number;
  company_name: string;
  contact_person: string;
  phone: string;
  email: string;
  address?: string;
  inn?: string;
  kpp?: string;
  ogrn?: string;
  created_at: string;
  updated_at?: string;
}

export interface CustomerProfileCreate {
  company_name: string;
  contact_person: string;
  phone: string;
  email: string;
  address?: string;
  inn?: string;
  kpp?: string;
  ogrn?: string;
}

export interface CustomerProfile {
  id: number;
  user_id: number;
  company_name: string;
  contact_person: string;
  phone: string;
  email: string;
  address?: string;
  inn?: string;
  kpp?: string;
  ogrn?: string;
  equipment_brands?: string[];
  equipment_types?: string[];
  mining_operations?: string[];
  service_history?: string;
  created_at: string;
  updated_at?: string;
}

export interface CustomerProfileCreate {
  company_name: string;
  contact_person: string;
  phone: string;
  email: string;
  address?: string;
  inn?: string;
  kpp?: string;
  ogrn?: string;
  equipment_brands?: string[];
  equipment_types?: string[];
  mining_operations?: string[];
  service_history?: string;
}

export interface ContractorProfile {
  id: number;
  user_id: number;
  last_name?: string;
  first_name?: string;
  patronymic?: string;
  phone?: string;
  email?: string;
  professional_info?: any[];
  education?: any[];
  bank_name?: string;
  bank_account?: string;
  bank_bik?: string;
  telegram_username?: string;
  website?: string;
  general_description?: string;
  profile_photo_path?: string;
  portfolio_files?: string[];
  document_files?: string[];
  created_at: string;
  updated_at?: string;
}

export interface ContractorProfileCreate {
  last_name?: string;
  first_name?: string;
  patronymic?: string;
  phone?: string;
  email?: string;
  professional_info?: any[];
  education?: any[];
  bank_name?: string;
  bank_account?: string;
  bank_bik?: string;
  telegram_username?: string;
  website?: string;
  general_description?: string;
}

export interface ContractorResponse {
  id: number;
  request_id: number;
  contractor_id: number;
  proposed_price?: number;
  estimated_time?: string;
  comment?: string;
  is_accepted: boolean;
  created_at: string;
  updated_at?: string;
  contractor?: ContractorProfile;
}

export interface ContractorResponseCreate {
  proposed_price?: number;
  estimated_time?: string;
  comment?: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Новые интерфейсы для системы безопасности и HR
export interface SecurityVerification {
  id: number;
  contractor_id: number;
  verification_status: 'pending' | 'approved' | 'rejected';
  verification_notes?: string;
  checked_by?: number;
  checked_at?: string;
  created_at: string;
  updated_at?: string;
  contractor?: ContractorProfile;
  security_officer?: User;
}

export interface SecurityVerificationCreate {
  contractor_id: number;
  verification_status: 'pending' | 'approved' | 'rejected';
  verification_notes?: string;
}

export interface HRDocument {
  id: number;
  contractor_id: number;
  document_type: string;
  document_status: 'pending' | 'generated' | 'completed';
  generated_by?: number;
  generated_at?: string;
  document_path?: string;
  created_at: string;
  updated_at?: string;
  contractor?: ContractorProfile;
  hr_officer?: User;
}

export interface HRDocumentCreate {
  contractor_id: number;
  document_type: string;
}

// Расширенные интерфейсы для профилей
export interface CustomerProfileExtended extends CustomerProfile {
  equipment_brands?: string[];
  equipment_types?: string[];
  mining_operations?: string[];
  service_history?: string;
}

export interface ContractorProfileExtended extends ContractorProfile {
  specializations?: string[];
  equipment_brands_experience?: string[];
  certifications?: string[];
  work_regions?: string[];
  hourly_rate?: number;
  availability_status?: string;
}
