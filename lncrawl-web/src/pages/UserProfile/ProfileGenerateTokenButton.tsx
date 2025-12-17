import { stringifyError } from '@/utils/errors';
import { SafetyCertificateOutlined } from '@ant-design/icons';
import { Button, Flex, Typography, message } from 'antd';
import axios from 'axios';
import { useCallback, useEffect, useState } from 'react';

export const ProfileGenerateTokenButton: React.FC<any> = () => {
  const [messageApi, contextHolder] = message.useMessage();

  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState<string>();

  const generateToken = useCallback(async () => {
    try {
      setLoading(true);
      const result = await axios.post<{ token: string }>(
        '/api/auth/me/create-token'
      );
      setToken(result.data.token);
    } catch (err) {
      console.error(err);
      messageApi.error(stringifyError(err));
    } finally {
      setLoading(false);
    }
  }, [messageApi]);

  useEffect(() => {
    if (loading || token) return;
    const tid = setTimeout(generateToken, 100);
    return () => clearTimeout(tid);
  }, [loading, token, generateToken]);

  return (
    <Flex justify="space-between" align="center" gap={'10'} wrap>
      {contextHolder}

      {token && (
        <Flex vertical>
          <Typography.Text
            copyable
            style={{ fontSize: 16, fontFamily: 'monospace' }}
          >
            {token}
          </Typography.Text>

          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            This token is only valid for a limited period time
          </Typography.Text>
        </Flex>
      )}

      <Button
        loading={loading}
        onClick={generateToken}
        icon={<SafetyCertificateOutlined />}
      >
        Generate Token
      </Button>
    </Flex>
  );
};
