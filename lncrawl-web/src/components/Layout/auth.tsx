import { Avatar, Card, Flex, Layout, Space, Typography } from 'antd';
import { Outlet } from 'react-router-dom';

export const AuthLayout: React.FC<any> = () => {
  return (
    <Layout
      style={{
        padding: '10px',
        overflow: 'hidden',
        height: 'calc(100vh - 40px)',
      }}
    >
      <Layout.Content style={{ overflow: 'auto' }}>
        <Flex
          align="center"
          justify="center"
          style={{ width: '100%', height: '100%' }}
        >
          <Card
            title={
              <Space
                direction="vertical"
                align="center"
                style={{ padding: '15px', width: '100%' }}
              >
                <Avatar
                  src="/lncrawl.svg"
                  style={{ width: '96px', height: '96px' }}
                />
                <Typography.Title
                  type="success"
                  level={3}
                  style={{ margin: 0 }}
                >
                  Lightnovel Crawler
                </Typography.Title>
              </Space>
            }
            style={{ width: '400px' }}
          >
            <Outlet />
          </Card>
        </Flex>
      </Layout.Content>
    </Layout>
  );
};
