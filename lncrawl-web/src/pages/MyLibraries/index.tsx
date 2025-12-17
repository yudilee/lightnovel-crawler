import { ErrorState } from '@/components/Loading/ErrorState';
import { LoadingState } from '@/components/Loading/LoadingState';
import type { Library, Paginated } from '@/types';
import { stringifyError } from '@/utils/errors';
import { Divider, Flex, message, Pagination, Row, Typography } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { LibraryCard } from '../LibraryList/LibraryCard';
import { CreateLibraryButton } from './CreateLibraryButton';

const PAGE_SIZE = 18;

export const MyLibrariesPage: React.FC = () => {
  const [messageApi, contextHolder] = message.useMessage();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [refresh, setRefresh] = useState(0);
  const [libraries, setLibraries] = useState<Library[]>([]);

  useEffect(() => {
    const loadLibraries = async () => {
      setLoading(true);
      setError(undefined);
      try {
        const offset = (page - 1) * PAGE_SIZE;
        const { data } = await axios.get<Paginated<Library>>(
          '/api/library/my',
          {
            params: {
              offset,
              limit: PAGE_SIZE,
            },
          }
        );
        setTotal(data.total);
        setLibraries(data.items);
      } catch (err) {
        setError(stringifyError(err));
      } finally {
        setLoading(false);
      }
    };
    loadLibraries();
  }, [page, refresh, messageApi]);

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <ErrorState
        error={error}
        title="Failed to load libraries"
        onRetry={() => setRefresh((v) => v + 1)}
      />
    );
  }

  return (
    <>
      {contextHolder}

      <Flex justify="space-between" align="center" wrap>
        <Typography.Title level={2} style={{ margin: 0 }}>
          My Libraries
        </Typography.Title>
        <CreateLibraryButton />
      </Flex>

      <Divider size="small" style={{ marginBottom: 24 }} />

      <Row gutter={[16, 16]}>
        {libraries.map((item) => (
          <LibraryCard key={item.id} library={item} />
        ))}
      </Row>

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
