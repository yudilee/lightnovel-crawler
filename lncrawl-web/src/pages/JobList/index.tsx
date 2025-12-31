import { ErrorState } from '@/components/Loading/ErrorState';
import { LoadingState } from '@/components/Loading/LoadingState';
import { Divider, Empty, List, Pagination } from 'antd';
import type { JSX } from 'react';
import { useJobList } from './hooks';
import { JobFilterBox } from './JobFilterBox';
import { JobListItemCard } from './JobListItemCard';

export const JobListPage: React.FC<{
  title?: JSX.Element;
  userId?: string;
  parentJobId?: string;
  disableFilters?: boolean;
  autoRefresh?: boolean;
  hideIfEmpty?: boolean;
}> = ({
  title,
  userId,
  hideIfEmpty,
  autoRefresh,
  parentJobId,
  disableFilters,
}) => {
  const {
    currentPage,
    error,
    loading,
    perPage,
    total,
    jobs,
    status,
    type,
    refresh,
    updateParams,
  } = useJobList(autoRefresh, userId, parentJobId);

  if (loading) {
    return <LoadingState />;
  }

  if (
    hideIfEmpty &&
    !jobs?.length &&
    status === undefined &&
    type === undefined
  ) {
    return null;
  }

  if (error) {
    return (
      <ErrorState
        error={error}
        title="Failed to load job list"
        onRetry={refresh}
      />
    );
  }

  return (
    <>
      {title}
      {title && <Divider size="small" />}
      {!disableFilters && (
        <>
          <JobFilterBox
            status={status}
            type={type}
            updateParams={updateParams}
          />
          <Divider size="small" />
        </>
      )}
      {jobs.length > 0 ? (
        <List
          itemLayout="horizontal"
          dataSource={jobs}
          renderItem={(job) => <JobListItemCard job={job} onChange={refresh} />}
        />
      ) : (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="No available requests"
        />
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
