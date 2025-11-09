import { type Job, type User } from '@/types';
import { stringifyError } from '@/utils/errors';
import {
  Button,
  Card,
  Flex,
  Grid,
  Result,
  Space,
  Spin,
  Typography,
} from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { JobListPage } from '../JobList';
import { JobDetailsCard } from './JobDetailsCard';
import { UserDetailsCard } from './UserDetailsCard';

export const JobDetailsPage: React.FC<any> = () => {
  const { lg } = Grid.useBreakpoint();
  const { id } = useParams<{ id: string }>();

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const [job, setJob] = useState<Job>();
  const [user, setUser] = useState<User>();

  const fetchJob = async (id: string) => {
    setError(undefined);
    try {
      const { data: job } = await axios.get<Job>(`/api/job/${id}`);
      setJob(job);

      const { data: user } = await axios.get<User>(`/api/user/${job.user_id}`);
      setUser(user);
    } catch (err: any) {
      setError(stringifyError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      fetchJob(id);
    }
  }, [id, refreshId]);

  useEffect(() => {
    if (job && !job.is_done) {
      const iid = setInterval(() => {
        setRefreshId((v) => v + 1);
      }, 2000);
      return () => {
        clearInterval(iid);
      };
    }
  }, [job]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (!job || !user) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load job data"
          subTitle={error}
          extra={[
            <Button
              onClick={() => {
                setLoading(true);
                setRefreshId((v) => v + 1);
              }}
            >
              Retry
            </Button>,
          ]}
        />
      </Flex>
    );
  }

  return (
    <Space direction="vertical" size={lg ? 'middle' : 'small'}>
      <JobDetailsCard job={job} />
      <UserDetailsCard user={user} />
      <Card>
        <Typography.Title level={4} style={{ margin: 0, marginBottom: 16 }}>
          Child Jobs
        </Typography.Title>
        <JobListPage key={job.id} parentJobId={job.id} disableFilters />
      </Card>
    </Space>
  );
};
