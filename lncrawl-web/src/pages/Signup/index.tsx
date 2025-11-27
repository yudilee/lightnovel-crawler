import { store } from '@/store';
import { Auth } from '@/store/_auth';
import { stringifyError } from '@/utils/errors';
import { LeftOutlined, LoginOutlined } from '@ant-design/icons';
import { Alert, Button, Divider, Flex, Form, Input, Typography } from 'antd';
import FormItem from 'antd/es/form/FormItem';
import axios from 'axios';
import { useState } from 'react';

export const SignupPage: React.FC<any> = () => {
  const [form] = Form.useForm();
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState<boolean>(false);

  const handleSignup = async (data: any) => {
    setLoading(true);
    setError(undefined);
    try {
      const result = await axios.post(`/api/auth/signup`, data);
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
      onFinish={handleSignup}
      size="large"
      layout="vertical"
      labelCol={{ style: { padding: 0 } }}
    >
      <Form.Item
        name="name"
        label="Full Name"
        rules={[
          {
            validator: (_, value) =>
              value && value.trim().length >= 2
                ? Promise.resolve()
                : Promise.reject('Please enter a valid name'),
          },
        ]}
      >
        <Input placeholder="Enter full name" autoComplete="name" />
      </Form.Item>

      <Form.Item
        name="email"
        label="Email"
        rules={[
          { required: true, message: 'Please enter your email' },
          { type: 'email', message: 'Please enter a valid email' },
        ]}
      >
        <Input placeholder="Enter email" autoComplete="new-user" />
      </Form.Item>

      <Form.Item
        name={'password'}
        label="Password"
        rules={[
          { required: true, message: 'Please enter a password' },
          { min: 6, message: 'Password must be at least 6 characters' },
        ]}
        hasFeedback
      >
        <Input.Password
          placeholder="New password"
          autoComplete="new-password"
        />
      </Form.Item>

      <Form.Item
        name="referrer"
        label="Referrer Token"
        rules={[{ required: true, message: 'Please enter a referrer token' }]}
      >
        <Input
          placeholder="Enter referrer token"
          autoComplete="referrer-token"
        />
      </Form.Item>

      <Typography.Text type="secondary" style={{ fontSize: 12 }}>
        Registration is now referral-only. If you want to refer someone, you can
        find your referral token on your Profile page.
      </Typography.Text>

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
          children={'Register'}
        />
      </FormItem>

      <Divider />
      <Flex justify="center">
        <Typography.Link href="/login">
          <LeftOutlined /> Back to login
        </Typography.Link>
      </Flex>
    </Form>
  );
};
