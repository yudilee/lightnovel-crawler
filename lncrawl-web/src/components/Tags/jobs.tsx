import { JobPriority, JobStatus, JobType } from '@/types';
import {
  AppstoreOutlined,
  BookOutlined,
  CheckOutlined,
  CloseOutlined,
  FileTextOutlined,
  FolderOutlined,
  HourglassOutlined,
  LoadingOutlined,
  PictureOutlined,
  ReadOutlined,
  ThunderboltOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import { Tag } from 'antd';

export const JobPriorityTag: React.FC<{ value: JobPriority }> = ({ value }) => {
  switch (value) {
    case JobPriority.LOW:
      return <Tag icon={<ThunderboltOutlined />}>Low Priority</Tag>;
    case JobPriority.NORMAL:
      return (
        <Tag icon={<ThunderboltOutlined />} color="gold">
          Normal Priority
        </Tag>
      );
    case JobPriority.HIGH:
      return (
        <Tag icon={<ThunderboltOutlined />} color="volcano">
          <b>High Priority</b>
        </Tag>
      );
  }
};

export const JobStatusTag: React.FC<{ value: JobStatus }> = ({ value }) => {
  switch (value) {
    case JobStatus.PENDING:
      return <Tag icon={<HourglassOutlined />}>Pending</Tag>;
    case JobStatus.RUNNING:
      return (
        <Tag icon={<LoadingOutlined spin />} color="cyan">
          Running
        </Tag>
      );
    case JobStatus.SUCCESS:
      return (
        <Tag icon={<CheckOutlined />} color="orange">
          Success
        </Tag>
      );
    case JobStatus.CANCELED:
      return (
        <Tag icon={<CloseOutlined />} color="red">
          Canceled
        </Tag>
      );
    case JobStatus.FAILED:
      return (
        <Tag icon={<WarningOutlined />} color="red">
          Failed
        </Tag>
      );
    default:
      return null;
  }
};

export const JobTypeTag: React.FC<{ value: JobType }> = ({ value }) => {
  switch (value) {
    case JobType.NOVEL:
      return <Tag icon={<BookOutlined />}>Novel</Tag>;
    case JobType.NOVEL_BATCH:
      return (
        <Tag icon={<BookOutlined />} color="cyan">
          Novels
        </Tag>
      );
    case JobType.FULL_NOVEL:
      return <Tag icon={<ReadOutlined />}>Full Novel</Tag>;
    case JobType.FULL_NOVEL_BATCH:
      return (
        <Tag icon={<ReadOutlined />} color="cyan">
          Full Novels
        </Tag>
      );
    case JobType.CHAPTER:
      return <Tag icon={<FileTextOutlined />}>Chapter</Tag>;
    case JobType.CHAPTER_BATCH:
      return (
        <Tag icon={<FileTextOutlined />} color="cyan">
          Chapters
        </Tag>
      );
    case JobType.VOLUME:
      return <Tag icon={<FolderOutlined />}>Volume</Tag>;
    case JobType.VOLUME_BATCH:
      return (
        <Tag icon={<FolderOutlined />} color="cyan">
          Volumes
        </Tag>
      );
    case JobType.IMAGE:
      return <Tag icon={<PictureOutlined />}>Image</Tag>;
    case JobType.IMAGE_BATCH:
      return (
        <Tag icon={<PictureOutlined />} color="cyan">
          Images
        </Tag>
      );
    case JobType.ARTIFACT:
      return <Tag icon={<AppstoreOutlined />}>Artifact</Tag>;
    case JobType.ARTIFACT_BATCH:
      return (
        <Tag icon={<AppstoreOutlined />} color="cyan">
          Artifacts
        </Tag>
      );
    default:
      return null;
  }
};
