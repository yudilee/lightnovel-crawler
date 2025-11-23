import './fonts.scss';
import './index.scss';

import { store } from '@/store';
import { Auth } from '@/store/_auth';
import { Reader } from '@/store/_reader';
import type { ReadChapter } from '@/types';
import { stringifyError } from '@/utils/errors';
import { formatFromNow } from '@/utils/time';
import { Button, Flex, Result, Spin } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import { ReaderVerticalLayout } from './ReaderLayoutVertical';

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

export const NovelReaderPage: React.FC<any> = () => {
  const { id } = useParams<{ id: string }>();
  const token = useSelector(Auth.select.authToken);

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [data, setData] = useState<ReadChapter>();

  useEffect(() => {
    if (id) {
      setError(undefined);
      fetchChapterCached(id)
        .then(setData)
        .catch((err) => setError(stringifyError(err)))
        .finally(() => setLoading(false));
    }
  }, [id, token, refreshId]);

  useEffect(() => {
    if (data?.next_id) {
      fetchChapterCached(data.next_id);
    }
  }, [data?.next_id]);

  useEffect(() => {
    if (data?.previous_id) {
      fetchChapterCached(data.previous_id);
    }
  }, [data?.previous_id]);

  useEffect(() => {
    store.dispatch(Reader.action.setSepakPosition(0));
    const fid = requestAnimationFrame(() => {
      const mainEl = document.querySelector('main');
      if (mainEl) {
        mainEl.scrollTop = 0;
      }
    });
    return () => cancelAnimationFrame(fid);
  }, [data]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100vh' }}>
        <Spin size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error || !data || !id) {
    return (
      <Flex align="center" justify="center" style={{ height: '100vh' }}>
        <Result
          status="error"
          title="Failed to load chapter content"
          subTitle={error}
          extra={[
            <Button onClick={() => setRefreshId((v) => v + 1)}>Retry</Button>,
          ]}
        />
      </Flex>
    );
  }

  return <ReaderVerticalLayout data={data} />;
};
