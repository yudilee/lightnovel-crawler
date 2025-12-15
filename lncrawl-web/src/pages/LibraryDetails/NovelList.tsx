import { Auth } from '@/store/_auth';
import type { Library, Novel, Paginated } from '@/types';
import {
  Button,
  Card,
  Col,
  Empty,
  Flex,
  Pagination,
  Result,
  Row,
  Space,
  Spin,
  Typography,
} from 'antd';
import axios from 'axios';
import { useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { NovelListItemCard } from '../NovelList/NovelListItemCard';
import { RemoveLibraryNovelButton } from './RemoveLibraryNovelButton';

const PAGE_SIZE = 12;

export const LibraryNovelList: React.FC<{
  library: Library;
}> = ({ library }) => {
  const user = useSelector(Auth.select.user);

  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState<boolean>(true);
  const [refresh, setRefresh] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [total, setTotal] = useState<number>(0);
  const [novels, setNovels] = useState<Novel[]>([]);

  const isOwner = useMemo(
    () => Boolean(user?.id === library.user_id),
    [user?.id, library.user_id]
  );

  useEffect(() => {
    setLoading(true);
    setError(undefined);
    const loadNovels = async () => {
      try {
        const { data } = await axios.get<Paginated<Novel>>(
          `/api/library/${library.id}/novels`,
          {
            params: {
              limit: PAGE_SIZE,
              offset: (page - 1) * PAGE_SIZE,
            },
          }
        );
        setTotal(data.total);
        setNovels(data.items || []);
      } catch (err: any) {
        setError(err?.message || 'Failed to load novels');
      } finally {
        setLoading(false);
      }
    };
    loadNovels();
  }, [library.id, refresh, page]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load novel list"
          subTitle={error}
          extra={[
            <Button onClick={() => setRefresh((v) => v + 1)}>Retry</Button>,
          ]}
        />
      </Flex>
    );
  }

  return (
    <Card
      title="📚 Novels"
      extra={
        <Typography.Text type="secondary">{total || 0} total</Typography.Text>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {novels.length ? (
          <Row gutter={[12, 12]}>
            {novels.map((novel) => (
              <Col key={novel.id} xs={12} sm={12} md={8} lg={6} xl={4}>
                <div style={{ position: 'relative' }}>
                  {isOwner && (
                    <RemoveLibraryNovelButton novel={novel} library={library} />
                  )}
                  <NovelListItemCard novel={novel} />
                </div>
              </Col>
            ))}
          </Row>
        ) : (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="No novels yet"
          />
        )}

        <Pagination
          current={page}
          total={total || 0}
          pageSize={PAGE_SIZE}
          onChange={(p) => setPage(p)}
          hideOnSinglePage
        />
      </Space>
    </Card>
  );
};
