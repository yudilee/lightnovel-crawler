import { ErrorState } from '@/components/Loading/ErrorState';
import { DeploymentUnitOutlined, LeftOutlined } from '@ant-design/icons';
import { Divider, Typography } from 'antd';
import { Link, useParams } from 'react-router-dom';
import { JobListPage } from '../JobList';
import { UserDetailSection } from './UserDetailSection';

export const UserDetailsPage: React.FC<any> = () => {
  const { id } = useParams<{ id: string }>();

  if (!id) {
    return <ErrorState title="ID parameter is missing" />;
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Link to={'/users'}>
        <LeftOutlined /> All Users
      </Link>

      <UserDetailSection userId={id} />

      <Divider size="large" />

      <JobListPage
        userId={id}
        autoRefresh
        title={
          <Typography.Title level={3}>
            <DeploymentUnitOutlined /> User Requests
          </Typography.Title>
        }
      />
    </div>
  );
};
