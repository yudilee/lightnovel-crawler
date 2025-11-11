import '@fontsource/arbutus-slab/400.css';
import '@fontsource/roboto-slab/400.css';
import './reader.scss';

import { Auth } from '@/store/_auth';
import type { ReadChapter } from '@/types';
import { stringifyError } from '@/utils/errors';
import { formatFromNow } from '@/utils/time';
import { LeftOutlined, RightOutlined } from '@ant-design/icons';
import { Button, Divider, Flex, Grid, Result, Spin, Typography } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { Link, useNavigate, useParams } from 'react-router-dom';

export const NovelReaderPage: React.FC<any> = () => {
  const { id } = useParams<{ id: string }>();
  const token = useSelector(Auth.select.authToken);

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [data, setData] = useState<ReadChapter>();

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
    <Flex vertical>
      <Flex
        vertical
        wrap
        align="center"
        gap={5}
        style={{ textAlign: 'center' }}
      >
        <Typography.Text type="success">{data.novel.authors}</Typography.Text>
        <Typography.Title level={3} style={{ margin: 0 }}>
          <Link to={`/novel/${data.novel.id}`}>{data.novel.title}</Link>
        </Typography.Title>
        <Typography.Title level={4} type="secondary" style={{ margin: 0 }}>
          {data.chapter.title}
        </Typography.Title>
        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
          Updated {formatFromNow(data.chapter.updated_at)}
        </Typography.Text>
      </Flex>

      <Divider size="small" />
      <NavigationButtons data={data} />
      <Divider size="small" />

      {data.content && (
        <div
          className="novel-content-reader"
          dangerouslySetInnerHTML={{ __html: data.content }}
        />
      )}

      <Divider size="small" />
      <NavigationButtons data={data} />
      <Divider size="small" />
    </Flex>
  );
};

export const NavigationButtons: React.FC<{
  data: ReadChapter;
}> = ({ data }) => {
  const { sm } = Grid.useBreakpoint();
  const navigate = useNavigate();
  return (
    <Flex align="center" justify="space-between">
      <Button
        disabled={!data.previous_id}
        onClick={() => navigate(`/read/${data.previous_id}`)}
      >
        <LeftOutlined />
        {sm && ' Previous'}
      </Button>

      <Typography.Text type="secondary">
        {data.chapter.serial} of {data.novel.chapter_count}
      </Typography.Text>

      <Button
        disabled={!data.next_id}
        onClick={() => navigate(`/read/${data.next_id}`)}
      >
        {sm && 'Next '}
        <RightOutlined />
      </Button>
    </Flex>
  );
};
