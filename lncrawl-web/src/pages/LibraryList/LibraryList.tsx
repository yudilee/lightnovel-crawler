import { ErrorState } from '@/components/Loading/ErrorState';
import { LoadingState } from '@/components/Loading/LoadingState';
import type { Library, Paginated } from '@/types';
import { stringifyError } from '@/utils/errors';
import {
  Col,
  Divider,
  Empty,
  Pagination,
  Row,
  Typography,
  message,
} from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { LibraryCard } from './LibraryCard';

const PAGE_SIZE = 12;

export const LibraryList: React.FC<{
  type: 'public' | 'my' | 'all';
  refreshId: number;
  updateRefresh: () => void;
}> = ({ type, refreshId, updateRefresh }) => {
  const [messageApi, contextHolder] = message.useMessage();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [libraries, setLibraries] = useState<Library[]>([]);

  useEffect(() => {
    const loadLibraries = async () => {
      setLoading(true);
      setError(undefined);
      try {
        const offset = (page - 1) * PAGE_SIZE;
        const { data } = await axios.get<Paginated<Library>>(
          `/api/library/${type}`,
          {
            params: {
              offset,
              limit: PAGE_SIZE,
            },
          }
        );
        setLibraries(data.items);
        setTotal(data.total);
      } catch (err) {
        setError(stringifyError(err));
      } finally {
        setLoading(false);
      }
    };

    loadLibraries();
  }, [page, refreshId, messageApi, type]);

  return (
    <>
      {contextHolder}

      {type !== 'all' && (
        <Typography.Title
          level={4}
          style={{ color: type === 'public' ? '#0f0' : '#39f' }}
        >
          {type === 'public' ? 'Public Libraries' : 'My Libraries'}
        </Typography.Title>
      )}

      <Divider size="small" style={{ marginBottom: 24 }} />

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState
          error={error}
          onRetry={updateRefresh}
          title="Failed to load libraries"
        />
      ) : (
        <Row gutter={[16, 16]}>
          {libraries.map((library) => (
            <LibraryCard key={library.id} library={library} />
          ))}
          {libraries.length === 0 && (
            <Col span={24}>
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="No libraries available"
              />
            </Col>
          )}
        </Row>
      )}

      <Pagination
        current={page}
        total={total}
        pageSize={PAGE_SIZE}
        showSizeChanger={false}
        onChange={setPage}
        hideOnSinglePage
      />
    </>
  );
};
