import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { config } from '../config';
import {
  LoginRequest,
  LoginResponse,
  User,
  UserCreate,
  CustomerRegistrationRequest,
  ContractorRegistrationRequest,
  RepairRequest,
  RepairRequestCreate,
  RepairRequestUpdate,
  CustomerProfile,
  CustomerProfileCreate,
  ContractorProfile,
  ContractorProfileCreate,
  ContractorResponse,
  ContractorResponseCreate,
  PaginatedResponse,
} from '../types/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: config.apiUrl,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Добавляем токен к каждому запросу
    this.api.interceptors.request.use(config => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Обрабатываем ошибки авторизации
    this.api.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Аутентификация
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.api.post(
      '/api/v1/auth/login',
      credentials,
    );
    return response.data;
  }

  async register(userData: UserCreate): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post(
      '/api/v1/auth/register',
      userData,
    );
    return response.data;
  }

  async registerCustomer(
    customerData: CustomerRegistrationRequest,
  ): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post(
      '/api/v1/auth/register-customer',
      customerData,
    );
    return response.data;
  }

  async registerContractor(
    contractorData: ContractorRegistrationRequest,
  ): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post(
      '/api/v1/auth/register-contractor',
      contractorData,
    );
    return response.data;
  }

  // Упрощенная регистрация
  async registerSimple(registrationData: {
    username: string;
    email: string;
    password: string;
    confirmPassword: string;
    role: 'contractor' | 'customer';
  }): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post(
      '/api/v1/auth/register-simple',
      registrationData,
    );
    return response.data;
  }

  async verifyEmail(token: string): Promise<any> {
    const response = await this.api.post('/api/v1/auth/verify-email', { token });
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/api/v1/auth/me');
    return response.data;
  }

  // Заявки на ремонт
  async getRepairRequests(
    page: number = 1,
    size: number = 10,
  ): Promise<PaginatedResponse<RepairRequest>> {
    const response: AxiosResponse<PaginatedResponse<RepairRequest>> =
      await this.api.get(`/api/v1/repair-requests/?page=${page}&size=${size}`);
    return response.data;
  }

  // Workflow методы
  async getWorkflowRequests(): Promise<RepairRequest[]> {
    const response: AxiosResponse<RepairRequest[]> =
      await this.api.get('/api/v1/workflow/');
    return response.data;
  }

  async getAvailableRequests(): Promise<RepairRequest[]> {
    const response: AxiosResponse<RepairRequest[]> = await this.api.get(
      '/api/v1/workflow/available',
    );
    return response.data;
  }

  async assignToManager(requestId: number, managerId: number): Promise<any> {
    const response = await this.api.post(
      `/api/v1/workflow/${requestId}/assign-manager?manager_id=${managerId}`,
    );
    return response.data;
  }

  async addClarification(
    requestId: number,
    clarificationData: any,
  ): Promise<any> {
    const response = await this.api.post(
      `/api/v1/workflow/${requestId}/clarify`,
      clarificationData,
    );
    return response.data;
  }

  async sendToContractors(requestId: number): Promise<any> {
    const response = await this.api.post(
      `/api/v1/workflow/${requestId}/send-to-contractors`,
    );
    return response.data;
  }

  async assignContractor(requestId: number, contractorData: any): Promise<any> {
    const response = await this.api.post(
      `/api/v1/workflow/${requestId}/assign-contractor`,
      contractorData,
    );
    return response.data;
  }

  async startWork(requestId: number): Promise<any> {
    const response = await this.api.post(
      `/api/v1/workflow/${requestId}/start-work`,
    );
    return response.data;
  }

  async completeWork(requestId: number, completionData: any): Promise<any> {
    const response = await this.api.post(
      `/api/v1/workflow/${requestId}/complete`,
      completionData,
    );
    return response.data;
  }

  async cancelRequest(requestId: number, cancellationData: any): Promise<any> {
    const response = await this.api.post(
      `/api/v1/workflow/${requestId}/cancel`,
      cancellationData,
    );
    return response.data;
  }

  async createWorkflowRequest(requestData: any): Promise<any> {
    const response = await this.api.post('/api/v1/workflow/', requestData);
    return response.data;
  }

  // Manager Dashboard методы
  async getManagerStats(): Promise<any> {
    const response = await this.api.get('/api/v1/manager/stats');
    return response.data;
  }

  async getCalendarEvents(startDate: string, endDate: string): Promise<any[]> {
    const response = await this.api.get(
      `/api/v1/manager/calendar-events?start_date=${startDate}&end_date=${endDate}`,
    );
    return response.data;
  }

  async getContractorWorkload(): Promise<any[]> {
    const response = await this.api.get('/api/v1/manager/contractor-workload');
    return response.data;
  }

  async getRecentActivity(limit: number = 10): Promise<any[]> {
    const response = await this.api.get(
      `/api/v1/manager/recent-activity?limit=${limit}`,
    );
    return response.data;
  }

  async getUpcomingDeadlines(): Promise<any[]> {
    const response = await this.api.get('/api/v1/manager/upcoming-deadlines');
    return response.data;
  }

  async scheduleRequest(
    requestId: number,
    scheduledDate: string,
  ): Promise<any> {
    const response = await this.api.post(
      `/api/v1/manager/schedule-request?request_id=${requestId}&scheduled_date=${scheduledDate}`,
    );
    return response.data;
  }

  async getPerformanceMetrics(periodDays: number = 30): Promise<any> {
    const response = await this.api.get(
      `/api/v1/manager/performance-metrics?period_days=${periodDays}`,
    );
    return response.data;
  }

  // Security Verification методы
  async getVerifiedContractors(): Promise<any[]> {
    const response = await this.api.get('/api/v1/security/verified');
    return response.data;
  }

  async getRejectedContractors(): Promise<any[]> {
    const response = await this.api.get('/api/v1/security/rejected');
    return response.data;
  }

  async getContractorDetails(contractorId: number): Promise<any> {
    const response = await this.api.get(
      `/api/v1/security/contractor/${contractorId}/details`,
    );
    return response.data;
  }

  async getContractorVerificationStatus(contractorId: number): Promise<any> {
    const response = await this.api.get(
      `/api/v1/security/contractor/${contractorId}/status`,
    );
    return response.data;
  }

  async approveContractor(
    contractorId: number,
    approvalData: any,
  ): Promise<any> {
    const response = await this.api.post(
      `/api/v1/security/contractor/${contractorId}/approve`,
      approvalData,
    );
    return response.data;
  }

  async rejectContractor(
    contractorId: number,
    rejectionData: any,
  ): Promise<any> {
    const response = await this.api.post(
      `/api/v1/security/contractor/${contractorId}/reject`,
      rejectionData,
    );
    return response.data;
  }

  async createVerificationRequest(contractorId: number): Promise<any> {
    const response = await this.api.post(
      `/api/v1/security/contractor/${contractorId}/create-verification`,
    );
    return response.data;
  }

  async getSecurityStatistics(): Promise<any> {
    const response = await this.api.get('/api/v1/security/statistics');
    return response.data;
  }

  async checkContractorAccess(contractorId: number): Promise<any> {
    const response = await this.api.get(
      `/api/v1/security/check-contractor-access/${contractorId}`,
    );
    return response.data;
  }

  // HR Documents методы
  async getVerifiedContractorsForHR(): Promise<any[]> {
    const response = await this.api.get('/api/v1/hr/verified-contractors');
    return response.data;
  }

  async getContractorDocuments(contractorId: number): Promise<any[]> {
    const response = await this.api.get(
      `/api/v1/hr/contractor/${contractorId}/documents`,
    );
    return response.data;
  }

  async createDocumentRequest(
    contractorId: number,
    documentData: any,
  ): Promise<any> {
    const response = await this.api.post(
      `/api/v1/hr/contractor/${contractorId}/create-document`,
      documentData,
    );
    return response.data;
  }

  async generateDocument(
    documentId: number,
    generationData: any,
  ): Promise<any> {
    const response = await this.api.post(
      `/api/v1/hr/document/${documentId}/generate`,
      generationData,
    );
    return response.data;
  }

  async completeDocument(documentId: number): Promise<any> {
    const response = await this.api.post(
      `/api/v1/hr/document/${documentId}/complete`,
    );
    return response.data;
  }

  async getDocumentContent(documentId: number): Promise<any> {
    const response = await this.api.get(
      `/api/v1/hr/document/${documentId}/content`,
    );
    return response.data;
  }

  async downloadDocument(documentId: number): Promise<string> {
    const response = await this.api.get(
      `/api/v1/hr/document/${documentId}/download`,
      {
        responseType: 'text',
      },
    );
    return response.data;
  }

  async getHRStatistics(): Promise<any> {
    const response = await this.api.get('/api/v1/hr/statistics');
    return response.data;
  }

  async getContractorDetailsForHR(contractorId: number): Promise<any> {
    const response = await this.api.get(
      `/api/v1/hr/contractor/${contractorId}/details`,
    );
    return response.data;
  }

  async getAvailableDocumentTypes(): Promise<any[]> {
    const response = await this.api.get('/api/v1/hr/document-types');
    return response.data;
  }

  // Telegram Bot методы
  async sendRequestToContractors(requestId: number): Promise<any> {
    const response = await this.api.post(
      `/api/v1/telegram/send-request/${requestId}`,
    );
    return response.data;
  }

  async sendNotificationToContractor(
    contractorId: number,
    notificationData: any,
  ): Promise<any> {
    const response = await this.api.post(
      `/api/v1/telegram/notify-contractor/${contractorId}`,
      notificationData,
    );
    return response.data;
  }

  async sendAssignmentNotification(
    contractorId: number,
    requestId: number,
  ): Promise<any> {
    const response = await this.api.post(
      `/api/v1/telegram/assign-notification/${contractorId}/${requestId}`,
    );
    return response.data;
  }

  async sendStatusUpdateNotification(
    contractorId: number,
    requestId: number,
    statusData: any,
  ): Promise<any> {
    const response = await this.api.post(
      `/api/v1/telegram/status-update/${contractorId}/${requestId}`,
      statusData,
    );
    return response.data;
  }

  async sendBulkNotification(notificationData: any): Promise<any> {
    const response = await this.api.post(
      '/api/v1/telegram/bulk-notification',
      notificationData,
    );
    return response.data;
  }

  async getVerifiedContractorsForNotifications(): Promise<any[]> {
    const response = await this.api.get(
      '/api/v1/telegram/verified-contractors',
    );
    return response.data;
  }

  async testTelegramBotConnection(): Promise<any> {
    const response = await this.api.get('/api/v1/telegram/test-connection');
    return response.data;
  }

  async getBotInfo(): Promise<any> {
    const response = await this.api.get('/api/v1/telegram/bot-info');
    return response.data;
  }

  // Customer Cabinet методы

  async createCustomerRequest(requestData: any): Promise<any> {
    const response = await this.api.post(
      '/api/v1/customer/requests',
      requestData,
    );
    return response.data;
  }

  async getCustomerRequest(requestId: number): Promise<any> {
    const response = await this.api.get(
      `/api/v1/customer/requests/${requestId}`,
    );
    return response.data;
  }

  async updateCustomerRequest(
    requestId: number,
    requestData: any,
  ): Promise<any> {
    const response = await this.api.put(
      `/api/v1/customer/requests/${requestId}`,
      requestData,
    );
    return response.data;
  }

  async cancelCustomerRequest(requestId: number): Promise<any> {
    const response = await this.api.delete(
      `/api/v1/customer/requests/${requestId}`,
    );
    return response.data;
  }

  async getCustomerStatistics(): Promise<any> {
    const response = await this.api.get('/api/v1/customer/statistics');
    return response.data;
  }

  // Admin Panel методы
  async getAdminDashboard(): Promise<any> {
    const response = await this.api.get('/api/v1/admin/dashboard');
    return response.data;
  }

  async getAdminUsers(filters?: any): Promise<any[]> {
    const params = new URLSearchParams();
    if (filters?.role) params.append('role_filter', filters.role);
    if (filters?.status) params.append('status_filter', filters.status);
    if (filters?.search) params.append('search', filters.search);

    const response = await this.api.get(`/api/v1/admin/users?${params}`);
    return response.data;
  }

  async getAdminUser(userId: number): Promise<any> {
    const response = await this.api.get(`/api/v1/admin/users/${userId}`);
    return response.data;
  }

  async createUser(userData: any): Promise<any> {
    const response = await this.api.post('/api/v1/admin/users', userData);
    return response.data;
  }

  async updateUserStatus(userId: number, statusData: any): Promise<any> {
    const response = await this.api.put(
      `/api/v1/admin/users/${userId}/status`,
      statusData,
    );
    return response.data;
  }

  async deleteUser(userId: number): Promise<any> {
    const response = await this.api.delete(`/api/v1/admin/users/${userId}`);
    return response.data;
  }

  async getAdminRequests(filters?: any): Promise<any[]> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status_filter', filters.status);
    if (filters?.priority) params.append('priority_filter', filters.priority);
    if (filters?.urgency) params.append('urgency_filter', filters.urgency);
    if (filters?.search) params.append('search', filters.search);

    const response = await this.api.get(`/api/v1/admin/requests?${params}`);
    return response.data;
  }

  async getAdminRequest(requestId: number): Promise<any> {
    const response = await this.api.get(`/api/v1/admin/requests/${requestId}`);
    return response.data;
  }

  async updateRequestStatus(requestId: number, statusData: any): Promise<any> {
    const response = await this.api.put(
      `/api/v1/admin/requests/${requestId}/status`,
      statusData,
    );
    return response.data;
  }

  async getAdminStatistics(period = '30d'): Promise<any> {
    const response = await this.api.get(
      `/api/v1/admin/statistics?period=${period}`,
    );
    return response.data;
  }

  async getRepairRequest(id: number): Promise<RepairRequest> {
    const response: AxiosResponse<RepairRequest> = await this.api.get(
      `/api/v1/repair-requests/${id}`,
    );
    return response.data;
  }

  async createRepairRequest(data: RepairRequestCreate): Promise<RepairRequest> {
    const response: AxiosResponse<RepairRequest> = await this.api.post(
      '/api/v1/repair-requests/',
      data,
    );
    return response.data;
  }

  async updateRepairRequest(
    id: number,
    data: RepairRequestUpdate,
  ): Promise<RepairRequest> {
    const response: AxiosResponse<RepairRequest> = await this.api.put(
      `/api/v1/repair-requests/${id}`,
      data,
    );
    return response.data;
  }

  async deleteRepairRequest(id: number): Promise<void> {
    await this.api.delete(`/api/v1/repair-requests/${id}`);
  }

  // Отклики исполнителей
  async createContractorResponse(
    requestId: number,
    data: ContractorResponseCreate,
  ): Promise<ContractorResponse> {
    const response: AxiosResponse<ContractorResponse> = await this.api.post(
      `/api/v1/repair-requests/${requestId}/responses`,
      data
    );
    return response.data;
  }

  async getContractorResponses(
    requestId: number,
  ): Promise<ContractorResponse[]> {
    const response: AxiosResponse<ContractorResponse[]> = await this.api.get(
      `/api/v1/repair-requests/${requestId}/responses`
    );
    return response.data;
  }

  // Профили заказчиков
  async getCustomerProfile(): Promise<CustomerProfile> {
    const response: AxiosResponse<CustomerProfile> = await this.api.get(
      '/api/v1/customers/profile',
    );
    return response.data;
  }

  async updateCustomerProfile(
    data: CustomerProfileCreate,
  ): Promise<CustomerProfile> {
    const response: AxiosResponse<CustomerProfile> = await this.api.put(
      '/api/v1/customers/profile',
      data,
    );
    return response.data;
  }

  async createCustomerProfile(
    data: CustomerProfileCreate,
  ): Promise<CustomerProfile> {
    const response: AxiosResponse<CustomerProfile> = await this.api.post(
      '/api/v1/customers/register',
      data,
    );
    return response.data;
  }

  async getCustomerRequests(): Promise<RepairRequest[]> {
    const response: AxiosResponse<RepairRequest[]> = await this.api.get(
      '/api/v1/customers/requests',
    );
    return response.data;
  }

  // Профили исполнителей
  async getContractorProfile(): Promise<ContractorProfile> {
    const response: AxiosResponse<ContractorProfile> = await this.api.get(
      '/api/v1/contractors/profile',
    );
    return response.data;
  }

  async updateContractorProfileByAdmin(
    userId: number,
    data: ContractorProfileCreate,
  ): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await this.api.put(
      `/api/v1/admin/contractors/${userId}/profile`,
      data,
    );
    return response.data;
  }

  // Аналитика для главной страницы
  async getDashboardAnalytics(): Promise<any> {
    const response: AxiosResponse<any> = await this.api.get(
      '/api/v1/dashboard/analytics',
    );
    return response.data;
  }

  async createContractorProfile(
    data: ContractorProfileCreate,
  ): Promise<ContractorProfile> {
    const response: AxiosResponse<ContractorProfile> = await this.api.post(
      '/api/v1/contractors/register',
      data,
    );
    return response.data;
  }

  async uploadContractorFile(file: File): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response: AxiosResponse<{ url: string }> = await this.api.post(
      '/api/v1/contractors/upload-file',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      },
    );
    return response.data;
  }

  async getTelegramLink(): Promise<{ link: string }> {
    const response: AxiosResponse<{ link: string }> = await this.api.get(
      '/api/v1/contractors/telegram-link',
    );
    return response.data;
  }

  // Админ методы для получения списков пользователей
  async getAllUsers(
    roleFilter?: string,
    limit = 20,
    offset = 0,
  ): Promise<User[]> {
    const params = new URLSearchParams();
    if (roleFilter) params.append('role_filter', roleFilter);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    // Определяем endpoint в зависимости от роли пользователя
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const endpoint =
      user.role === 'admin' ? '/api/v1/admin/users' : '/api/v1/manager/users';

    const response: AxiosResponse<User[]> = await this.api.get(
      `${endpoint}?${params}`,
    );
    return response.data;
  }

  async getAllCustomers(limit = 20, offset = 0): Promise<User[]> {
    return this.getAllUsers('customer', limit, offset);
  }

  async getAllContractors(limit = 20, offset = 0): Promise<User[]> {
    return this.getAllUsers('contractor', limit, offset);
  }

  async getAllContractorProfiles(
    limit = 20,
    offset = 0,
  ): Promise<ContractorProfile[]> {
    const response: AxiosResponse<ContractorProfile[]> = await this.api.get(
      `/api/v1/contractors/profiles?limit=${limit}&offset=${offset}`,
    );
    return response.data;
  }

  async getAllCustomerProfiles(
    limit = 20,
    offset = 0,
  ): Promise<CustomerProfile[]> {
    const response: AxiosResponse<CustomerProfile[]> = await this.api.get(
      `/api/v1/customers/profiles?limit=${limit}&offset=${offset}`,
    );
    return response.data;
  }

  // Методы для повторной отправки писем
  async resendEmailVerification(userId: number): Promise<void> {
    await this.api.post(`/api/v1/auth/resend-verification/${userId}`);
  }

  // Методы для системы верификации исполнителей
  async getContractorProfileExtended(contractorId: number): Promise<any> {
    const response: AxiosResponse<any> = await this.api.get(
      `/api/v1/contractor-verification/profile/${contractorId}`,
    );
    return response.data;
  }

  async updateContractorProfile(contractorId: number, profileData: any): Promise<any> {
    const response: AxiosResponse<any> = await this.api.put(
      `/api/v1/contractor-verification/profile/${contractorId}`,
      profileData,
    );
    return response.data;
  }

  async addEducationRecord(contractorId: number, educationData: any): Promise<any> {
    const response: AxiosResponse<any> = await this.api.post(
      `/api/v1/contractor-verification/education/${contractorId}`,
      educationData,
    );
    return response.data;
  }

  async deleteEducationRecord(educationId: number): Promise<void> {
    await this.api.delete(`/api/v1/contractor-verification/education/${educationId}`);
  }

  async uploadContractorDocument(contractorId: number, formData: FormData): Promise<any> {
    const response: AxiosResponse<any> = await this.api.post(
      `/api/v1/contractor-verification/documents/${contractorId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      },
    );
    return response.data;
  }

  async deleteContractorDocument(documentId: number): Promise<void> {
    await this.api.delete(`/api/v1/contractor-verification/documents/${documentId}`);
  }

  async verifyDocument(documentId: number, verificationData: any): Promise<any> {
    const response: AxiosResponse<any> = await this.api.put(
      `/api/v1/contractor-verification/documents/${documentId}/verify`,
      verificationData,
    );
    return response.data;
  }

  async verifyContractor(contractorId: number, verificationData: any): Promise<any> {
    const response: AxiosResponse<any> = await this.api.put(
      `/api/v1/contractor-verification/contractor/${contractorId}/verify`,
      verificationData,
    );
    return response.data;
  }

  async getPendingVerifications(verificationType?: string): Promise<any[]> {
    const params = verificationType ? `?verification_type=${verificationType}` : '';
    const response: AxiosResponse<any[]> = await this.api.get(
      `/api/v1/contractor-verification/pending${params}`,
    );
    return response.data;
  }

  // Методы для работы с аватарами
  async uploadAvatar(file: File): Promise<{ avatar_url: string; avatar_urls: Record<string, string> }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response: AxiosResponse<{ avatar_url: string; avatar_urls: Record<string, string> }> = await this.api.post(
      '/api/v1/avatar/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      },
    );
    return response.data;
  }

  async removeAvatar(): Promise<void> {
    await this.api.delete('/api/v1/avatar/remove');
  }

  async getAvatarInfo(): Promise<{ has_avatar: boolean; avatar_url: string; avatar_urls: Record<string, string> }> {
    const response: AxiosResponse<{ has_avatar: boolean; avatar_url: string; avatar_urls: Record<string, string> }> = await this.api.get('/api/v1/avatar/info');
    return response.data;
  }

  // Методы для обновления пользователя
  async updateUser(userId: number, userData: Partial<User>): Promise<User> {
    const response: AxiosResponse<User> = await this.api.put(`/api/v1/users/${userId}`, userData);
    return response.data;
  }

  // Методы для работы с Telegram чатом
  async getChatHistory(telegramUserId: number): Promise<any> {
    const response: AxiosResponse<any> = await this.api.get(`/api/v1/telegram-chat/chat-history/${telegramUserId}`);
    return response.data;
  }

  async markMessagesRead(telegramUserId: number): Promise<void> {
    await this.api.post(`/api/v1/telegram-chat/mark-messages-read/${telegramUserId}`);
  }

  async getUnreadCounts(): Promise<any> {
    const response: AxiosResponse<any> = await this.api.get('/api/v1/telegram-chat/unread-counts');
    return response.data;
  }
}

export const apiService = new ApiService();
