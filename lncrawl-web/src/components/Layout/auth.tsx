import LncrawlImage from '@/assets/lncrawl.svg';
import { Avatar, Card, Flex, Layout, Space, Typography } from 'antd';
import { Outlet } from 'react-router-dom';

export const AuthLayout: React.FC<any> = () => {
  return (
    <Layout style={{ padding: '10px', height: '100vh' }}>
      <Layout.Content style={{ overflow: 'auto' }}>
        <Flex
          wrap
          align="center"
          justify="center"
          style={{ width: '100%', height: '100%' }}
        >
          <Card
            style={{ width: '500px' }}
            title={
              <Space
                align="center"
                direction="vertical"
                style={{ padding: '15px', width: '100%' }}
              >
                <Avatar
                  src={LncrawlImage}
                  style={{
                    width: '96px',
                    height: '96px',
                    borderRadius: 0,
                  }}
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
          >
            <Outlet />
          </Card>
        </Flex>
      </Layout.Content>
    </Layout>
  );
};
