import { ArtifactListCard } from '@/components/ArtifactList/ArtifactListCard';
import { type Artifact, type Job, type Novel, type User } from '@/types';
import { stringifyError } from '@/utils/errors';
import { Button, Flex, Grid, Result, Space, Spin } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { JobListPage } from '../JobList';
import { NovelDetailsCard } from '../NovelDetails/NovelDetailsCard';
import { JobDetailsCard } from './JobDetailsCard';
import { UserDetailsCard } from './UserDetailsCard';

export const JobDetailsPage: React.FC<any> = () => {
  const { lg } = Grid.useBreakpoint();
  const { id } = useParams<{ id: string }>();

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const [job, setJob] = useState<Job>();
  const [user, setUser] = useState<User | undefined>();
  const [novel, setNovel] = useState<Novel | undefined>();
  const [artifact, setArtifact] = useState<Artifact | undefined>();

  useEffect(() => {
    const fetchJob = async (id: string) => {
      setError(undefined);
      try {
        const { data: job } = await axios.get<Job>(`/api/job/${id}`);
        setJob(job);
      } catch (err: any) {
        setError(stringifyError(err));
      } finally {
        setLoading(false);
      }
    };
    if (id) {
      fetchJob(id);
    }
  }, [id, refreshId]);

  useEffect(() => {
    const fetchUser = async (id: string) => {
      try {
        const res = await axios.get<User>(`/api/user/${id}`);
        setUser(res.data);
      } catch {}
    };
    if (job?.user_id) {
      fetchUser(job.user_id);
    }
  }, [job?.user_id]);

  useEffect(() => {
    const fetchNovel = async (id: string) => {
      try {
        const res = await axios.get<Novel>(`/api/novel/${id}`);
        setNovel(res.data);
      } catch {}
    };
    if (job?.extra.novel_id) {
      fetchNovel(job.extra.novel_id);
    }
  }, [job?.extra.novel_id]);

  useEffect(() => {
    const fetchArtifact = async (id: string) => {
      try {
        const res = await axios.get<Artifact>(`/api/artifact/${id}`);
        setArtifact(res.data);
      } catch {}
    };
    if (job?.extra.artifact_id) {
      fetchArtifact(job?.extra.artifact_id);
    }
  }, [job?.extra.artifact_id]);

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

  if (!job) {
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
      {user && <UserDetailsCard user={user} />}
      {novel && <NovelDetailsCard novel={novel} />}
      {artifact && <ArtifactListCard artifacts={[artifact]} />}

      <JobListPage
        key={job.id}
        parentJobId={job.id}
        disableFilters
        autoRefresh={!job.is_done}
        hideIfEmpty
      />
    </Space>
  );
};
