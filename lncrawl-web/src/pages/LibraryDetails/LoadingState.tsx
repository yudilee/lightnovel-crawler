import { Flex, Spin } from 'antd';

export const LoadingState: React.FC = () => {
  return (
    <Flex align="center" justify="center" style={{ height: '100%' }}>
      <Spin size="large" style={{ marginTop: 100 }} />
    </Flex>
  );
};

