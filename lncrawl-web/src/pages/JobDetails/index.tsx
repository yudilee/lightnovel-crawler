import { ArtifactListCard } from '@/components/ArtifactList/ArtifactListCard';
import {
  type Artifact,
  type Chapter,
  type Job,
  type Novel,
  type User,
  type Volume,
} from '@/types';
import { stringifyError } from '@/utils/errors';
import { DeploymentUnitOutlined, LeftOutlined } from '@ant-design/icons';
import {
  Button,
  Divider,
  Flex,
  Grid,
  Result,
  Space,
  Spin,
  Typography,
} from 'antd';
import axios from 'axios';
import { LRUCache } from 'lru-cache';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { JobListPage } from '../JobList';
import { NovelDetailsCard } from '../NovelDetails/NovelDetailsCard';
import { ChapterDetailsCard } from '../NovelDetails/ChapterDetailsCard';
import { JobDetailsCard } from './JobDetailsCard';
import { UserDetailsCard } from './UserDetailsCard';
import { VolumeDetailsCard } from '../NovelDetails/VolumeDetailsCard';

const _cache = new LRUCache<string, any>({
  max: 1000,
  ttl: 30000,
});

async function handleFetch<T>(
  name: string,
  id: string | null | undefined,
  setValue: (value: T | undefined) => any
) {
  if (!id) {
    setValue(undefined);
    return;
  }
  const url = `/api/${name}/${id}`;
  if (!_cache.has(url)) {
    try {
      const res = await axios.get<T>(url);
      _cache.set(url, res.data);
    } catch {
      _cache.set(url, undefined);
    }
  }
  setValue(_cache.get(url));
}

export const JobDetailsPage: React.FC<any> = () => {
  const { lg } = Grid.useBreakpoint();
  const { id } = useParams<{ id: string }>();

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const [job, setJob] = useState<Job>();
  const [user, setUser] = useState<User | undefined>();
  const [novel, setNovel] = useState<Novel | undefined>();
  const [volume, setVolume] = useState<Volume | undefined>();
  const [chapter, setChapter] = useState<Chapter | undefined>();
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
    handleFetch('user', job?.user_id, setUser);
  }, [job?.user_id]);

  useEffect(() => {
    handleFetch('novel', job?.extra.novel_id, setNovel);
  }, [job?.extra.novel_id]);

  useEffect(() => {
    handleFetch('volume', job?.extra.volume_id, setVolume);
  }, [job?.extra.volume_id]);

  useEffect(() => {
    handleFetch('chapter', job?.extra.chapter_id, setChapter);
  }, [job?.extra.chapter_id]);

  useEffect(() => {
    handleFetch('artifact', job?.extra.artifact_id, setArtifact);
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
      {job.parent_job_id && (
        <Link to={`/job/${job.parent_job_id}`}>
          <LeftOutlined /> Parent Request
        </Link>
      )}

      <JobDetailsCard job={job} />
      {user && <UserDetailsCard user={user} />}
      {novel && <NovelDetailsCard novel={novel} withPageLink />}
      {volume && <VolumeDetailsCard volume={volume} hideChapters />}
      {chapter && <ChapterDetailsCard chapter={chapter} />}
      {artifact && <ArtifactListCard artifacts={[artifact]} />}

      <JobListPage
        key={job.id}
        parentJobId={job.id}
        disableFilters
        autoRefresh={!job.is_done}
        hideIfEmpty
        title={
          <>
            <Divider style={{ margin: 0 }} />
            <Typography.Title level={3}>
              <DeploymentUnitOutlined /> Linked Requests
            </Typography.Title>
          </>
        }
      />
    </Space>
  );
};
