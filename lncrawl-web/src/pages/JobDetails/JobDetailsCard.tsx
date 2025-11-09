import {
  JobPriorityTag,
  JobStatusTag,
  JobTypeTag,
} from '@/components/Tags/jobs';
import { JobStatus, type Job } from '@/types';
import { formatDate, formatDuration } from '@/utils/time';
import {
  ClockCircleFilled,
  ClockCircleOutlined,
  HourglassFilled,
} from '@ant-design/icons';
import { Alert, Card, Flex, Grid, Tag, Typography } from 'antd';
import { JobActionButtons } from '../JobList/JobActionButtons';
import { JobProgressLine } from '../JobList/JobProgessBar';
import { JobTitleText } from './JobTitleText';

export const JobDetailsCard: React.FC<{ job: Job }> = ({ job }) => {
  const { lg } = Grid.useBreakpoint();

  return (
    <Card variant="outlined">
      <Typography.Title
        level={lg ? 2 : 3}
        style={{
          margin: 0,
          marginBottom: 8,
          fontFamily: "'Roboto Slab', serif",
        }}
      >
        <JobTitleText job={job} />
      </Typography.Title>

      <Flex wrap align="center" gap={5}>
        <JobTypeTag value={job.type} />
        <JobPriorityTag value={job.priority} />
        <Tag icon={<ClockCircleOutlined />} color="default">
          <b>Requested:</b> {formatDate(job.created_at)}
        </Tag>
      </Flex>

      <JobProgressLine job={job} size={['100%', 18]} style={{ marginTop: 8 }} />

      <Flex wrap gap={4} style={{ marginTop: 5 }}>
        <JobStatusTag value={job.status} />
        {!job.is_pending && (
          <Tag icon={<ClockCircleOutlined />} color="default">
            <b>Started:</b> {formatDate(job.started_at)}
          </Tag>
        )}
        {!job.is_done && (
          <Tag icon={<ClockCircleOutlined spin />} color="default">
            <b>Elapsed:</b> {formatDuration(Date.now() - job.started_at)}
          </Tag>
        )}
        {job.is_done && (
          <Tag icon={<ClockCircleFilled />} color="default">
            <b>Completed:</b> {formatDate(job.finished_at)}
          </Tag>
        )}
        {job.is_done && (
          <Tag icon={<HourglassFilled />} color="default">
            <b>Runtime:</b> {formatDuration(job.finished_at - job.started_at)}
          </Tag>
        )}
      </Flex>

      {Boolean(job.error) && (
        <Alert
          showIcon
          description={job.error}
          type={job.status === JobStatus.FAILED ? 'error' : 'warning'}
          style={{ marginTop: 15, padding: '10px 20px' }}
        />
      )}

      <Flex justify="end" align="center" gap={'10px'} style={{ marginTop: 15 }}>
        <JobActionButtons job={job} />
      </Flex>
    </Card>
  );
};
