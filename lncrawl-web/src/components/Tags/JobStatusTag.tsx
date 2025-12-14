import { JobStatus, type Job } from '@/types';
import {
  CheckOutlined,
  CloseOutlined,
  HourglassOutlined,
  LoadingOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import { Tag } from 'antd';

export const JobStatusTag: React.FC<{ job: Job }> = ({ job }) => {
  switch (job.status) {
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
          {job.total > 1 ? 'Completed' : 'Success'}
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
