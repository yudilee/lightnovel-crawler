import { Divider, Flex, Result, Typography } from 'antd';
import { JobListPage } from '../JobList';
import { UserDetailSection } from './UserDetailSection';
import { useParams } from 'react-router-dom';
import { DeploymentUnitOutlined } from '@ant-design/icons';

export const UserDetailsPage: React.FC<any> = () => {
  const { id } = useParams<{ id: string }>();

  if (!id) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result status="error" title="ID parameter is missing" />
      </Flex>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <UserDetailSection userId={id} />

      <Divider size="large" />

      <JobListPage
        userId={id}
        autoRefresh
        title={
          <>
            <Divider style={{ margin: 0 }} />
            <Typography.Title level={3}>
              <DeploymentUnitOutlined /> User Requests
            </Typography.Title>
          </>
        }
      />
    </div>
  );
};
