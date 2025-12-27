import { ErrorState } from '@/components/Loading/ErrorState';
import { LoadingState } from '@/components/Loading/LoadingState';
import { TeamOutlined } from '@ant-design/icons';
import { Divider, Flex, Input, List, Pagination, Typography } from 'antd';
import { useUserList } from './hooks';
import { UserListItemCard } from './UserListItemCard';

export const UserListPage: React.FC<any> = () => {
  const {
    search: initialSearch,
    perPage,
    currentPage,
    error,
    loading,
    total,
    users,
    refresh,
    updateParams,
  } = useUserList();

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
      <Typography.Title level={2}>
        <TeamOutlined /> Users
      </Typography.Title>

      <Divider size="small" />

      <Flex align="center">
        <Input.Search
          defaultValue={initialSearch}
          onSearch={(search) => updateParams({ search, page: 1 })}
          placeholder="Find users"
          allowClear
          size="large"
        />
      </Flex>

      <Divider size="small" />

      <Typography.Text
        italic
        type="secondary"
        style={{ display: 'block', marginBottom: 5 }}
      >
        Found {total} users
      </Typography.Text>

      <List
        itemLayout="horizontal"
        dataSource={users}
        renderItem={(user) => (
          <UserListItemCard user={user} onChange={refresh} />
        )}
      />

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

export default UserListPage;
