import './reader.scss';

import { Auth } from '@/store/_auth';
import { Reader } from '@/store/_reader';
import type { ReadChapter } from '@/types';
import { stringifyError } from '@/utils/errors';
import { formatFromNow } from '@/utils/time';
import { Button, Divider, Flex, Result, Spin, Typography } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import { ReaderNavBar } from './ReaderNavBar';

export const NovelReaderPage: React.FC<any> = () => {
  const { id } = useParams<{ id: string }>();
  const token = useSelector(Auth.select.authToken);

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [data, setData] = useState<ReadChapter>();

  const theme = useSelector(Reader.select.theme);
  const fontSize = useSelector(Reader.select.fontSize);
  const lineHeight = useSelector(Reader.select.lineHeight);
  const fontFamily = useSelector(Reader.select.fontFamily);

  useEffect(() => {
    const fetchChapter = async (id: string) => {
      setError(undefined);
      try {
        const { data: chapter } = await axios.get<ReadChapter>(
          `/api/chapter/${id}/read`
        );
        setData(chapter);
      } catch (err: any) {
        setError(stringifyError(err));
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchChapter(id);
    }
  }, [id, token, refreshId]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error || !data || !id) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
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

  return (
    <Flex
      vertical
      className="novel-reader"
      style={{ fontSize, lineHeight, fontFamily, ...theme }}
    >
      <div style={{ textAlign: 'center' }}>
        <Typography.Title level={4} style={{ margin: 0, color: '#F16C6F' }}>
          {data.novel.authors}
        </Typography.Title>
        <Typography.Title level={1} style={{ margin: 0 }}>
          <Link to={`/novel/${data.novel.id}`} style={{ color: '#8484F4' }}>
            {data.novel.title}
          </Link>
        </Typography.Title>
      </div>

      <Divider size="middle" />
      <ReaderNavBar data={data} />

      <h1 style={{ marginBottom: 0 }}>{data.chapter.title}</h1>
      <Typography.Text style={{ fontSize: 12, color: 'inherit', opacity: 0.8 }}>
        {data.chapter.serial} of {data.novel.chapter_count}
        <Divider type="vertical" style={{ background: theme.color }} />
        Updated {formatFromNow(data.chapter.updated_at)}
      </Typography.Text>

      {data.content && (
        <div
          dangerouslySetInnerHTML={{ __html: data.content }}
          style={{ margin: '25px 0' }}
        />
      )}

      <ReaderNavBar data={data} />
    </Flex>
  );
};
