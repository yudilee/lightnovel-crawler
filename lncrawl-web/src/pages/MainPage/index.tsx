import { Divider, Typography } from 'antd';
import { JobListPage } from '../JobList';
import { RequestNovelCard } from '../JobList/RequestNovelCard';
import { DeploymentUnitOutlined } from '@ant-design/icons';
import { useSelector } from 'react-redux';
import { Auth } from '@/store/_auth';

export const MainPage: React.FC<any> = () => {
  const isAdmin = useSelector(Auth.select.isAdmin);
  return (
    <>
      <RequestNovelCard />

      <Divider />

      <JobListPage
        autoRefresh
        title={
          <Typography.Title level={2}>
            <DeploymentUnitOutlined /> {isAdmin ? 'All' : 'My'} Requests
            {isAdmin && (
              <Typography.Text type="secondary" style={{ display: 'block' }}>
                Check user profile page for user specific requests
              </Typography.Text>
            )}
          </Typography.Title>
        }
      />
    </>
  );
};
