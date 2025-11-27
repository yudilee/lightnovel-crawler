import './fonts.css';
import './index.scss';

import { store } from '@/store';
import { Auth } from '@/store/_auth';
import { Reader } from '@/store/_reader';
import { type Job, type ReadChapter } from '@/types';
import { stringifyError } from '@/utils/errors';
import { formatFromNow } from '@/utils/time';
import { Button, Flex, Result, Spin } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import { JobDetailsCard } from '../JobDetails/JobDetailsCard';
import { ReaderVerticalLayout } from './ReaderLayoutVertical';

const fetchJobs = new Map<string, Promise<Job>>();
const cache = new Map<string, Promise<ReadChapter>>();

async function fetchChapter(id: string) {
  const { data } = await axios.get<ReadChapter>(`/api/chapter/${id}/read`);
  if (data.content) {
    data.content = `
      <h1 style="margin-bottom: 0">${data.chapter.title}</h1>
      <div style="font-size: 12px; opacity: 0.8; margin-bottom: 25px">
        ${data.chapter.serial} of ${data.novel.chapter_count}
        <span> | </span>
        Updated ${formatFromNow(data.chapter.updated_at)}
      </div>
      ${data.content}
    `;
  }
  return data;
}

function fetchChapterCached(id: string): Promise<ReadChapter> {
  if (!cache.has(id)) {
    cache.set(id, fetchChapter(id));
  }
  return cache.get(id)!;
}

function createFetchJob(id: string) {
  if (!fetchJobs.has(id)) {
    const promise = axios
      .get<Job>(`/api/chapter/${id}/fetch`)
      .then((res) => res.data);
    fetchJobs.set(id, promise);
  }
  return fetchJobs.get(id)!;
}

export const NovelReaderPage: React.FC<any> = () => {
  const { id } = useParams<{ id: string }>();
  const token = useSelector(Auth.select.authToken);
  const autoFetch = useSelector(Reader.select.autoFetch);

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [data, setData] = useState<ReadChapter>();
  const [job, setJob] = useState<Job>();

  // get chapter content data
  useEffect(() => {
    setJob(undefined);
    setData(undefined);
    setError(undefined);
    if (id) {
      setLoading(true);
      fetchChapterCached(id)
        .then(setData)
        .catch((err) => setError(stringifyError(err)))
        .finally(() => setLoading(false));
    }
  }, [id, token, refreshId]);

  // get job details if auto fetch is enabled
  useEffect(() => {
    if (autoFetch && data && !data.chapter.is_done) {
      setLoading(true);
      createFetchJob(data.chapter.id)
        .then(setJob)
        .catch(console.error)
        .finally(() => setLoading(false));
    } else {
      setJob(undefined);
    }
  }, [autoFetch, data]);

  // auto refresh job status
  useEffect(() => {
    if (!job || !data || data.chapter.is_done) {
      return;
    }
    if (job.is_done) {
      cache.delete(data.chapter.id);
      setRefreshId((v) => v + 1);
    } else {
      const iid = setInterval(() => {
        axios
          .get<Job>(`/api/job/${job.id}`)
          .then((res) => setJob(res.data))
          .catch(console.error);
      }, 1000);
      return () => clearInterval(iid);
    }
  }, [data, job]);

  // preload next chapter
  useEffect(() => {
    if (data?.next_id) {
      fetchChapterCached(data.next_id).then((next) => {
        if (autoFetch && !next.chapter.is_done) {
          createFetchJob(next.chapter.id);
        }
      });
    }
  }, [data?.next_id, autoFetch]);

  // preload previous chapter
  useEffect(() => {
    if (data?.previous_id) {
      fetchChapterCached(data.previous_id).then((prev) => {
        if (autoFetch && !prev.chapter.is_done) {
          createFetchJob(prev.chapter.id);
        }
      });
    }
  }, [data?.previous_id, autoFetch]);

  useEffect(() => {
    if (!loading) {
      store.dispatch(Reader.action.setSepakPosition(0));
      if (!data?.content) {
        store.dispatch(Reader.action.setSpeaking(false));
      }
    }
    const fid = requestAnimationFrame(() => {
      const mainEl = document.querySelector('main');
      if (mainEl) {
        mainEl.scrollTop = 0;
      }
    });
    return () => cancelAnimationFrame(fid);
  }, [loading, data?.content]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100vh' }}>
        <Spin size="large" style={{ margin: '50px 0' }} />
      </Flex>
    );
  }

  if (job && !job.is_done) {
    return (
      <Flex
        vertical
        gap={15}
        align="center"
        justify="center"
        style={{ height: '100vh' }}
      >
        <JobDetailsCard job={job} />
        <Button href={`/job/${job.id}`}>View Request</Button>
      </Flex>
    );
  }

  if (error || !data || !id) {
    return (
      <Flex align="center" justify="center" style={{ height: '100vh' }}>
        <Result
          status="404"
          title="Failed to load chapter content"
          subTitle={error}
          extra={[
            <Button onClick={() => setRefreshId((v) => v + 1)}>Retry</Button>,
          ]}
        />
      </Flex>
    );
  }

  return <ReaderVerticalLayout key={id} data={data} />;
};
