import type {
  JobPriority,
  JobStatus,
  JobType,
  OutputFormat,
  UserRole,
  UserTier,
} from './enums';

export * from './enums';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  tier: UserTier;
  is_active: boolean;
  created_at: number;
  updated_at: number;
}

export interface LoginResponse {
  user: User;
  token: string;
  is_verified: boolean;
}

export interface Paginatied<T> {
  total: number;
  offset: number;
  limit: number;
  items: T[];
}

export interface Job {
  id: string;
  created_at: number;
  updated_at: number;
  parent_job_id?: string;

  user_id: string;
  type: JobType;
  priority: JobPriority;

  status: JobStatus;
  is_done: boolean;
  is_running: boolean;
  is_pending: boolean;

  error: string;
  started_at: number;
  finished_at: number;

  done: number;
  total: number;
  progress: number;

  extra: {
    url?: string;
    urls?: string[];
    novel_id?: string;
    volume_id?: string;
    volume_ids?: string[];
    chapter_id?: string;
    chapter_ids?: string[];
    image_id?: string;
    image_ids?: string[];
    format?: OutputFormat;
    formats?: OutputFormat[];
    novel_title?: string;
    volume_serial?: string;
    chapter_serial?: string;
    artifact_id?: string;
  };
}

export interface Novel {
  id: string;

  url: string;
  domain: string;

  title: string;
  crawled: boolean;
  authors: string;
  synopsis: string;
  tags: string[];
  manga: boolean;
  mtl: boolean;
  language: string;
  rtl: boolean;
  volume_count: number;
  chapter_count: number;

  cover_url: string;
  cover_file: string;
  cover_available: boolean;

  created_at: number;
  updated_at: number;
  extra: {
    crawler_version?: number;
  };
}

export interface Chapter {
  id: number;
  created_at: number;
  updated_at: number;

  novel_id: string;
  volume_id: string;
  url: string;
  title: string;
  serial: number;

  is_done: boolean;
  is_available: boolean;
  content_file: string;

  extra: {
    crawler_version?: number;
  };
}

export interface Volume {
  id: number;
  novel_id: string;
  title: string;
  serial: number;
  chapter_count: number;
  created_at: number;
  updated_at: number;
}

export interface Artifact {
  id: string;
  format: OutputFormat;
  created_at: number;
  updated_at: number;
  novel_id: string;
  job_id?: string;
  user_id?: string;
  is_zip: boolean;
  output_file: string;
  file_name: string;
  file_size?: number;
  is_available: boolean;
}

export interface SupportedSource {
  url: string;
  domain: string;
  has_manga: boolean;
  has_mtl: boolean;
  language: string;
  is_disabled: boolean;
  disable_reason?: string;
  can_search: boolean;
  can_login: boolean;
}
