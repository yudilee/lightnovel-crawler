import { stringifyError } from '@/utils/errors';
import { Button, Flex, Result } from 'antd';

interface ErrorStateProps {
  error: string | undefined;
  onRetry: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({ error, onRetry }) => {
  return (
    <Flex align="center" justify="center" style={{ height: '100%' }}>
      <Result
        status="error"
        title="Failed to load library details"
        subTitle={error}
        extra={[
          <Button key="retry" onClick={onRetry}>
            Retry
          </Button>,
        ]}
      />
    </Flex>
  );
};

