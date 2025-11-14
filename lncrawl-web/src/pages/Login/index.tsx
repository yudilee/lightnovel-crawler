import { store } from '@/store';
import { Auth } from '@/store/_auth';
import { stringifyError } from '@/utils/errors';
import { LoginOutlined } from '@ant-design/icons';
import { Alert, Button, Divider, Flex, Form, Input, Typography } from 'antd';
import FormItem from 'antd/es/form/FormItem';
import axios from 'axios';
import { useState } from 'react';

export const LoginPage: React.FC<any> = () => {
  const [form] = Form.useForm();
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState<boolean>(false);

  const handleLogin = async (data: any) => {
    setLoading(true);
    setError(undefined);
    try {
      const result = await axios.post(`/api/auth/login`, data);
      store.dispatch(Auth.action.setAuth(result.data));
    } catch (err) {
      setError(stringifyError(err, 'Oops! Something went wrong.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form
      form={form}
      onFinish={handleLogin}
      size="large"
      layout="vertical"
      labelCol={{ style: { padding: 0 } }}
    >
      <Form.Item name="email" label="Email" rules={[{ required: true }]}>
        <Input placeholder="Enter email" autoComplete="current-user" />
      </Form.Item>
      <Form.Item
        name={'password'}
        label="Password"
        rules={[{ required: true }]}
      >
        <Input.Password
          placeholder="Enter password"
          autoComplete="current-password"
        />
      </Form.Item>

      <Flex justify="end">
        <Typography.Link href="/forgot-password">
          Forgot password?
        </Typography.Link>
      </Flex>

      {Boolean(error) && (
        <Alert
          type="warning"
          showIcon
          message={error}
          closable
          onClose={() => setError('')}
        />
      )}

      <FormItem style={{ marginTop: '20px' }}>
        <Button
          block
          type="primary"
          htmlType="submit"
          loading={loading}
          disabled={loading}
          icon={<LoginOutlined />}
          children={'Login'}
        />
      </FormItem>

      <Divider />
      <Flex justify="center">
        <Typography.Link href="/signup">Create new account</Typography.Link>
      </Flex>
    </Form>
  );
};
