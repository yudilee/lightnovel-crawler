import { ErrorState } from '@/components/Loading/ErrorState';
import { LoadingState } from '@/components/Loading/LoadingState';
import { Auth } from '@/store/_auth';
import type { LibrarySummary, Paginated } from '@/types';
import { stringifyError } from '@/utils/errors';
import { Divider, Flex, Pagination, Row, Typography, message } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { LibraryCard } from './LibraryCard';

const PAGE_SIZE = 18;

export const LibraryListPage: React.FC = () => {
  const navigate = useNavigate();
  const user = useSelector(Auth.select.user);
  const isAdmin = useSelector(Auth.select.isAdmin);
  const [messageApi, contextHolder] = message.useMessage();

  const [refresh, setRefresh] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [libraries, setLibraries] = useState<LibrarySummary[]>([]);

  useEffect(() => {
    const loadLibraries = async () => {
      setLoading(true);
      setError(undefined);
      try {
        const offset = (page - 1) * PAGE_SIZE;
        const shared = await axios.get<Paginated<LibrarySummary>>(
          isAdmin ? '/api/library/all' : '/api/library/public',
          {
            params: {
              offset,
              limit: PAGE_SIZE,
            },
          }
        );
        setLibraries(shared.data.items);
        setTotal(shared.data.total);
      } catch (err) {
        setError(stringifyError(err));
      } finally {
        setLoading(false);
      }
    };

    loadLibraries();
  }, [page, refresh, messageApi, isAdmin]);

  if (loading) {
    return <LoadingState message="Loading libraries..." />;
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
          {isAdmin ? 'All Libraries' : 'Public Libraries'}
        </Typography.Title>
      </Flex>

      <Divider size="small" style={{ marginBottom: 24 }} />

      <Row gutter={[16, 16]}>
        {libraries.map((item) => (
          <LibraryCard
            key={item.library.id}
            item={item}
            loading={loading}
            isOwner={item.owner.id === user!.id}
            onSelect={(id) => navigate(`/library/${id}`)}
          />
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
