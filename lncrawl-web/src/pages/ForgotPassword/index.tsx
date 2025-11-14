import { stringifyError } from '@/utils/errors';
import { LeftOutlined } from '@ant-design/icons';
import { Alert, Button, Divider, Flex, Form, Input, Typography } from 'antd';
import FormItem from 'antd/es/form/FormItem';
import axios from 'axios';
import { useState } from 'react';

export const ForgotPasswordPage: React.FC<any> = () => {
  const [form] = Form.useForm();
  const [error, setError] = useState<string>();
  const [success, setSuccess] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const sendResetLink = async (data: any) => {
    if (success) return;
    setLoading(true);
    setSuccess(false);
    setError(undefined);
    try {
      await axios.post(`/api/auth/send-password-reset-link`, data);
      setSuccess(true);
    } catch (err) {
      setError(stringifyError(err, 'Oops! Something went wrong.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form
      form={form}
      onFinish={sendResetLink}
      size="large"
      layout="vertical"
      labelCol={{ style: { padding: 0 } }}
    >
      <Form.Item
        name="email"
        label="Email"
        rules={[
          { required: true, message: 'Please enter your email' },
          { type: 'email', message: 'Please enter a valid email' },
        ]}
      >
        <Input
          placeholder="Enter email"
          autoComplete="current-user"
          disabled={success}
        />
      </Form.Item>

      {error ? (
        <Alert
          type="warning"
          showIcon
          message={error}
          closable
          onClose={() => setError('')}
        />
      ) : success ? (
        <Alert type="success" showIcon message={'Please check your email'} />
      ) : null}

      {!success ? (
        <FormItem style={{ marginTop: '20px' }}>
          <Button
            block
            type="primary"
            htmlType="submit"
            loading={loading}
            disabled={loading}
            children={'Send Reset Link'}
          />
        </FormItem>
      ) : (
        <Flex justify="center" style={{ marginTop: 20 }}>
          <Typography.Link href="/forgot-password">
            I have not receive any link
          </Typography.Link>
        </Flex>
      )}

      <Divider />
      <Flex justify="center">
        <Typography.Link href="/login">
          <LeftOutlined /> Back to login
        </Typography.Link>
      </Flex>
    </Form>
  );
};
