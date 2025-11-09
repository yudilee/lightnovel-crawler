import { JobStatusTag, JobTypeTag } from '@/components/Tags/jobs';
import { type Job } from '@/types';
import { formatDate } from '@/utils/time';
import { ClockCircleOutlined } from '@ant-design/icons';
import { Card, Flex, Grid, Space, Tag, Typography } from 'antd';
import { Link } from 'react-router-dom';
import { JobTitleText } from '../JobDetails/JobTitleText';
import { JobActionButtons } from './JobActionButtons';
import { JobProgressCircle, JobProgressLine } from './JobProgessBar';

export const JobListItemCard: React.FC<{
  job: Job;
  onChange?: () => any;
}> = ({ job, onChange }) => {
  const { lg } = Grid.useBreakpoint();
  return (
    <Link to={`/job/${job.id}`}>
      <Card
        hoverable
        style={{ marginBottom: 5 }}
        styles={{
          body: { padding: 15 },
        }}
      >
        <Flex wrap align="center" justify="end" gap="15px">
          {lg && <JobProgressCircle job={job} size={48} />}

          <div style={{ flex: 1, minWidth: lg ? 0 : '100%' }}>
            <Typography.Text
              ellipsis
              style={{
                display: 'block',
                fontSize: '1.15rem',
                fontFamily: "'Roboto Slab', serif",
              }}
            >
              <JobTitleText job={job} />
            </Typography.Text>

            <Space style={{ marginTop: 5 }}>
              <JobTypeTag value={job.type} />
              <Tag icon={<ClockCircleOutlined />} color="default">
                {formatDate(job.created_at)}
              </Tag>
              <JobStatusTag value={job.status} />
            </Space>

            {!lg && <JobProgressLine job={job} style={{ marginTop: 10 }} />}
          </div>

          <Flex
            wrap
            justify="end"
            align="center"
            gap={5}
            onClick={(e) => e.preventDefault()}
          >
            <JobActionButtons job={job} size="small" onChange={onChange} />
          </Flex>
        </Flex>
      </Card>
    </Link>
  );
};
