export const UserRole = {
  USER: 'user',
  ADMIN: 'admin',
};
export type UserRole = (typeof UserRole)[keyof typeof UserRole];

export const UserTier = {
  BASIC: 0,
  PREMIUM: 1,
  VIP: 2,
};
export type UserTier = (typeof UserTier)[keyof typeof UserTier];

export const JobPriority = {
  LOW: 0,
  NORMAL: 1,
  HIGH: 2,
};
export type JobPriority = (typeof JobPriority)[keyof typeof JobPriority];

export const JobStatus = {
  PENDING: 0,
  RUNNING: 1,
  SUCCESS: 2,
  FAILED: 3,
  CANCELED: 4,
};
export type JobStatus = (typeof JobStatus)[keyof typeof JobStatus];

export const JobType = {
  NOVEL: 0,
  NOVEL_BATCH: 1,
  FULL_NOVEL: 5,
  FULL_NOVEL_BATCH: 6,
  CHAPTER: 10,
  CHAPTER_BATCH: 11,
  VOLUME: 20,
  VOLUME_BATCH: 21,
  IMAGE: 30,
  IMAGE_BATCH: 31,
  ARTIFACT: 40,
  ARTIFACT_BATCH: 41,
};
export type JobType = (typeof JobType)[keyof typeof JobType];

export const OutputFormat = {
  json: 'json',
  epub: 'epub',
  text: 'text',
  web: 'web',
  docx: 'docx',
  mobi: 'mobi',
  pdf: 'pdf',
  rtf: 'rtf',
  txt: 'txt',
  azw3: 'azw3',
  fb2: 'fb2',
  lit: 'lit',
  lrf: 'lrf',
  oeb: 'oeb',
  pdb: 'pdb',
  rb: 'rb',
  snb: 'snb',
  tcr: 'tcr',
};
export type OutputFormat = (typeof OutputFormat)[keyof typeof OutputFormat];
