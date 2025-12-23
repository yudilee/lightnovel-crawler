import { FeedbackButton } from '@/pages/FeedbackList/FeedbackButton';
import { ErrorState } from '@/components/Loading/ErrorState';
import { LoadingState } from '@/components/Loading/LoadingState';
import { FeedbackStatusLabels } from '@/components/Tags/FeedbackStatusTag';
import { FeedbackTypeLabels } from '@/components/Tags/FeedbackTypeTag';
import { CommentOutlined } from '@ant-design/icons';
import { Divider, Flex, Input, Pagination, Select, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';
import { FeedbackListItemCard } from './FeedbackListItemCard';
import { useFeedbackList } from './hooks';

export const FeedbackListPage: React.FC<any> = () => {
  const navigate = useNavigate();
  const {
    search: initialSearch,
    status: initialStatus,
    type: initialType,
    perPage,
    currentPage,
    error,
    loading,
    total,
    feedbackList,
    refresh,
    updateParams,
  } = useFeedbackList();

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <ErrorState
        error={error}
        title="Failed to load feedback list"
        onRetry={refresh}
      />
    );
  }

  return (
    <>
      <Flex justify="space-between" align="center">
        <Typography.Title level={2} style={{ margin: 0 }}>
          <CommentOutlined style={{ color: '#0ca3f2' }} /> Feedback
        </Typography.Title>
        <FeedbackButton onSubmit={refresh} />
      </Flex>

      <Divider size="small" />

      <Flex align="center" gap="middle" wrap>
        <Input.Search
          defaultValue={initialSearch}
          onSearch={(search) => updateParams({ search, page: 1 })}
          placeholder="Search feedback"
          allowClear
          size="large"
          style={{ flex: 1, minWidth: 200 }}
        />
        <Select
          placeholder="Filter by type"
          allowClear
          size="large"
          style={{ width: 150 }}
          value={initialType}
          onChange={(type) => updateParams({ type, page: 1 })}
          options={Object.entries(FeedbackTypeLabels).map(([value, label]) => ({
            value,
            label,
          }))}
        />
        <Select
          placeholder="Filter by status"
          allowClear
          size="large"
          style={{ width: 150 }}
          value={initialStatus}
          onChange={(status) => updateParams({ status, page: 1 })}
          options={Object.entries(FeedbackStatusLabels).map(
            ([value, label]) => ({ value, label })
          )}
        />
      </Flex>

      <Divider size="small" />

      <div>
        {feedbackList.map((feedback) => (
          <FeedbackListItemCard
            key={feedback.id}
            feedback={feedback}
            onClick={() => navigate(`/feedback/${feedback.id}`)}
          />
        ))}
      </div>

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

export default FeedbackListPage;
