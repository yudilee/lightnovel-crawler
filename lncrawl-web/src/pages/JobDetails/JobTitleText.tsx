import { JobType, type Job } from '@/types';

export const JobTitleText: React.FC<{ job: Job }> = ({ job }) => {
  switch (job.type) {
    case JobType.NOVEL:
    case JobType.IMAGE:
    case JobType.FULL_NOVEL:
      return job.extra.url;
    case JobType.VOLUME:
      return `${job.extra.novel_title} · Volume ${job.extra.volume_serial}`;
    case JobType.CHAPTER:
      return `${job.extra.novel_title} · Chapter ${job.extra.chapter_serial}`;
    case JobType.NOVEL_BATCH:
    case JobType.FULL_NOVEL_BATCH: {
      const length = job.extra.urls!.length;
      const first = job.extra.urls![0];
      const more = length > 1 ? ` & ${length - 1} more` : '';
      return `${first}${more}`;
    }
    case JobType.VOLUME_BATCH:
      return `Crawl ${job.extra.volume_ids!.length} volumes`;
    case JobType.CHAPTER_BATCH:
      return `Crawl ${job.extra.chapter_ids!.length} chapters`;
    case JobType.IMAGE_BATCH:
      return `Crawl ${job.extra.image_ids!.length} images`;
    case JobType.ARTIFACT:
      return `${job.extra.novel_title} · ${job.extra.format}`;
    case JobType.ARTIFACT_BATCH: {
      const length = job.extra.formats!.length;
      const first = job.extra.formats!.slice(0, 2).join(', ');
      const more = length > 2 ? ` & ${length - 2} more` : '';
      return `${job.extra.novel_title} · ${first}${more}`;
    }
    default:
      return null;
  }
};
