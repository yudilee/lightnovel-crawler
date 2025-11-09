import { JobStatus, JobType } from '@/types';

export const JobStatusFilterParams = [
  {
    value: 'any',
    label: 'Any',
  },
  {
    value: 'successful',
    label: 'Successful',
    params: { status: JobStatus.SUCCESS },
  },
  {
    value: 'failed',
    label: 'Failed',
    params: { status: JobStatus.FAILED },
  },
  {
    value: 'canceled',
    label: 'Canceled',
    params: { status: JobStatus.CANCELED },
  },
  {
    value: 'pending',
    label: 'Pending',
    params: { status: JobStatus.PENDING },
  },
  {
    value: 'running',
    label: 'Running',
    params: { status: JobStatus.RUNNING },
  },
];

export const JobTypeFilterParams = [
  {
    value: -1,
    label: 'Any',
  },
  {
    value: JobType.NOVEL,
    label: 'Novel',
  },
  {
    value: JobType.NOVEL_BATCH,
    label: 'Novel Batch',
  },
  {
    value: JobType.FULL_NOVEL,
    label: 'Full Novel',
  },
  {
    value: JobType.FULL_NOVEL_BATCH,
    label: 'Full Novel Batch',
  },
  {
    value: JobType.CHAPTER,
    label: 'Chapter',
  },
  {
    value: JobType.CHAPTER_BATCH,
    label: 'Chapter Batch',
  },
  {
    value: JobType.VOLUME,
    label: 'Volume',
  },
  {
    value: JobType.VOLUME_BATCH,
    label: 'Volume Batch',
  },
  {
    value: JobType.IMAGE,
    label: 'Image',
  },
  {
    value: JobType.IMAGE_BATCH,
    label: 'Image Batch',
  },
  {
    value: JobType.ARTIFACT,
    label: 'Artifact',
  },
  {
    value: JobType.ARTIFACT_BATCH,
    label: 'Artifact Batch',
  },
];
