import { JobEtaTimeTag } from '@/components/Tags/JobEtaTimeTag';
import { JobPriorityTag } from '@/components/Tags/JobPriorityTag';
import { JobStatusTag } from '@/components/Tags/JobStatusTag';
import { JobTypeTag } from '@/components/Tags/JobTypeTag';
import type { Job } from '@/types';
import { formatDate, formatDuration } from '@/utils/time';
import { ClockCircleFilled, ClockCircleOutlined } from '@ant-design/icons';
import { Card, Flex, Grid, Tag, Typography } from 'antd';
import { JobActionButtons } from '../JobList/JobActionButtons';
import { JobProgressLine } from '../JobList/JobProgessBar';

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
        {job.job_title || `Request ${job.id}`}
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
        {!!job.is_running && (
          <Tag icon={<ClockCircleOutlined spin />} color="default">
            <b>Elapsed:</b> {formatDuration(Date.now() - job.started_at!)}
          </Tag>
        )}
        <JobEtaTimeTag job={job} />
        {!!job.is_done && (
          <Tag icon={<ClockCircleFilled />} color="default">
            <b>Completed:</b> {formatDate(job.finished_at)}
          </Tag>
        )}
      </Flex>

      <JobErrorDetailsCard job={job} />

      <Flex justify="end" align="center" gap={'10px'} style={{ marginTop: 15 }}>
        <JobActionButtons job={job} />
      </Flex>
    </Card>
  );
};

export const JobErrorDetailsCard: React.FC<{ job: Job }> = ({ job }) => {
  if (!job.error) {
    return null;
  }

  const html = job.error
    .split('\n')
    .filter(Boolean)
    .map((line) => line.replace(/^\s+/, '&nbsp;'))
    .join('<br/>');

  return (
    <pre
      style={{
        fontSize: '0.775rem',
        maxHeight: 300,
        margin: '15px 0',
        padding: '10px 20px',
        whiteSpace: 'nowrap',
        overflow: 'auto',
        color: '#f8f749',
        border: '1px solid #f8f749',
        background: '#f8f74910',
      }}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
};
