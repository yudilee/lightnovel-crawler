import { Flex, Spin, Typography } from 'antd';

export const LoadingState: React.FC<{ message?: string }> = ({ message }) => {
  return (
    <Flex align="center" justify="center" style={{ height: '100%' }}>
      <Spin size="large" style={{ marginTop: 100 }}>
        {message && (
          <Typography.Text type="secondary">{message}</Typography.Text>
        )}
      </Spin>
    </Flex>
  );
};
