import { JobStatus, type Job } from '@/types';
import { Progress, type ProgressProps } from 'antd';

function getProgressStatus(job: Job): ProgressProps['status'] {
  switch (job.status) {
    case JobStatus.PENDING:
      return 'normal';
    case JobStatus.RUNNING:
      return 'active';
    case JobStatus.SUCCESS:
      return 'success';
    case JobStatus.FAILED:
    case JobStatus.CANCELED:
      return 'exception';
  }
}

export const JobProgressCircle: React.FC<
  {
    job: Job;
  } & ProgressProps
> = ({ job, ...props }) => {
  return (
    <Progress
      size="small"
      {...props}
      type="circle"
      percent={job.progress || 0}
      status={getProgressStatus(job)}
    />
  );
};

export const JobProgressLine: React.FC<
  {
    job: Job;
  } & ProgressProps
> = ({ job, ...props }) => {
  return (
    <Progress
      size={['100%', 12]}
      {...props}
      type="line"
      percent={job.progress || 0}
      status={getProgressStatus(job)}
      strokeColor={{ from: '#108ee9', to: '#87d068' }}
    />
  );
};
