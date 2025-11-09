import { JobType, type Job } from '@/types';
import { Space } from 'antd';

export const JobTitleText: React.FC<{ job: Job }> = ({ job }) => {
  switch (job.type) {
    case JobType.NOVEL:
    case JobType.FULL_NOVEL:
      return job.extra.url;
    case JobType.NOVEL_BATCH:
    case JobType.FULL_NOVEL_BATCH: {
      const size = job.extra.urls?.length;
      if (!size) return undefined;
      const first = job.extra.urls![0];
      if (size < 2) return first;
      return `${first} & ${size - 1} more`;
    }
    case JobType.VOLUME:
      return (
        <Space>
          {job.extra.novel_title && <span>{job.extra.novel_title}</span>}
          &middot;
          {job.extra.volume_serial && (
            <span>Volume {job.extra.volume_serial}</span>
          )}
        </Space>
      );
    case JobType.VOLUME_BATCH:
      return `Crawl ${job.extra.volume_ids?.length ?? 0} volumes`;
    case JobType.CHAPTER:
      return (
        <Space>
          {job.extra.novel_title && <span>{job.extra.novel_title}</span>}
          &middot;
          {job.extra.chapter_serial && (
            <span>Chapter {job.extra.chapter_serial}</span>
          )}
        </Space>
      );
    case JobType.CHAPTER_BATCH:
      return `Crawl ${job.extra.chapter_ids?.length ?? 0} chapters`;
    case JobType.IMAGE:
      return job.extra.url;
    case JobType.IMAGE_BATCH:
      return `Crawl ${job.extra.image_ids?.length ?? 0} images`;
    case JobType.ARTIFACT:
      return (
        <Space>
          {job.extra.novel_title && <span>{job.extra.novel_title}</span>}
          &middot;
          {job.extra.format && (
            <strong style={{ fontFamily: 'monospace' }}>
              {job.extra.format}
            </strong>
          )}
        </Space>
      );
    case JobType.ARTIFACT_BATCH:
      return (
        <Space>
          {job.extra.novel_title && <span>{job.extra.novel_title}</span>}
          &middot;
          {Boolean(job.extra.formats?.length) && (
            <strong style={{ fontFamily: 'monospace' }}>
              {job.extra.formats!.join(', ')}
            </strong>
          )}
        </Space>
      );
    default:
      return null;
  }
};
