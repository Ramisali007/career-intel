/**
 * API Client - Communicates with the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private token: string | null = null;

  constructor() {
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("token");
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("token", token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
    }
  }

  logout() {
    this.clearToken();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  }

  getToken() {
    return this.token;
  }

  private async request(path: string, options: RequestInit = {}) {
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    if (res.status === 401) {
      const isAuthRoute = path.startsWith("/auth/login") || path.startsWith("/auth/register");
      const error = await res.json().catch(() => ({ detail: "Unauthorized" }));
      if (!isAuthRoute) {
        this.clearToken();
        if (typeof window !== "undefined" && window.location.pathname !== "/login" && window.location.pathname !== "/register") {
          window.location.href = "/login";
        }
      }
      throw new Error(error.detail || "Invalid email or password");
    }

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `Request failed: ${res.status}`);
    }

    return res.json();
  }

  // ── Auth ──
  async register(email: string, password: string, fullName: string) {
    const data = await this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async login(email: string, password: string) {
    const data = await this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async getMe() {
    return this.request("/auth/me");
  }

  // ── Documents ──
  async uploadDocument(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return this.request("/documents/upload", {
      method: "POST",
      body: formData,
    });
  }

  async listDocuments() {
    try {
      const data = await this.request("/documents/");
      if (data && Array.isArray(data.items)) return data.items;
      if (Array.isArray(data)) return data;
      return [];
    } catch {
      return [];
    }
  }

  async getDocument(id: string) {
    return this.request(`/documents/${id}`);
  }

  async deleteDocument(id: string) {
    return this.request(`/documents/${id}`, { method: "DELETE" });
  }

  // ── Job Descriptions ──
  async createJobDescription(text: string, title?: string) {
    return this.request("/job-descriptions/", {
      method: "POST",
      body: JSON.stringify({ text, title: title || "" }),
    });
  }

  async listJobDescriptions() {
    try {
      const data = await this.request("/job-descriptions/");
      if (data && Array.isArray(data.items)) return data.items;
      if (Array.isArray(data)) return data;
      return [];
    } catch {
      return [];
    }
  }

  async getJobDescription(id: string) {
    return this.request(`/job-descriptions/${id}`);
  }

  async deleteJobDescription(id: string) {
    return this.request(`/job-descriptions/${id}`, { method: "DELETE" });
  }

  // ── Analyses ──
  async createAnalysis(documentId: string, jobDescriptionId: string) {
    return this.request("/analyses/", {
      method: "POST",
      body: JSON.stringify({
        document_id: documentId,
        job_description_id: jobDescriptionId,
      }),
    });
  }

  async getAnalysis(id: string) {
    return this.request(`/analyses/${id}`);
  }

  async listAnalyses() {
    try {
      const data = await this.request("/analyses/");
      if (data && Array.isArray(data.items)) return data.items;
      if (Array.isArray(data)) return data;
      return [];
    } catch {
      return [];
    }
  }

  async deleteAnalysis(id: string) {
    return this.request(`/analyses/${id}`, { method: "DELETE" });
  }

  // ── Recommendations ──
  async getRecommendations(analysisId: string) {
    return this.request(`/recommendations/analysis/${analysisId}`);
  }

  async recommendationAction(recId: string, action: string, editedText?: string) {
    return this.request(`/recommendations/${recId}/action`, {
      method: "POST",
      body: JSON.stringify({ action, edited_text: editedText }),
    });
  }

  async approveAllSafe(analysisId: string) {
    return this.request(`/recommendations/analysis/${analysisId}/approve-all`, {
      method: "POST",
    });
  }

  // ── Profile ──
  async getProfile() {
    return this.request("/profile/");
  }

  async updateProfile(data: Record<string, unknown>) {
    return this.request("/profile/", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async purgeUserData() {
    return this.request("/profile/purge-data", {
      method: "POST",
    });
  }

  // ── CV Versions ──
  async listCVVersions() {
    const data = await this.request("/cv-versions/");
    return data.items || data;
  }

  async getCVVersion(id: string) {
    return this.request(`/cv-versions/${id}`);
  }

  async deleteCVVersion(id: string) {
    return this.request(`/cv-versions/${id}`, { method: "DELETE" });
  }

  async rollbackCVVersion(id: string) {
    return this.request(`/cv-versions/${id}/rollback`, { method: "POST" });
  }

  async getCVVersionDiff(versionId: string) {
    return this.request(`/cv-versions/${versionId}/diff`);
  }

  async getGapAnalysis(analysisId: string) {
    return this.request(`/analyses/${analysisId}/gap-analysis`);
  }

  async optimizeAnalysis(analysisId: string) {
    return this.request(`/analyses/${analysisId}/optimize`, {
      method: "POST",
    });
  }

  // ── Multi-JD Analysis (§32, §33) ──
  async createMultiJDAnalysis(data: { document_id: string; job_descriptions: { title: string; text: string }[] }) {
    return this.request("/analyses/multi-jd", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ── Exports (§41-43, §93) ──
  async getExportTemplates() {
    return this.request("/exports/templates");
  }

  async downloadExport(versionId: string, format: "pdf" | "docx", template: string = "ats_classic") {
    const token = this.getToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}/exports/${versionId}/${format}?template=${template}`, {
      method: "POST",
      headers,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Export failed" }));
      throw new Error(err.detail || `Export failed with status ${res.status}`);
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `CV_${template}.${format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
}

export const api = new ApiClient();
export default api;
