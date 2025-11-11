import {
  Button,
  Divider,
  Empty,
  Flex,
  List,
  Pagination,
  Result,
  Spin,
} from 'antd';
import { useJobList } from './hooks';
import { JobFilterBox } from './JobFilterBox';
import { JobListItemCard } from './JobListItemCard';
import type { JSX } from 'react';

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
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (hideIfEmpty && !jobs?.length) {
    return null;
  }

  if (error) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load job list"
          subTitle={error}
          extra={[<Button onClick={refresh}>Retry</Button>]}
        />
      </Flex>
    );
  }

  return (
    <>
      {title}
      {!disableFilters && (
        <>
          <Divider size="small" />
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
      {(jobs.length > 0 || currentPage > 1) && total / perPage > 1 ? (
        <Pagination
          current={currentPage}
          total={total}
          pageSize={perPage}
          showSizeChanger={false}
          onChange={(page) => updateParams({ page })}
          style={{ textAlign: 'center', marginTop: 32 }}
        />
      ) : null}
    </>
  );
};
