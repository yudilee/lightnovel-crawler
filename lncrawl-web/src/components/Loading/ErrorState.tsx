import { Button, Flex, Result } from 'antd';

export const ErrorState: React.FC<{
  title: string;
  error?: string;
  onRetry?: () => void;
}> = ({ title, error, onRetry }) => {
  return (
    <Flex align="center" justify="center" style={{ height: '100%' }}>
      <Result
        status="error"
        title={title}
        subTitle={error || 'An error occurred while loading the data.'}
        extra={
          onRetry
            ? [
                <Button key="retry" onClick={onRetry}>
                  Retry
                </Button>,
              ]
            : undefined
        }
      />
    </Flex>
  );
};
