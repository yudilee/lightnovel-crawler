import { AddToLibraryButton } from '@/components/Library/AddToLibraryButton';
import { ErrorState } from '@/components/Loading/ErrorState';
import { LoadingState } from '@/components/Loading/LoadingState';
import { Col, Divider, Empty, Flex, Pagination, Row, Typography } from 'antd';
import { useNovelList } from './hooks';
import { NovelFilterBox } from './NovelFilterBox';
import { NovelListItemCard } from './NovelListItemCard';

export const NovelListPage: React.FC<any> = () => {
  const {
    search: initialSearch,
    domain: initialDomain,
    currentPage,
    perPage,
    error,
    loading,
    total,
    novels,
    refresh,
    updateParams,
  } = useNovelList();

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <ErrorState
        error={error}
        title="Failed to load novel list"
        onRetry={refresh}
      />
    );
  }

  return (
    <>
      <Typography.Title level={2}>📚 All Novels</Typography.Title>

      <Divider size="small" />

      <NovelFilterBox
        search={initialSearch}
        domain={initialDomain}
        updateParams={updateParams}
      />

      <Divider size="small" />

      <Row gutter={[16, 16]}>
        {novels.map((novel) => (
          <Col key={novel.id} xs={8} lg={6} xl={4}>
            <div style={{ position: 'relative' }}>
              <div
                style={{ position: 'absolute', right: 4, top: 4, zIndex: 2 }}
                onClick={(e) => e.stopPropagation()}
              >
                <AddToLibraryButton
                  novelId={novel.id}
                  buttonText="Add"
                  buttonType="primary"
                  size="small"
                />
              </div>
              <NovelListItemCard novel={novel} />
            </div>
          </Col>
        ))}
      </Row>

      {!novels.length && (
        <Flex align="center" justify="center" style={{ height: '100%' }}>
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No novels" />
        </Flex>
      )}

      <Pagination
        current={currentPage}
        total={total}
        pageSize={perPage}
        showSizeChanger={false}
        onChange={(page) => updateParams({ page })}
        style={{ textAlign: 'center', marginTop: 32 }}
        hideOnSinglePage
      />
    </>
  );
};
